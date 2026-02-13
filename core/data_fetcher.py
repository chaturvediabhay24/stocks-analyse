import yfinance as yf
import pandas as pd

from core.markets import get_market_config
from core import cache


def fetch_stock_data(symbol: str, period: str = "1y", market: str = "IN") -> pd.DataFrame:
    """Fetch historical OHLCV data for a stock.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE", "AAPL").
        period: yfinance period string (e.g. "1y", "6mo", "3mo").
        market: Market code ("IN" for NSE, "US" for US stocks).

    Returns:
        DataFrame with Date index, Open, High, Low, Close, Volume columns.

    Raises:
        ValueError: If no data is found for the symbol.
    """
    cached = cache.get("stock_data", symbol, market, period=period)
    if cached is not None:
        return cached

    config = get_market_config(market)
    suffix = config["suffix"]
    ticker_symbol = f"{symbol}{suffix}"
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    if df.empty:
        raise ValueError(f"No data found for {ticker_symbol}. Check the ticker symbol.")

    cache.set("stock_data", symbol, market, df, period=period)
    return df


def fetch_stock_financials(symbol: str, market: str = "IN"):
    """Return the yfinance Ticker object for accessing financial statements.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE", "AAPL").
        market: Market code ("IN" for NSE, "US" for US stocks).

    Returns:
        yfinance Ticker object.

    Raises:
        ValueError: If no data is found for the symbol.
    """
    cached = cache.get("stock_financials", symbol, market)
    if cached is not None:
        return cached

    config = get_market_config(market)
    suffix = config["suffix"]
    ticker_symbol = f"{symbol}{suffix}"
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None:
        raise ValueError(f"No data found for {ticker_symbol}. Check the ticker symbol.")

    cache.set("stock_financials", symbol, market, ticker)
    return ticker


def fetch_stock_info(symbol: str, market: str = "IN") -> dict:
    """Fetch fundamental info dict for a stock.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE", "AAPL").
        market: Market code ("IN" for NSE, "US" for US stocks).

    Returns:
        Dict with all available info fields from yfinance.

    Raises:
        ValueError: If info cannot be retrieved.
    """
    cached = cache.get("stock_info", symbol, market)
    if cached is not None:
        return cached

    config = get_market_config(market)
    suffix = config["suffix"]
    ticker_symbol = f"{symbol}{suffix}"
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None:
        raise ValueError(f"No info found for {ticker_symbol}. Check the ticker symbol.")

    cache.set("stock_info", symbol, market, info)
    return info
