"""Group-level stock analysis (Magic Formula, etc.)."""

import math

from core.data_fetcher import fetch_stock_info, fetch_stock_financials
from core.markets import get_market_config


def _safe_val(series, *labels):
    """Extract a finite numeric value from a pandas Series, trying multiple label variants."""
    for label in labels:
        if label in series.index:
            try:
                v = float(series[label])
                if math.isfinite(v):
                    return v
            except (TypeError, ValueError):
                pass
    return None


def _finite(v):
    """Return v if it's a finite number, else None."""
    if v is None:
        return None
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _compute_magic_formula_metrics(symbol: str, market: str = "IN"):
    """Compute Earnings Yield and ROIC for a single stock.

    Returns dict with metrics or None if insufficient data.
    """
    config = get_market_config(market)
    cur = config["currency"]

    try:
        ticker = fetch_stock_financials(symbol, market=market)
    except (ValueError, Exception):
        return None

    info = ticker.info
    financials = ticker.financials
    balance = ticker.balance_sheet

    if financials is None or financials.empty or balance is None or balance.empty:
        return None

    # Most recent annual data
    fin = financials.iloc[:, 0]
    bal = balance.iloc[:, 0]

    # --- EBIT ---
    ebit = _safe_val(fin, "EBIT", "Operating Income")
    if ebit is None:
        total_revenue = _safe_val(fin, "Total Revenue", "Operating Revenue")
        cost_of_revenue = _safe_val(fin, "Cost Of Revenue", "Cost Of Goods Sold")
        operating_expense = _safe_val(fin, "Operating Expense", "Total Operating Expenses",
                                      "Selling General And Administration")
        if total_revenue is not None and cost_of_revenue is not None:
            gross_profit = total_revenue - cost_of_revenue
            if operating_expense is not None:
                ebit = gross_profit - operating_expense
            else:
                # Fallback: use gross profit as rough proxy
                ebit = gross_profit

    if ebit is None:
        return None

    # --- Enterprise Value ---
    ev = _finite(info.get("enterpriseValue"))
    if not ev or ev <= 0:
        return None

    # --- Invested Capital (Net Working Capital + Net Fixed Assets) ---
    current_assets = _safe_val(bal, "Current Assets", "Total Current Assets")
    current_liabilities = _safe_val(bal, "Current Liabilities", "Total Current Liabilities")
    total_assets = _safe_val(bal, "Total Assets")

    if current_assets is None or current_liabilities is None or total_assets is None:
        return None

    net_working_capital = current_assets - current_liabilities
    net_fixed_assets = total_assets - current_assets
    invested_capital = net_working_capital + net_fixed_assets

    if invested_capital <= 0:
        return None

    # --- Metrics ---
    earnings_yield = ebit / ev
    roic = ebit / invested_capital

    # Extra info for display
    price = _finite(info.get("regularMarketPrice")) or _finite(info.get("currentPrice"))
    market_cap = _finite(info.get("marketCap"))
    pe = _finite(info.get("trailingPE"))
    name = info.get("shortName") or info.get("longName") or symbol

    # Format market cap
    if market_cap is not None:
        if abs(market_cap) >= 1e12:
            mc_str = f"{cur}{market_cap / 1e12:,.2f}T"
        elif abs(market_cap) >= 1e9:
            mc_str = f"{cur}{market_cap / 1e9:,.2f}B"
        elif abs(market_cap) >= 1e7:
            mc_str = f"{cur}{market_cap / 1e7:,.2f} Cr"
        else:
            mc_str = f"{cur}{market_cap:,.0f}"
    else:
        mc_str = "N/A"

    return {
        "symbol": symbol,
        "name": name,
        "earnings_yield": earnings_yield,
        "roic": roic,
        "price": price,
        "market_cap": mc_str,
        "pe": pe,
    }


def magic_formula(symbols: list[str], market: str = "IN"):
    """Run Magic Formula ranking on a list of stocks.

    Yields progress events and a final result event.
    Each yield is a dict:
        {"type": "progress", "current": N, "total": M, "symbol": "...", "status": "ok"|"skipped"}
        {"type": "result", "rankings": [...]}
    """
    total = len(symbols)
    stock_data = []

    for i, symbol in enumerate(symbols, 1):
        metrics = _compute_magic_formula_metrics(symbol, market=market)
        status = "ok" if metrics else "skipped"

        yield {
            "type": "progress",
            "current": i,
            "total": total,
            "symbol": symbol,
            "status": status,
        }

        if metrics:
            stock_data.append(metrics)

    if not stock_data:
        yield {"type": "result", "rankings": []}
        return

    # Rank by Earnings Yield (higher = better → lower rank number)
    stock_data.sort(key=lambda x: x["earnings_yield"], reverse=True)
    for rank, s in enumerate(stock_data, 1):
        s["ey_rank"] = rank

    # Rank by ROIC (higher = better → lower rank number)
    stock_data.sort(key=lambda x: x["roic"], reverse=True)
    for rank, s in enumerate(stock_data, 1):
        s["roic_rank"] = rank

    # Combined rank (lower = better)
    for s in stock_data:
        s["combined_rank"] = s["ey_rank"] + s["roic_rank"]

    # Sort by combined rank
    stock_data.sort(key=lambda x: x["combined_rank"])

    # Assign final rank
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

    yield {"type": "result", "rankings": rankings}
