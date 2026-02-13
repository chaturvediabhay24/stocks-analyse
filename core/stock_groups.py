"""Stock group definitions for index-level analysis."""

from __future__ import annotations

STOCK_GROUPS = {
    "IN": [
        {
            "id": "nifty50",
            "name": "Nifty 50",
            "symbols": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
                "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
                "LT", "HCLTECH", "AXISBANK", "ASIANPAINT", "MARUTI",
                "SUNPHARMA", "TITAN", "BAJFINANCE", "ULTRACEMCO", "WIPRO",
                "ONGC", "NTPC", "JSWSTEEL", "POWERGRID", "M&M",
                "TATASTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA", "HINDALCO",
                "GRASIM", "NESTLEIND", "TECHM", "BAJAJFINSV", "BAJAJ-AUTO",
                "INDUSINDBK", "HDFCLIFE", "SBILIFE", "BRITANNIA", "CIPLA",
                "APOLLOHOSP", "DIVISLAB", "DRREDDY", "EICHERMOT", "HEROMOTOCO",
                "TATACONSUM", "BPCL", "SHRIRAMFIN", "TATAMOTORS", "BEL",
            ],
        },
        {
            "id": "sensex",
            "name": "Sensex 30",
            "symbols": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
                "HINDUNILVR", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK",
                "LT", "HCLTECH", "AXISBANK", "ASIANPAINT", "MARUTI",
                "SUNPHARMA", "TITAN", "BAJFINANCE", "ULTRACEMCO", "WIPRO",
                "NTPC", "POWERGRID", "M&M", "TATASTEEL", "ADANIENT",
                "NESTLEIND", "TECHM", "BAJAJFINSV", "INDUSINDBK", "TATAMOTORS",
            ],
        },
    ],
    "US": [
        {
            "id": "nasdaq100",
            "name": "NASDAQ 100",
            "symbols": [
                "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL",
                "META", "TSLA", "AVGO", "COST", "NFLX",
                "AMD", "ADBE", "PEP", "CSCO", "TMUS",
                "INTC", "INTU", "CMCSA", "TXN", "AMGN",
                "QCOM", "HON", "AMAT", "ISRG", "BKNG",
                "SBUX", "VRTX", "LRCX", "ADI", "MDLZ",
                "GILD", "PANW", "REGN", "MU", "KLAC",
                "SNPS", "CDNS", "MELI", "PYPL", "CRWD",
                "CTAS", "MAR", "MRVL", "ORLY", "ABNB",
                "FTNT", "MNST", "DASH", "WDAY", "KDP",
            ],
        },
        {
            "id": "sp500_top50",
            "name": "S&P 500 (Top 50)",
            "symbols": [
                "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL",
                "META", "TSLA", "BRK-B", "UNH", "JNJ",
                "JPM", "V", "XOM", "PG", "MA",
                "HD", "CVX", "LLY", "MRK", "ABBV",
                "PEP", "KO", "COST", "AVGO", "WMT",
                "MCD", "CSCO", "ACN", "TMO", "ABT",
                "DHR", "LIN", "NEE", "PM", "TXN",
                "UPS", "RTX", "LOW", "ORCL", "AMGN",
                "COP", "UNP", "MS", "GS", "CAT",
                "BA", "DE", "SCHW", "ADP", "BLK",
            ],
        },
    ],
}


def get_groups(market: str = "IN") -> list[dict]:
    """Return available groups for a market (without full symbol lists)."""
    groups = STOCK_GROUPS.get(market.upper(), [])
    return [{"id": g["id"], "name": g["name"], "count": len(g["symbols"])} for g in groups]


def get_group(market: str, group_id: str) -> dict | None:
    """Return a specific group by market and id."""
    for g in STOCK_GROUPS.get(market.upper(), []):
        if g["id"] == group_id:
            return g
    return None
