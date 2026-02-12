"""Pure analysis logic that yields results section-by-section.

Both the Telegram plugin and web frontend consume these generators.
Each generator yields dicts of the form:
    {"section": "Section Name", "rows": [{"label": ..., "value": ..., "signal": ...}, ...]}
where signal is one of: "bullish", "bearish", "neutral", "info", or None.
"""

import ta
from core.data_fetcher import fetch_stock_data, fetch_stock_info, fetch_stock_financials


def _fmt(value, prefix="", suffix="", decimals=2):
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) >= 1e7:
            return f"{prefix}{value / 1e7:,.{decimals}f} Cr{suffix}"
        return f"{prefix}{value:,.{decimals}f}{suffix}"
    return str(value)


def _pct(value):
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def technical_analysis(symbol: str):
    """Yield technical analysis sections one at a time."""
    df = fetch_stock_data(symbol)
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    latest_price = close.iloc[-1]
    prev_close = close.iloc[-2]
    price_change = latest_price - prev_close
    price_change_pct = (price_change / prev_close) * 100
    change_sign = "+" if price_change >= 0 else ""

    # Track signals for overall scoring
    bullish = 0
    bearish = 0

    # --- Price ---
    yield {
        "section": "Price",
        "rows": [
            {"label": "Current Price", "value": f"₹{latest_price:,.2f}", "signal": None},
            {"label": "Change", "value": f"{change_sign}{price_change:,.2f} ({change_sign}{price_change_pct:.2f}%)",
             "signal": "bullish" if price_change >= 0 else "bearish"},
        ],
    }

    # --- Moving Averages ---
    sma_20 = ta.trend.sma_indicator(close, window=20).iloc[-1]
    sma_50 = ta.trend.sma_indicator(close, window=50).iloc[-1]
    sma_200 = ta.trend.sma_indicator(close, window=200).iloc[-1]
    ema_12 = ta.trend.ema_indicator(close, window=12).iloc[-1]
    ema_26 = ta.trend.ema_indicator(close, window=26).iloc[-1]

    sma_50_prev = ta.trend.sma_indicator(close, window=50).iloc[-2]
    sma_200_prev = ta.trend.sma_indicator(close, window=200).iloc[-2]
    if sma_50_prev <= sma_200_prev and sma_50 > sma_200:
        cross_signal = "GOLDEN CROSS"
        cross_s = "bullish"
    elif sma_50_prev >= sma_200_prev and sma_50 < sma_200:
        cross_signal = "DEATH CROSS"
        cross_s = "bearish"
    elif sma_50 > sma_200:
        cross_signal = "SMA 50 > SMA 200"
        cross_s = "bullish"
    else:
        cross_signal = "SMA 50 < SMA 200"
        cross_s = "bearish"

    above_50 = latest_price > sma_50
    above_200 = latest_price > sma_200
    bullish += int(above_50) + int(above_200)
    bearish += int(not above_50) + int(not above_200)

    yield {
        "section": "Moving Averages",
        "rows": [
            {"label": "SMA 20", "value": f"₹{sma_20:,.2f}",
             "signal": "bullish" if latest_price > sma_20 else "bearish"},
            {"label": "SMA 50", "value": f"₹{sma_50:,.2f}",
             "signal": "bullish" if above_50 else "bearish"},
            {"label": "SMA 200", "value": f"₹{sma_200:,.2f}",
             "signal": "bullish" if above_200 else "bearish"},
            {"label": "EMA 12", "value": f"₹{ema_12:,.2f}", "signal": None},
            {"label": "EMA 26", "value": f"₹{ema_26:,.2f}", "signal": None},
            {"label": "Cross Signal", "value": cross_signal, "signal": cross_s},
        ],
    }

    # --- Momentum ---
    rsi = ta.momentum.rsi(close, window=14).iloc[-1]
    if rsi > 70:
        rsi_signal, rsi_s = "Overbought", "bearish"
    elif rsi < 30:
        rsi_signal, rsi_s = "Oversold", "bullish"
    else:
        rsi_signal, rsi_s = "Neutral", "neutral"

    if 40 < rsi < 70:
        bullish += 1
    elif rsi > 70:
        bearish += 1
    else:
        bearish += 1

    stoch_k = ta.momentum.stoch(high, low, close, window=14, smooth_window=3).iloc[-1]
    stoch_d = ta.momentum.stoch_signal(high, low, close, window=14, smooth_window=3).iloc[-1]
    if stoch_k > 80:
        stoch_sig, stoch_s = "Overbought", "bearish"
        bearish += 1
    elif stoch_k < 20:
        stoch_sig, stoch_s = "Oversold", "bullish"
        bearish += 1
    else:
        stoch_sig, stoch_s = "Neutral", "neutral"
        bullish += 1

    macd_line = ta.trend.macd(close).iloc[-1]
    macd_signal_line = ta.trend.macd_signal(close).iloc[-1]
    macd_hist = ta.trend.macd_diff(close).iloc[-1]
    macd_trend = "Bullish" if macd_hist > 0 else "Bearish"
    macd_s = "bullish" if macd_hist > 0 else "bearish"
    if macd_hist > 0:
        bullish += 1
    else:
        bearish += 1

    yield {
        "section": "Momentum",
        "rows": [
            {"label": "RSI (14)", "value": f"{rsi:.2f} ({rsi_signal})", "signal": rsi_s},
            {"label": "Stochastic %K", "value": f"{stoch_k:.2f} ({stoch_sig})", "signal": stoch_s},
            {"label": "Stochastic %D", "value": f"{stoch_d:.2f}", "signal": None},
            {"label": "MACD", "value": f"{macd_line:.2f}", "signal": None},
            {"label": "MACD Signal", "value": f"{macd_signal_line:.2f}", "signal": None},
            {"label": "MACD Histogram", "value": f"{macd_hist:.2f} ({macd_trend})", "signal": macd_s},
        ],
    }

    # --- Trend Strength ---
    adx = ta.trend.adx(high, low, close, window=14).iloc[-1]
    adx_signal = "Strong Trend" if adx > 25 else "Weak/No Trend"

    yield {
        "section": "Trend Strength",
        "rows": [
            {"label": "ADX (14)", "value": f"{adx:.2f} ({adx_signal})",
             "signal": "bullish" if adx > 25 else "neutral"},
        ],
    }

    # --- Volatility ---
    atr = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1]
    atr_pct = (atr / latest_price) * 100

    bb_high = ta.volatility.bollinger_hband(close).iloc[-1]
    bb_low = ta.volatility.bollinger_lband(close).iloc[-1]
    bb_mid = ta.volatility.bollinger_mavg(close).iloc[-1]
    bb_width = ((bb_high - bb_low) / bb_mid) * 100

    if latest_price >= bb_high:
        bb_sig = "At/Above Upper Band"
        bb_s = "bearish"
    elif latest_price <= bb_low:
        bb_sig = "At/Below Lower Band"
        bb_s = "bullish"
    else:
        bb_sig = "Within Bands"
        bb_s = "neutral"

    if latest_price > bb_mid:
        bullish += 1
    else:
        bearish += 1

    yield {
        "section": "Volatility",
        "rows": [
            {"label": "ATR (14)", "value": f"₹{atr:,.2f} ({atr_pct:.2f}%)", "signal": None},
            {"label": "Bollinger Upper", "value": f"₹{bb_high:,.2f}", "signal": None},
            {"label": "Bollinger Mid", "value": f"₹{bb_mid:,.2f}", "signal": None},
            {"label": "Bollinger Lower", "value": f"₹{bb_low:,.2f}", "signal": None},
            {"label": "BB Width", "value": f"{bb_width:.2f}%", "signal": None},
            {"label": "BB Signal", "value": bb_sig, "signal": bb_s},
        ],
    }

    # --- Volume ---
    avg_volume_20 = volume.rolling(window=20).mean().iloc[-1]
    current_volume = volume.iloc[-1]
    vol_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0

    obv = ta.volume.on_balance_volume(close, volume)
    obv_current = obv.iloc[-1]
    obv_5_ago = obv.iloc[-5]
    obv_trend = "Rising" if obv_current > obv_5_ago else "Falling"
    obv_s = "bullish" if obv_current > obv_5_ago else "bearish"

    if obv_current > obv_5_ago:
        bullish += 1
    else:
        bearish += 1

    yield {
        "section": "Volume",
        "rows": [
            {"label": "Current Volume", "value": f"{current_volume:,.0f}", "signal": None},
            {"label": "20-Day Avg Volume", "value": f"{avg_volume_20:,.0f}", "signal": None},
            {"label": "Volume Ratio", "value": f"{vol_ratio:.2f}x",
             "signal": "bullish" if vol_ratio > 1.2 else ("bearish" if vol_ratio < 0.5 else "neutral")},
            {"label": "OBV Trend (5d)", "value": obv_trend, "signal": obv_s},
        ],
    }

    # --- Support / Resistance ---
    recent_high = high.tail(20).max()
    recent_low = low.tail(20).min()

    prev_high = high.iloc[-2]
    prev_low = low.iloc[-2]
    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * pivot - prev_low
    s1 = 2 * pivot - prev_high
    r2 = pivot + (prev_high - prev_low)
    s2 = pivot - (prev_high - prev_low)

    yield {
        "section": "Support / Resistance",
        "rows": [
            {"label": "20-Day Support", "value": f"₹{recent_low:,.2f}", "signal": None},
            {"label": "20-Day Resistance", "value": f"₹{recent_high:,.2f}", "signal": None},
            {"label": "Pivot Point", "value": f"₹{pivot:,.2f}", "signal": None},
            {"label": "R1 / R2", "value": f"₹{r1:,.2f} / ₹{r2:,.2f}", "signal": None},
            {"label": "S1 / S2", "value": f"₹{s1:,.2f} / ₹{s2:,.2f}", "signal": None},
        ],
    }

    # --- Fibonacci ---
    week52_high = high.max()
    week52_low = low.min()
    fib_diff = week52_high - week52_low
    fib_236 = week52_high - fib_diff * 0.236
    fib_382 = week52_high - fib_diff * 0.382
    fib_500 = week52_high - fib_diff * 0.500
    fib_618 = week52_high - fib_diff * 0.618

    yield {
        "section": "Fibonacci Levels (52-wk)",
        "rows": [
            {"label": "23.6%", "value": f"₹{fib_236:,.2f}", "signal": None},
            {"label": "38.2%", "value": f"₹{fib_382:,.2f}", "signal": None},
            {"label": "50.0%", "value": f"₹{fib_500:,.2f}", "signal": None},
            {"label": "61.8%", "value": f"₹{fib_618:,.2f}", "signal": None},
        ],
    }

    # --- Overall ---
    total = 7
    if bullish >= 5:
        overall = "BULLISH"
        overall_s = "bullish"
    elif bearish >= 5:
        overall = "BEARISH"
        overall_s = "bearish"
    else:
        overall = "NEUTRAL"
        overall_s = "neutral"

    yield {
        "section": "Overall Signal",
        "is_summary": True,
        "rows": [
            {"label": "Signal", "value": f"{overall} ({bullish}/{total})", "signal": overall_s},
        ],
    }


