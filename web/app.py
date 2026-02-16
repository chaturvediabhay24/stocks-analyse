from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.analysis import technical_analysis, fundamental_analysis, piotroski_fscore, canslim_analysis
from core.cache import _last_refresh_boundary
from core.data_fetcher import fetch_stock_data, fetch_stock_info, fetch_stock_financials
from core.db import save_snapshot, get_snapshot, list_snapshot_dates, ensure_indexes
from core.tickers import search_tickers
from core.stock_groups import get_groups, get_group
from core.group_analysis import _compute_magic_formula_metrics

@asynccontextmanager
async def lifespan(app):
    await ensure_indexes()
    yield


app = FastAPI(title="Stock Analyzer", lifespan=lifespan)

TEMPLATE_DIR = Path(__file__).parent / "templates"

MAGIC_FORMULA_BATCH_SIZE = 10


@app.get("/", response_class=HTMLResponse)
async def landing():
    return (TEMPLATE_DIR / "landing.html").read_text()


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page():
    return (TEMPLATE_DIR / "index.html").read_text()


@app.get("/api/search")
async def search(q: str = "", market: str = "IN"):
    return await asyncio.to_thread(search_tickers, q, market=market)


@app.get("/api/analyze/{symbol}")
async def analyze(symbol: str, market: str = "IN"):
    symbol = symbol.strip().upper()

    # Pre-fetch all data sources in parallel so generators hit cache
    results = await asyncio.gather(
        asyncio.to_thread(fetch_stock_data, symbol, "1y", market),
        asyncio.to_thread(fetch_stock_info, symbol, market),
        asyncio.to_thread(fetch_stock_financials, symbol, market),
        return_exceptions=True,
    )

    # If stock data fetch failed, no point continuing
    if isinstance(results[0], Exception):
        async def error_stream():
            yield {
                "event": "error",
                "data": json.dumps({"message": str(results[0])}),
            }
        return EventSourceResponse(error_stream())

    async def event_stream():
        analyses = [
            ("technical", technical_analysis),
            ("fundamental", fundamental_analysis),
            ("piotroski", piotroski_fscore),
            ("canslim", canslim_analysis),
        ]

        for category, analysis_fn in analyses:
            try:
                sections = await asyncio.to_thread(
                    lambda fn=analysis_fn: list(fn(symbol, market=market))
                )
                for section in sections:
                    yield {
                        "event": "section",
                        "data": json.dumps({"category": category, **section}),
                    }
            except ValueError as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": str(e)}),
                }
                return

        yield {
            "event": "done",
            "data": json.dumps({"status": "complete"}),
        }

    return EventSourceResponse(event_stream())


@app.get("/groups", response_class=HTMLResponse)
async def groups_page():
    return (TEMPLATE_DIR / "groups.html").read_text()


@app.get("/api/groups")
async def list_groups(market: str = "IN"):
    return get_groups(market)


@app.get("/api/groups/{group_id}/symbols")
async def group_symbols(group_id: str, market: str = "IN"):
    group = get_group(market, group_id)
    if not group:
        return {"error": f"Group '{group_id}' not found for market '{market}'"}
    return {"symbols": group["symbols"]}


