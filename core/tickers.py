"""NSE stock ticker directory for autocomplete suggestions."""

# Top ~200 NSE stocks by market cap / popularity
# Format: (SYMBOL, COMPANY_NAME)
NSE_TICKERS = [
    ("RELIANCE", "Reliance Industries"),
    ("TCS", "Tata Consultancy Services"),
    ("HDFCBANK", "HDFC Bank"),
    ("INFY", "Infosys"),
    ("ICICIBANK", "ICICI Bank"),
    ("HINDUNILVR", "Hindustan Unilever"),
    ("SBIN", "State Bank of India"),
    ("BHARTIARTL", "Bharti Airtel"),
    ("ITC", "ITC Limited"),
    ("KOTAKBANK", "Kotak Mahindra Bank"),
    ("LT", "Larsen & Toubro"),
    ("HCLTECH", "HCL Technologies"),
    ("AXISBANK", "Axis Bank"),
    ("ASIANPAINT", "Asian Paints"),
    ("MARUTI", "Maruti Suzuki India"),
    ("SUNPHARMA", "Sun Pharmaceutical"),
    ("TITAN", "Titan Company"),
    ("BAJFINANCE", "Bajaj Finance"),
    ("DMART", "Avenue Supermarts (DMart)"),
    ("ULTRACEMCO", "UltraTech Cement"),
    ("WIPRO", "Wipro"),
    ("ONGC", "Oil & Natural Gas Corp"),
    ("NTPC", "NTPC Limited"),
    ("TMCV", "Tata Motors Commercial Vehicles"),
    ("TMPV", "Tata Motors Passenger Vehicles"),
    ("JSWSTEEL", "JSW Steel"),
    ("POWERGRID", "Power Grid Corp"),
    ("M&M", "Mahindra & Mahindra"),
    ("TATASTEEL", "Tata Steel"),
    ("ADANIENT", "Adani Enterprises"),
    ("ADANIPORTS", "Adani Ports & SEZ"),
    ("ADANIGREEN", "Adani Green Energy"),
    ("ADANIPOWER", "Adani Power"),
    ("COALINDIA", "Coal India"),
    ("HINDALCO", "Hindalco Industries"),
    ("GRASIM", "Grasim Industries"),
    ("NESTLEIND", "Nestle India"),
    ("TECHM", "Tech Mahindra"),
    ("BAJAJFINSV", "Bajaj Finserv"),
    ("BAJAJ-AUTO", "Bajaj Auto"),
    ("INDUSINDBK", "IndusInd Bank"),
    ("HDFCLIFE", "HDFC Life Insurance"),
    ("SBILIFE", "SBI Life Insurance"),
    ("BRITANNIA", "Britannia Industries"),
    ("CIPLA", "Cipla"),
    ("DRREDDY", "Dr. Reddy's Laboratories"),
    ("EICHERMOT", "Eicher Motors"),
    ("DIVISLAB", "Divi's Laboratories"),
    ("BPCL", "Bharat Petroleum"),
    ("HEROMOTOCO", "Hero MotoCorp"),
    ("APOLLOHOSP", "Apollo Hospitals"),
    ("TATACONSUM", "Tata Consumer Products"),
    ("PIDILITIND", "Pidilite Industries"),
    ("DABUR", "Dabur India"),
    ("GODREJCP", "Godrej Consumer Products"),
    ("HAVELLS", "Havells India"),
    ("SHREECEM", "Shree Cement"),
    ("AMBUJACEM", "Ambuja Cements"),
    ("ACC", "ACC Limited"),
    ("DLF", "DLF Limited"),
    ("GODREJPROP", "Godrej Properties"),
    ("IRCTC", "IRCTC"),
    ("ZOMATO", "Zomato"),
    ("PAYTM", "One97 Communications (Paytm)"),
    ("NYKAA", "FSN E-Commerce (Nykaa)"),
    ("POLICYBZR", "PB Fintech (PolicyBazaar)"),
    ("DELHIVERY", "Delhivery"),
    ("SIEMENS", "Siemens India"),
    ("ABB", "ABB India"),
    ("HAL", "Hindustan Aeronautics"),
    ("BEL", "Bharat Electronics"),
    ("BHEL", "Bharat Heavy Electricals"),
    ("IOC", "Indian Oil Corporation"),
    ("GAIL", "GAIL India"),
    ("VEDL", "Vedanta Limited"),
    ("TRENT", "Trent Limited"),
    ("JUBLFOOD", "Jubilant FoodWorks"),
    ("PAGEIND", "Page Industries"),
    ("MUTHOOTFIN", "Muthoot Finance"),
    ("CHOLAFIN", "Cholamandalam Fin"),
    ("BANKBARODA", "Bank of Baroda"),
    ("PNB", "Punjab National Bank"),
    ("CANBK", "Canara Bank"),
    ("UNIONBANK", "Union Bank of India"),
    ("IDFCFIRSTB", "IDFC First Bank"),
    ("FEDERALBNK", "Federal Bank"),
    ("BANDHANBNK", "Bandhan Bank"),
    ("AUBANK", "AU Small Finance Bank"),
    ("MCDOWELL-N", "United Spirits"),
    ("COLPAL", "Colgate-Palmolive India"),
    ("MARICO", "Marico"),
    ("BERGEPAINT", "Berger Paints India"),
    ("VOLTAS", "Voltas"),
    ("WHIRLPOOL", "Whirlpool of India"),
    ("CROMPTON", "Crompton Greaves Consumer"),
    ("POLYCAB", "Polycab India"),
    ("ASTRAL", "Astral Limited"),
    ("SUPREMEIND", "Supreme Industries"),
    ("PIIND", "PI Industries"),
    ("UPL", "UPL Limited"),
    ("BIOCON", "Biocon"),
    ("AUROPHARMA", "Aurobindo Pharma"),
    ("LUPIN", "Lupin"),
    ("TORNTPHARM", "Torrent Pharmaceuticals"),
    ("ALKEM", "Alkem Laboratories"),
    ("IPCALAB", "IPCA Laboratories"),
    ("LALPATHLAB", "Dr Lal PathLabs"),
    ("METROPOLIS", "Metropolis Healthcare"),
    ("MAXHEALTH", "Max Healthcare"),
    ("FORTIS", "Fortis Healthcare"),
    ("SBICARD", "SBI Cards"),
    ("MFSL", "Max Financial Services"),
    ("ICICIGI", "ICICI Lombard General Ins"),
    ("ICICIPRULI", "ICICI Prudential Life Ins"),
    ("HDFCAMC", "HDFC Asset Management"),
    ("NAM-INDIA", "Nippon Life India AMC"),
    ("MCX", "Multi Commodity Exchange"),
    ("BSE", "BSE Limited"),
    ("CDSL", "CDSL"),
    ("CAMS", "Computer Age Management"),
    ("NAUKRI", "Info Edge (Naukri)"),
    ("INDIAMART", "IndiaMART InterMESH"),
    ("PERSISTENT", "Persistent Systems"),
    ("COFORGE", "Coforge"),
    ("LTTS", "L&T Technology Services"),
    ("MPHASIS", "Mphasis"),
    ("LTIM", "LTIMindtree"),
    ("OFSS", "Oracle Financial Services"),
    ("TATAELXSI", "Tata Elxsi"),
    ("DIXON", "Dixon Technologies"),
    ("KAYNES", "Kaynes Technology"),
    ("DEEPAKNTR", "Deepak Nitrite"),
    ("ATUL", "Atul Limited"),
    ("SRF", "SRF Limited"),
    ("NAVINFLUOR", "Navin Fluorine Intl"),
    ("FLUOROCHEM", "Gujarat Fluorochemicals"),
    ("CLEAN", "Clean Science & Tech"),
    ("TATACHEM", "Tata Chemicals"),
    ("SAIL", "Steel Authority of India"),
    ("NMDC", "NMDC Limited"),
    ("NATIONALUM", "National Aluminium"),
    ("JINDALSTEL", "Jindal Steel & Power"),
    ("TATAPOWER", "Tata Power"),
    ("ADANITRANS", "Adani Energy Solutions"),
    ("TORNTPOWER", "Torrent Power"),
    ("CESC", "CESC Limited"),
    ("NHPC", "NHPC Limited"),
    ("RECLTD", "REC Limited"),
    ("PFC", "Power Finance Corp"),
    ("IRFC", "Indian Railway Finance"),
    ("MOTHERSON", "Samvardhana Motherson"),
    ("BOSCHLTD", "Bosch Limited"),
    ("MRF", "MRF Limited"),
    ("BALKRISIND", "Balkrishna Industries"),
    ("CEATLTD", "CEAT Limited"),
    ("APOLLOTYRE", "Apollo Tyres"),
    ("BHARATFORG", "Bharat Forge"),
    ("THERMAX", "Thermax"),
    ("CUMMINSIND", "Cummins India"),
    ("ESCORTS", "Escorts Kubota"),
    ("ASHOKLEY", "Ashok Leyland"),
    ("TVSMOTORS", "TVS Motor Company"),
    ("OBEROIRLTY", "Oberoi Realty"),
    ("PRESTIGE", "Prestige Estates"),
    ("PHOENIXLTD", "Phoenix Mills"),
    ("LODHA", "Macrotech Developers"),
    ("SOBHA", "Sobha Limited"),
    ("INDHOTEL", "Indian Hotels (Taj)"),
    ("LEMON TREE", "Lemon Tree Hotels"),
    ("EIHOTEL", "EIH Limited"),
    ("TATACOMM", "Tata Communications"),
    ("IDEA", "Vodafone Idea"),
    ("ROUTE", "Route Mobile"),
    ("RAIN", "Rain Industries"),
    ("TRIDENT", "Trident Limited"),
    ("IEX", "Indian Energy Exchange"),
    ("ABCAPITAL", "Aditya Birla Capital"),
    ("ABFRL", "Aditya Birla Fashion"),
    ("RAYMOND", "Raymond"),
    ("VBL", "Varun Beverages"),
    ("PGHH", "Procter & Gamble Hygiene"),
    ("HONAUT", "Honeywell Automation"),
    ("3MINDIA", "3M India"),
    ("KAJARIACER", "Kajaria Ceramics"),
    ("CENTURYTEX", "Century Textiles"),
    ("JKCEMENT", "JK Cement"),
    ("RAMCOCEM", "Ramco Cements"),
    ("STARCEMENT", "Star Cement"),
    ("JSWENERGY", "JSW Energy"),
    ("SJVN", "SJVN Limited"),
    ("CONCOR", "Container Corp of India"),
    ("GMRINFRA", "GMR Airports Infra"),
    ("SUZLON", "Suzlon Energy"),
    ("RELINFRA", "Reliance Infrastructure"),
    ("YESBANK", "Yes Bank"),
    ("MANAPPURAM", "Manappuram Finance"),
    ("L&TFH", "L&T Finance"),
    ("EXIDEIND", "Exide Industries"),
    ("AMARAJABAT", "Amara Raja Energy"),
]