def fundamental_analysis(symbol: str):
    """Yield fundamental analysis sections one at a time."""
    info = fetch_stock_info(symbol)

    def get(key, default=None):
        return info.get(key, default)

    current_price = get("regularMarketPrice") or get("currentPrice")
    sector = get("sector", "N/A")
    industry = get("industry", "N/A")

    # --- Company Info ---
    yield {
        "section": "Company Info",
        "rows": [
            {"label": "Sector", "value": sector, "signal": None},
            {"label": "Industry", "value": industry, "signal": None},
            {"label": "Current Price", "value": _fmt(current_price, prefix="₹"), "signal": None},
        ],
    }

    # --- Valuation ---
    market_cap = get("marketCap")
    enterprise_value = get("enterpriseValue")
    pe_trailing = get("trailingPE")
    pe_forward = get("forwardPE")
    pb = get("priceToBook")
    ps = get("priceToSalesTrailing12Months")
    ev_ebitda = get("enterpriseToEbitda")
    ev_revenue = get("enterpriseToRevenue")
    book_value = get("bookValue")

    pe_s = None
    if pe_trailing is not None:
        pe_s = "bullish" if pe_trailing < 20 else ("bearish" if pe_trailing > 35 else "neutral")

    yield {
        "section": "Valuation",
        "rows": [
            {"label": "Market Cap", "value": _fmt(market_cap, prefix="₹"), "signal": None},
            {"label": "Enterprise Value", "value": _fmt(enterprise_value, prefix="₹"), "signal": None},
            {"label": "PE Ratio (TTM)", "value": _fmt(pe_trailing), "signal": pe_s},
            {"label": "PE Ratio (Forward)", "value": _fmt(pe_forward),
             "signal": "bullish" if pe_forward and pe_trailing and pe_forward < pe_trailing else None},
            {"label": "PB Ratio", "value": _fmt(pb), "signal": None},
            {"label": "P/S Ratio", "value": _fmt(ps), "signal": None},
            {"label": "EV/EBITDA", "value": _fmt(ev_ebitda), "signal": None},
            {"label": "EV/Revenue", "value": _fmt(ev_revenue), "signal": None},
            {"label": "Book Value", "value": _fmt(book_value, prefix="₹"), "signal": None},
        ],
    }

    # --- Earnings & Growth ---
    eps = get("trailingEps")
    forward_eps = get("forwardEps")
    revenue = get("totalRevenue")
    ebitda = get("ebitda")
    revenue_growth = get("revenueGrowth")
    earnings_growth = get("earningsGrowth")

    yield {
        "section": "Earnings & Growth",
        "rows": [
            {"label": "EPS (TTM)", "value": _fmt(eps, prefix="₹"), "signal": None},
            {"label": "EPS (Forward)", "value": _fmt(forward_eps, prefix="₹"),
             "signal": "bullish" if forward_eps and eps and forward_eps > eps else None},
            {"label": "Revenue", "value": _fmt(revenue, prefix="₹"), "signal": None},
            {"label": "EBITDA", "value": _fmt(ebitda, prefix="₹"), "signal": None},
            {"label": "Revenue Growth", "value": _pct(revenue_growth),
             "signal": "bullish" if revenue_growth and revenue_growth > 0.05 else (
                 "bearish" if revenue_growth and revenue_growth < 0 else "neutral")},
            {"label": "Earnings Growth", "value": _pct(earnings_growth),
             "signal": "bullish" if earnings_growth and earnings_growth > 0.05 else (
                 "bearish" if earnings_growth and earnings_growth < 0 else "neutral")},
        ],
    }

    # --- Profitability ---
    gross_margin = get("grossMargins")
    operating_margin = get("operatingMargins")
    profit_margin = get("profitMargins")
    roe = get("returnOnEquity")
    roa = get("returnOnAssets")

    yield {
        "section": "Profitability",
        "rows": [
            {"label": "Gross Margin", "value": _pct(gross_margin), "signal": None},
            {"label": "Operating Margin", "value": _pct(operating_margin),
             "signal": "bullish" if operating_margin and operating_margin > 0.15 else None},
            {"label": "Profit Margin", "value": _pct(profit_margin),
             "signal": "bullish" if profit_margin and profit_margin > 0.10 else (
                 "bearish" if profit_margin and profit_margin < 0.05 else "neutral")},
            {"label": "ROE", "value": _pct(roe),
             "signal": "bullish" if roe and roe > 0.15 else ("bearish" if roe and roe < 0.05 else "neutral")},
            {"label": "ROA", "value": _pct(roa),
             "signal": "bullish" if roa and roa > 0.05 else None},
        ],
    }

    # --- Cash Flow ---
    operating_cashflow = get("operatingCashflow")
    free_cashflow = get("freeCashflow")

    yield {
        "section": "Cash Flow",
        "rows": [
            {"label": "Operating Cash Flow", "value": _fmt(operating_cashflow, prefix="₹"), "signal": None},
            {"label": "Free Cash Flow", "value": _fmt(free_cashflow, prefix="₹"),
             "signal": "bullish" if free_cashflow and free_cashflow > 0 else (
                 "bearish" if free_cashflow and free_cashflow < 0 else None)},
        ],
    }

    # --- Financial Health ---
    debt_to_equity = get("debtToEquity")
    total_debt = get("totalDebt")
    total_cash = get("totalCash")
    current_ratio = get("currentRatio")
    quick_ratio = get("quickRatio")

    yield {
        "section": "Financial Health",
        "rows": [
            {"label": "Debt/Equity", "value": _fmt(debt_to_equity),
             "signal": "bullish" if debt_to_equity is not None and debt_to_equity < 50 else (
                 "bearish" if debt_to_equity is not None and debt_to_equity > 150 else "neutral")},
            {"label": "Total Debt", "value": _fmt(total_debt, prefix="₹"), "signal": None},
            {"label": "Total Cash", "value": _fmt(total_cash, prefix="₹"), "signal": None},
            {"label": "Current Ratio", "value": _fmt(current_ratio),
             "signal": "bullish" if current_ratio and current_ratio > 1.5 else (
                 "bearish" if current_ratio and current_ratio < 1 else "neutral")},
            {"label": "Quick Ratio", "value": _fmt(quick_ratio), "signal": None},
        ],
    }

    # --- Dividends ---
    dividend_yield = get("dividendYield")
    dividend_rate = get("dividendRate")
    payout_ratio = get("payoutRatio")

    if dividend_rate and current_price:
        div_yield_str = f"{(dividend_rate / current_price) * 100:.2f}%"
    elif dividend_yield is not None:
        div_yield_str = f"{dividend_yield:.2f}%"
    else:
        div_yield_str = "N/A"

    yield {
        "section": "Dividends",
        "rows": [
            {"label": "Dividend Yield", "value": div_yield_str, "signal": None},
            {"label": "Dividend Rate", "value": _fmt(dividend_rate, prefix="₹"), "signal": None},
            {"label": "Payout Ratio", "value": _pct(payout_ratio), "signal": None},
        ],
    }

    # --- Risk & Range ---
    beta = get("beta")
    fifty_two_high = get("fiftyTwoWeekHigh")
    fifty_two_low = get("fiftyTwoWeekLow")

    if fifty_two_high and fifty_two_low and current_price:
        range_position = ((current_price - fifty_two_low) / (fifty_two_high - fifty_two_low)) * 100
        range_str = f"{range_position:.1f}% from low"
    else:
        range_str = "N/A"

    yield {
        "section": "Risk & Range",
        "rows": [
            {"label": "Beta", "value": _fmt(beta), "signal": None},
            {"label": "52-Week High", "value": _fmt(fifty_two_high, prefix="₹"), "signal": None},
            {"label": "52-Week Low", "value": _fmt(fifty_two_low, prefix="₹"), "signal": None},
            {"label": "52-Week Position", "value": range_str, "signal": None},
        ],
    }

    # --- Overall ---
    score = 0
    max_score = 0

    def check(condition):
        nonlocal score, max_score
        max_score += 1
        if condition:
            score += 1

    check(pe_trailing is not None and pe_trailing < 25)
    check(pe_forward is not None and pe_trailing is not None and pe_forward < pe_trailing)
    check(roe is not None and roe > 0.15)
    check(roa is not None and roa > 0.05)
    check(debt_to_equity is not None and debt_to_equity < 100)
    check(revenue_growth is not None and revenue_growth > 0.05)
    check(earnings_growth is not None and earnings_growth > 0.05)
    check(profit_margin is not None and profit_margin > 0.10)
    check(operating_margin is not None and operating_margin > 0.10)
    check(free_cashflow is not None and free_cashflow > 0)

    pct = (score / max_score * 100) if max_score > 0 else 0
    if pct >= 70:
        rating, rating_s = "STRONG", "bullish"
    elif pct >= 40:
        rating, rating_s = "MODERATE", "neutral"
    else:
        rating, rating_s = "WEAK", "bearish"

    yield {
        "section": "Overall Rating",
        "is_summary": True,
        "rows": [
            {"label": "Rating", "value": f"{rating} ({score}/{max_score})", "signal": rating_s},
        ],
    }


