import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetch historical OHLCV data for an NSE stock.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE"). ".NS" is appended automatically.
        period: yfinance period string (e.g. "1y", "6mo", "3mo").

    Returns:
        DataFrame with Date index, Open, High, Low, Close, Volume columns.

    Raises:
        ValueError: If no data is found for the symbol.
    """
    ticker = yf.Ticker(f"{symbol}.NS")
    df = ticker.history(period=period)
    if df.empty:
        raise ValueError(f"No data found for {symbol}.NS. Check the ticker symbol.")
    return df


def fetch_stock_financials(symbol: str):
    """Return the yfinance Ticker object for accessing financial statements.

    Provides access to .financials, .quarterly_financials, .balance_sheet,
    .quarterly_balance_sheet, .cashflow, and .quarterly_cashflow DataFrames.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE").

    Returns:
        yfinance Ticker object.

    Raises:
        ValueError: If no data is found for the symbol.
    """
    ticker = yf.Ticker(f"{symbol}.NS")
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None:
        raise ValueError(f"No data found for {symbol}.NS. Check the ticker symbol.")
    return ticker


def fetch_stock_info(symbol: str) -> dict:
    """Fetch fundamental info dict for an NSE stock.

    Args:
        symbol: Stock ticker (e.g. "RELIANCE").

    Returns:
        Dict with all available info fields from yfinance.

    Raises:
        ValueError: If info cannot be retrieved.
    """
    ticker = yf.Ticker(f"{symbol}.NS")
    info = ticker.info
    if not info or info.get("regularMarketPrice") is None:
        raise ValueError(f"No info found for {symbol}.NS. Check the ticker symbol.")
    return info
