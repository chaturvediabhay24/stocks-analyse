import json
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.analysis import technical_analysis, fundamental_analysis, piotroski_fscore, canslim_analysis
from core.tickers import search_tickers
from core.stock_groups import get_groups, get_group
from core.group_analysis import magic_formula

app = FastAPI(title="Stock Analyzer")

TEMPLATE_DIR = Path(__file__).parent / "templates"


@app.get("/", response_class=HTMLResponse)
async def index():
    return (TEMPLATE_DIR / "groups.html").read_text()


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page():
    return (TEMPLATE_DIR / "index.html").read_text()


@app.get("/api/search")
async def search(q: str = "", market: str = "IN"):
    return search_tickers(q, market=market)


@app.get("/api/analyze/{symbol}")
async def analyze(symbol: str, market: str = "IN"):
    symbol = symbol.strip().upper()

    async def event_stream():
        # Stream technical analysis sections
        try:
            for section in technical_analysis(symbol, market=market):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "technical",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream fundamental analysis sections
        try:
            for section in fundamental_analysis(symbol, market=market):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "fundamental",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream Piotroski F-Score sections
        try:
            for section in piotroski_fscore(symbol, market=market):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "piotroski",
                        **section,
                    }),
                }
        except ValueError as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }
            return

        # Stream CAN SLIM analysis sections
        try:
            for section in canslim_analysis(symbol, market=market):
                yield {
                    "event": "section",
                    "data": json.dumps({
                        "category": "canslim",
                        **section,
                    }),
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
    """Keep /groups as an alias."""
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


@app.get("/api/groups/{group_id}/magic-formula")
async def group_magic_formula(group_id: str, market: str = "IN"):
    group = get_group(market, group_id)
    if not group:
        return {"error": f"Group '{group_id}' not found for market '{market}'"}

    async def event_stream():
        try:
            for event in magic_formula(group["symbols"], market=market):
                if event["type"] == "progress":
                    yield {
                        "event": "progress",
                        "data": json.dumps(event),
                    }
                elif event["type"] == "result":
                    yield {
                        "event": "result",
                        "data": json.dumps(event),
                    }
        except Exception as e:
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


@app.post("/api/magic-formula")
async def custom_magic_formula(request: Request):
    body = await request.json()
    symbols = body.get("symbols", [])
    market = body.get("market", "IN")

    if not symbols:
        return {"error": "No symbols provided"}

    async def event_stream():
        try:
            for event in magic_formula(symbols, market=market):
                if event["type"] == "progress":
                    yield {
                        "event": "progress",
                        "data": json.dumps(event),
                    }
                elif event["type"] == "result":
                    yield {
                        "event": "result",
                        "data": json.dumps(event),
                    }
        except Exception as e:
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