async def _magic_formula_stream(symbols: list[str], market: str = "IN",
                                group_id: str | None = None):
    """Process magic formula with parallel batch fetching."""

    # Return cached snapshot from DB if one exists for this session
    # and the symbol list hasn't changed (e.g. user added/removed stocks)
    if group_id:
        session_date = _last_refresh_boundary(market).strftime("%Y-%m-%d")
        existing = await get_snapshot(group_id, market, session_date)
        if existing and existing.get("rankings") and sorted(existing.get("symbols", [])) == sorted(symbols):
            yield {
                "event": "result",
                "data": json.dumps({"type": "result", "rankings": existing["rankings"],
                                    "from_cache": True}),
            }
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"}),
            }
            return

    total = len(symbols)
    stock_data = []

    for batch_start in range(0, total, MAGIC_FORMULA_BATCH_SIZE):
        batch = symbols[batch_start:batch_start + MAGIC_FORMULA_BATCH_SIZE]

        # Fetch all stocks in this batch in parallel
        batch_results = await asyncio.gather(*[
            asyncio.to_thread(_compute_magic_formula_metrics, sym, market)
            for sym in batch
        ])

        for i, (sym, metrics) in enumerate(zip(batch, batch_results)):
            status = "ok" if metrics else "skipped"
            yield {
                "event": "progress",
                "data": json.dumps({
                    "type": "progress",
                    "current": batch_start + i + 1,
                    "total": total,
                    "symbol": sym,
                    "status": status,
                }),
            }
            if metrics:
                stock_data.append(metrics)

    # Rank and produce final result (same logic as magic_formula)
    if not stock_data:
        yield {
            "event": "result",
            "data": json.dumps({"type": "result", "rankings": []}),
        }
    else:
        stock_data.sort(key=lambda x: x["earnings_yield"], reverse=True)
        for rank, s in enumerate(stock_data, 1):
            s["ey_rank"] = rank

        stock_data.sort(key=lambda x: x["roic"], reverse=True)
        for rank, s in enumerate(stock_data, 1):
            s["roic_rank"] = rank

        for s in stock_data:
            s["combined_rank"] = s["ey_rank"] + s["roic_rank"]

        stock_data.sort(key=lambda x: x["combined_rank"])

        rankings = []
        for rank, s in enumerate(stock_data, 1):
            rankings.append({
                "rank": rank,
                "symbol": s["symbol"],
                "name": s["name"],
                "earnings_yield": round(s["earnings_yield"] * 100, 2),
                "roic": round(s["roic"] * 100, 2),
                "ey_rank": s["ey_rank"],
                "roic_rank": s["roic_rank"],
                "combined_score": s["combined_rank"],
                "price": round(s["price"], 2) if s["price"] else None,
                "market_cap": s["market_cap"],
                "pe": round(s["pe"], 2) if s["pe"] else None,
            })

        yield {
            "event": "result",
            "data": json.dumps({"type": "result", "rankings": rankings}),
        }

        # Auto-save snapshot to MongoDB
        if group_id:
            session_date = _last_refresh_boundary(market).strftime("%Y-%m-%d")
            await save_snapshot(group_id, market, session_date, symbols, rankings)

    yield {
        "event": "done",
        "data": json.dumps({"status": "complete"}),
    }


@app.get("/api/groups/{group_id}/magic-formula")
async def group_magic_formula(group_id: str, market: str = "IN"):
    group = get_group(market, group_id)
    if not group:
        return {"error": f"Group '{group_id}' not found for market '{market}'"}

    return EventSourceResponse(
        _magic_formula_stream(group["symbols"], market=market, group_id=group_id)
    )


@app.post("/api/magic-formula")
async def custom_magic_formula(request: Request):
    body = await request.json()
    symbols = body.get("symbols", [])
    market = body.get("market", "IN")
    group_id = body.get("group_id")

    if not symbols:
        return {"error": "No symbols provided"}

    return EventSourceResponse(
        _magic_formula_stream(symbols, market=market, group_id=group_id)
    )


@app.get("/api/groups/{group_id}/history")
async def group_history(group_id: str, market: str = "IN"):
    dates = await list_snapshot_dates(group_id, market)
    return {"dates": dates}


@app.get("/api/groups/{group_id}/snapshot")
async def group_snapshot(group_id: str, market: str = "IN", date: str = ""):
    if not date:
        return {"error": "date query parameter is required"}
    snapshot = await get_snapshot(group_id, market, date)
    if not snapshot:
        return {"error": "Snapshot not found"}
    return {
        "session_date": snapshot["session_date"],
        "rankings": snapshot["rankings"],
        "symbols": snapshot.get("symbols", []),
    }