def _search_local(query: str, limit: int) -> list[dict]:
    """Search the local ticker list."""
    query_upper = query.upper().strip()
    results = []

    # Exact symbol prefix matches first
    for symbol, name in NSE_TICKERS:
        if symbol.startswith(query_upper):
            results.append({"symbol": symbol, "name": name})

    # Then name matches
    query_lower = query.lower()
    for symbol, name in NSE_TICKERS:
        if query_lower in name.lower() and {"symbol": symbol, "name": name} not in results:
            results.append({"symbol": symbol, "name": name})

    return results[:limit]


def _search_yahoo(query: str, limit: int) -> list[dict]:
    """Fallback: search Yahoo Finance for NSE/BSE tickers."""
    import requests

    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": query, "quotesCount": limit, "newsCount": 0}
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        r.raise_for_status()

        results = []
        for q in r.json().get("quotes", []):
            # Only include NSE (.NS) and BSE (.BO) stocks
            sym = q.get("symbol", "")
            if sym.endswith(".NS") or sym.endswith(".BO"):
                clean_symbol = sym.rsplit(".", 1)[0]
                name = q.get("longname") or q.get("shortname") or clean_symbol
                exchange = "NSE" if sym.endswith(".NS") else "BSE"
                results.append({
                    "symbol": clean_symbol,
                    "name": f"{name} ({exchange})",
                })
        return results[:limit]
    except Exception:
        return []


def search_tickers(query: str, limit: int = 8) -> list[dict]:
    """Search tickers — local list first, Yahoo Finance fallback.

    Returns list of {"symbol": ..., "name": ...} dicts.
    """
    query = query.strip()
    if not query:
        return []

    # Try local list first
    local_results = _search_local(query, limit)

    if len(local_results) >= 3:
        return local_results

    # Supplement with Yahoo Finance search
    yahoo_results = _search_yahoo(query, limit)
    seen = {r["symbol"] for r in local_results}
    for yr in yahoo_results:
        if yr["symbol"] not in seen:
            local_results.append(yr)
            seen.add(yr["symbol"])

    return local_results[:limit]