def _safe_get_row(df, label):
    """Try multiple common row-label variants to find a value in a financial statement DataFrame."""
    variants = {
        "Net Income": ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"],
        "Total Assets": ["Total Assets"],
        "Total Revenue": ["Total Revenue", "Operating Revenue"],
        "Cost Of Revenue": ["Cost Of Revenue", "Cost Of Goods Sold"],
        "Gross Profit": ["Gross Profit"],
        "Operating Cash Flow": ["Operating Cash Flow", "Total Cash From Operating Activities", "Cash Flow From Continuing Operating Activities"],
        "Long Term Debt": ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"],
        "Current Assets": ["Current Assets", "Total Current Assets"],
        "Current Liabilities": ["Current Liabilities", "Total Current Liabilities"],
        "Ordinary Shares Number": ["Ordinary Shares Number", "Share Issued"],
    }
    keys = variants.get(label, [label])
    for key in keys:
        if key in df.index:
            return df.loc[key]
    return None


def piotroski_fscore(symbol: str):
    """Yield Piotroski F-Score analysis sections one at a time."""
    ticker = fetch_stock_financials(symbol)
    info = ticker.info

    financials = ticker.financials  # annual income statement
    balance = ticker.balance_sheet  # annual balance sheet
    cashflow = ticker.cashflow  # annual cash flow

    if financials.empty or balance.empty or cashflow.empty:
        yield {
            "section": "Piotroski F-Score",
            "is_summary": True,
            "rows": [{"label": "Error", "value": "Insufficient financial data available", "signal": "bearish"}],
        }
        return

    # We need at least 2 years of data for YoY comparisons
    # Columns are dates, most recent first
    has_prior = financials.shape[1] >= 2 and balance.shape[1] >= 2

    # Current year (most recent annual column)
    curr_fin = financials.iloc[:, 0]
    curr_bal = balance.iloc[:, 0]
    curr_cf = cashflow.iloc[:, 0]

    # Prior year
    if has_prior:
        prev_fin = financials.iloc[:, 1]
        prev_bal = balance.iloc[:, 1]

    # Helper to safely get a value
    def val(series, label):
        row = _safe_get_row(series.to_frame().T if hasattr(series, 'to_frame') else series, label)
        if row is not None:
            v = row.iloc[0] if hasattr(row, 'iloc') else row
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        # Direct index access fallback
        variants_map = {
            "Net Income": ["Net Income", "Net Income Common Stockholders"],
            "Total Assets": ["Total Assets"],
            "Total Revenue": ["Total Revenue", "Operating Revenue"],
            "Cost Of Revenue": ["Cost Of Revenue"],
            "Gross Profit": ["Gross Profit"],
            "Operating Cash Flow": ["Operating Cash Flow", "Total Cash From Operating Activities", "Cash Flow From Continuing Operating Activities"],
            "Long Term Debt": ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"],
            "Current Assets": ["Current Assets"],
            "Current Liabilities": ["Current Liabilities"],
            "Ordinary Shares Number": ["Ordinary Shares Number", "Share Issued"],
        }
        for key in variants_map.get(label, [label]):
            if key in series.index:
                try:
                    return float(series[key])
                except (TypeError, ValueError):
                    pass
        return None

    score = 0

    # --- Profitability (4 points) ---
    net_income = val(curr_fin, "Net Income")
    total_assets = val(curr_bal, "Total Assets")
    prev_total_assets = val(prev_bal, "Total Assets") if has_prior else None
    ocf = val(curr_cf, "Operating Cash Flow")

    # 1. Net Income > 0
    ni_positive = net_income is not None and net_income > 0
    if ni_positive:
        score += 1

    # 2. ROA > 0 (net income / total assets)
    roa = None
    if net_income is not None and total_assets and total_assets != 0:
        roa = net_income / total_assets
    roa_positive = roa is not None and roa > 0
    if roa_positive:
        score += 1

    # 3. Operating Cash Flow > 0
    ocf_positive = ocf is not None and ocf > 0
    if ocf_positive:
        score += 1

    # 4. Quality of Earnings: OCF > Net Income
    quality = ocf is not None and net_income is not None and ocf > net_income
    if quality:
        score += 1

    yield {
        "section": "Profitability (4 pts)",
        "rows": [
            {"label": "Net Income > 0", "value": _fmt(net_income, prefix="₹"),
             "signal": "bullish" if ni_positive else "bearish"},
            {"label": "ROA > 0", "value": f"{roa * 100:.2f}%" if roa is not None else "N/A",
             "signal": "bullish" if roa_positive else "bearish"},
            {"label": "Operating CF > 0", "value": _fmt(ocf, prefix="₹"),
             "signal": "bullish" if ocf_positive else "bearish"},
            {"label": "CF > Net Income (Quality)", "value": "Yes" if quality else "No",
             "signal": "bullish" if quality else "bearish"},
        ],
    }

    # --- Leverage, Liquidity & Source of Funds (3 points) ---
    curr_lt_debt = val(curr_bal, "Long Term Debt")
    prev_lt_debt = val(prev_bal, "Long Term Debt") if has_prior else None

    curr_current_assets = val(curr_bal, "Current Assets")
    curr_current_liab = val(curr_bal, "Current Liabilities")
    prev_current_assets = val(prev_bal, "Current Assets") if has_prior else None
    prev_current_liab = val(prev_bal, "Current Liabilities") if has_prior else None

    curr_shares = info.get("sharesOutstanding")
    # We can't easily get prior shares from yfinance info, so use balance sheet
    prev_shares_val = val(prev_bal, "Ordinary Shares Number") if has_prior else None
    curr_shares_val = val(curr_bal, "Ordinary Shares Number")

    # 5. Lower long-term debt ratio YoY
    if curr_lt_debt is not None and prev_lt_debt is not None and total_assets and prev_total_assets:
        curr_debt_ratio = curr_lt_debt / total_assets
        prev_debt_ratio = prev_lt_debt / prev_total_assets
        lower_debt = curr_debt_ratio <= prev_debt_ratio
        debt_str = f"{curr_debt_ratio:.2%} vs {prev_debt_ratio:.2%}"
    elif curr_lt_debt is not None and (curr_lt_debt == 0 or prev_lt_debt is None):
        lower_debt = True
        debt_str = "No long-term debt"
    else:
        lower_debt = False
        debt_str = "N/A"
    if lower_debt:
        score += 1

    # 6. Higher current ratio YoY
    curr_ratio = curr_current_assets / curr_current_liab if curr_current_assets and curr_current_liab and curr_current_liab != 0 else None
    prev_ratio = prev_current_assets / prev_current_liab if prev_current_assets and prev_current_liab and prev_current_liab != 0 else None
    if curr_ratio is not None and prev_ratio is not None:
        higher_cr = curr_ratio > prev_ratio
        cr_str = f"{curr_ratio:.2f} vs {prev_ratio:.2f}"
    elif curr_ratio is not None:
        higher_cr = curr_ratio > 1
        cr_str = f"{curr_ratio:.2f}"
    else:
        higher_cr = False
        cr_str = "N/A"
    if higher_cr:
        score += 1

    # 7. No new shares issued
    if curr_shares_val is not None and prev_shares_val is not None:
        no_dilution = curr_shares_val <= prev_shares_val
        shares_str = f"{curr_shares_val:,.0f} vs {prev_shares_val:,.0f}"
    elif curr_shares is not None:
        no_dilution = True  # assume no dilution if we can't compare
        shares_str = f"{curr_shares:,.0f} (prior N/A)"
    else:
        no_dilution = True
        shares_str = "N/A"
    if no_dilution:
        score += 1

    yield {
        "section": "Leverage & Liquidity (3 pts)",
        "rows": [
            {"label": "Lower Debt Ratio YoY", "value": debt_str,
             "signal": "bullish" if lower_debt else "bearish"},
            {"label": "Higher Current Ratio YoY", "value": cr_str,
             "signal": "bullish" if higher_cr else "bearish"},
            {"label": "No New Shares Issued", "value": shares_str,
             "signal": "bullish" if no_dilution else "bearish"},
        ],
    }

    # --- Operating Efficiency (2 points) ---
    curr_revenue = val(curr_fin, "Total Revenue")
    prev_revenue = val(prev_fin, "Total Revenue") if has_prior else None
    curr_gross = val(curr_fin, "Gross Profit")
    prev_gross = val(prev_fin, "Gross Profit") if has_prior else None

    # 8. Higher gross margin YoY
    curr_gm = curr_gross / curr_revenue if curr_gross is not None and curr_revenue and curr_revenue != 0 else None
    prev_gm = prev_gross / prev_revenue if prev_gross is not None and prev_revenue and prev_revenue != 0 else None
    if curr_gm is not None and prev_gm is not None:
        higher_gm = curr_gm > prev_gm
        gm_str = f"{curr_gm:.2%} vs {prev_gm:.2%}"
    elif curr_gm is not None:
        higher_gm = curr_gm > 0.2
        gm_str = f"{curr_gm:.2%}"
    else:
        higher_gm = False
        gm_str = "N/A"
    if higher_gm:
        score += 1

    # 9. Higher asset turnover YoY
    curr_at = curr_revenue / total_assets if curr_revenue and total_assets and total_assets != 0 else None
    prev_at = prev_revenue / prev_total_assets if prev_revenue and prev_total_assets and prev_total_assets != 0 else None
    if curr_at is not None and prev_at is not None:
        higher_at = curr_at > prev_at
        at_str = f"{curr_at:.2f} vs {prev_at:.2f}"
    elif curr_at is not None:
        higher_at = True
        at_str = f"{curr_at:.2f}"
    else:
        higher_at = False
        at_str = "N/A"
    if higher_at:
        score += 1

    yield {
        "section": "Operating Efficiency (2 pts)",
        "rows": [
            {"label": "Higher Gross Margin YoY", "value": gm_str,
             "signal": "bullish" if higher_gm else "bearish"},
            {"label": "Higher Asset Turnover YoY", "value": at_str,
             "signal": "bullish" if higher_at else "bearish"},
        ],
    }

    # --- Overall F-Score ---
    if score >= 7:
        rating, rating_s = "STRONG", "bullish"
    elif score >= 4:
        rating, rating_s = "MODERATE", "neutral"
    else:
        rating, rating_s = "WEAK", "bearish"

    yield {
        "section": "Piotroski F-Score",
        "is_summary": True,
        "rows": [
            {"label": "F-Score", "value": f"{rating} ({score}/9)", "signal": rating_s},
        ],
    }


def canslim_analysis(symbol: str):
    """Yield CAN SLIM analysis sections one at a time."""
    ticker = fetch_stock_financials(symbol)
    info = ticker.info
    df = fetch_stock_data(symbol)

    close = df["Close"]
    high = df["High"]
    volume = df["Volume"]
    latest_price = close.iloc[-1]

    quarterly_fin = ticker.quarterly_financials
    annual_fin = ticker.financials

    # --- C: Current Quarterly Earnings ---
    c_score = False
    c_rows = []
    if not quarterly_fin.empty and quarterly_fin.shape[1] >= 2:
        q_ni_curr = None
        q_ni_prev = None
        for label in ["Net Income", "Net Income Common Stockholders", "Net Income From Continuing Operations"]:
            if label in quarterly_fin.index:
                q_ni_curr = quarterly_fin.iloc[:, 0].get(label)
                # YoY comparison: compare with same quarter last year (4 quarters ago) if available, else prior quarter
                if quarterly_fin.shape[1] >= 5:
                    q_ni_prev = quarterly_fin.iloc[:, 4].get(label)
                else:
                    q_ni_prev = quarterly_fin.iloc[:, 1].get(label)
                break

        if q_ni_curr is not None and q_ni_prev is not None:
            try:
                q_ni_curr, q_ni_prev = float(q_ni_curr), float(q_ni_prev)
                if q_ni_prev > 0:
                    eps_growth = (q_ni_curr - q_ni_prev) / q_ni_prev
                    c_score = eps_growth > 0.25
                    c_rows.append({"label": "Quarterly EPS Growth", "value": f"{eps_growth:.1%}",
                                   "signal": "bullish" if c_score else ("neutral" if eps_growth > 0 else "bearish")})
                else:
                    c_score = q_ni_curr > 0
                    c_rows.append({"label": "Quarterly EPS", "value": "Turnaround" if c_score else "Negative",
                                   "signal": "bullish" if c_score else "bearish"})
            except (TypeError, ValueError):
                c_rows.append({"label": "Quarterly EPS Growth", "value": "N/A", "signal": None})
        else:
            c_rows.append({"label": "Quarterly EPS Growth", "value": "N/A", "signal": None})
    else:
        c_rows.append({"label": "Quarterly EPS Growth", "value": "Insufficient data", "signal": None})

    c_rows.append({"label": "C Score", "value": "PASS" if c_score else "FAIL",
                   "signal": "bullish" if c_score else "bearish"})
    yield {"section": "C — Current Earnings", "rows": c_rows}

    # --- A: Annual Earnings Growth ---
    a_score = False
    a_rows = []
    if not annual_fin.empty and annual_fin.shape[1] >= 2:
        ann_ni = []
        for col_idx in range(min(annual_fin.shape[1], 5)):
            for label in ["Net Income", "Net Income Common Stockholders"]:
                if label in annual_fin.index:
                    try:
                        ann_ni.append(float(annual_fin.iloc[:, col_idx][label]))
                    except (TypeError, ValueError):
                        pass
                    break

        if len(ann_ni) >= 2:
            # Check if earnings have been growing consistently
            growing = all(ann_ni[i] > ann_ni[i + 1] for i in range(len(ann_ni) - 1))
            if ann_ni[-1] > 0:
                total_growth = (ann_ni[0] - ann_ni[-1]) / ann_ni[-1]
                cagr = (ann_ni[0] / ann_ni[-1]) ** (1 / len(ann_ni)) - 1 if ann_ni[-1] > 0 else 0
                a_score = cagr > 0.15 or growing
                a_rows.append({"label": f"Earnings CAGR ({len(ann_ni)}yr)", "value": f"{cagr:.1%}",
                               "signal": "bullish" if a_score else "neutral"})
            else:
                a_score = ann_ni[0] > 0
                a_rows.append({"label": "Annual Earnings Trend", "value": "Improving" if a_score else "Weak",
                               "signal": "bullish" if a_score else "bearish"})
            a_rows.append({"label": "Consistent Growth", "value": "Yes" if growing else "No",
                           "signal": "bullish" if growing else "neutral"})
        else:
            a_rows.append({"label": "Annual Earnings", "value": "Insufficient data", "signal": None})
    else:
        a_rows.append({"label": "Annual Earnings", "value": "Insufficient data", "signal": None})

    a_rows.append({"label": "A Score", "value": "PASS" if a_score else "FAIL",
                   "signal": "bullish" if a_score else "bearish"})
    yield {"section": "A — Annual Earnings", "rows": a_rows}

    # --- N: New Highs ---
    week52_high = high.max()
    pct_from_high = ((latest_price - week52_high) / week52_high) * 100
    n_score = pct_from_high >= -10  # within 10% of 52-week high

    yield {
        "section": "N — New Highs",
        "rows": [
            {"label": "52-Week High", "value": f"₹{week52_high:,.2f}", "signal": None},
            {"label": "Current Price", "value": f"₹{latest_price:,.2f}", "signal": None},
            {"label": "Distance from High", "value": f"{pct_from_high:.1f}%",
             "signal": "bullish" if n_score else "bearish"},
            {"label": "N Score", "value": "PASS" if n_score else "FAIL",
             "signal": "bullish" if n_score else "bearish"},
        ],
    }

    # --- S: Supply & Demand ---
    shares_outstanding = info.get("sharesOutstanding")
    avg_vol_20 = volume.rolling(window=20).mean().iloc[-1]
    current_vol = volume.iloc[-1]
    vol_ratio = current_vol / avg_vol_20 if avg_vol_20 > 0 else 0

    # Prefer stocks with reasonable float, and increasing volume on up days
    price_up = close.iloc[-1] > close.iloc[-2]
    s_score = vol_ratio > 1.0 and price_up  # above-average volume on an up day

    s_rows = []
    if shares_outstanding:
        s_rows.append({"label": "Shares Outstanding", "value": _fmt(shares_outstanding), "signal": None})
    s_rows.extend([
        {"label": "Avg Volume (20d)", "value": f"{avg_vol_20:,.0f}", "signal": None},
        {"label": "Volume Ratio", "value": f"{vol_ratio:.2f}x",
         "signal": "bullish" if vol_ratio > 1.2 else ("bearish" if vol_ratio < 0.8 else "neutral")},
        {"label": "S Score", "value": "PASS" if s_score else "FAIL",
         "signal": "bullish" if s_score else "bearish"},
    ])
    yield {"section": "S — Supply & Demand", "rows": s_rows}

    # --- L: Leader or Laggard ---
    rsi = ta.momentum.rsi(close, window=14).iloc[-1]
    week52_low = close.min()
    range_position = ((latest_price - week52_low) / (week52_high - week52_low) * 100) if week52_high != week52_low else 50
    l_score = rsi >= 50 and range_position >= 60  # relative strength

    yield {
        "section": "L — Leader or Laggard",
        "rows": [
            {"label": "RSI (14)", "value": f"{rsi:.1f}", "signal": "bullish" if rsi >= 50 else "bearish"},
            {"label": "52-Week Range Position", "value": f"{range_position:.1f}%",
             "signal": "bullish" if range_position >= 60 else "bearish"},
            {"label": "L Score", "value": "PASS" if l_score else "FAIL",
             "signal": "bullish" if l_score else "bearish"},
        ],
    }

    # --- I: Institutional Ownership ---
    inst_pct = info.get("heldPercentInstitutions")
    i_score = inst_pct is not None and inst_pct > 0.10  # at least 10% institutional ownership

    yield {
        "section": "I — Institutional Sponsorship",
        "rows": [
            {"label": "Institutional Ownership", "value": f"{inst_pct:.1%}" if inst_pct is not None else "N/A",
             "signal": "bullish" if i_score else "neutral"},
            {"label": "I Score", "value": "PASS" if i_score else "FAIL",
             "signal": "bullish" if i_score else "bearish"},
        ],
    }

    # --- M: Market Direction ---
    # Use Nifty 50 (^NSEI) as market proxy
    import yfinance as yf
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_df = nifty.history(period="6mo")
        if not nifty_df.empty:
            nifty_close = nifty_df["Close"]
            nifty_sma50 = nifty_close.rolling(window=50).mean().iloc[-1]
            nifty_latest = nifty_close.iloc[-1]
            m_score = nifty_latest > nifty_sma50
            m_rows = [
                {"label": "Nifty 50", "value": f"{nifty_latest:,.2f}", "signal": None},
                {"label": "Nifty 50 SMA(50)", "value": f"{nifty_sma50:,.2f}", "signal": None},
                {"label": "Market Trend", "value": "Uptrend" if m_score else "Downtrend",
                 "signal": "bullish" if m_score else "bearish"},
            ]
        else:
            m_score = False
            m_rows = [{"label": "Market Data", "value": "Unavailable", "signal": None}]
    except Exception:
        m_score = False
        m_rows = [{"label": "Market Data", "value": "Unavailable", "signal": None}]

    m_rows.append({"label": "M Score", "value": "PASS" if m_score else "FAIL",
                   "signal": "bullish" if m_score else "bearish"})
    yield {"section": "M — Market Direction", "rows": m_rows}

    # --- Overall CAN SLIM ---
    total_pass = sum([c_score, a_score, n_score, s_score, l_score, i_score, m_score])
    if total_pass >= 6:
        rating, rating_s = "STRONG", "bullish"
    elif total_pass >= 4:
        rating, rating_s = "MODERATE", "neutral"
    else:
        rating, rating_s = "WEAK", "bearish"

    yield {
        "section": "CAN SLIM Rating",
        "is_summary": True,
        "rows": [
            {"label": "Rating", "value": f"{rating} ({total_pass}/7)", "signal": rating_s},
        ],
    }
