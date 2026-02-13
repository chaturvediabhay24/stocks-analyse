MARKET_CONFIG = {
    "IN": {
        "suffix": ".NS",
        "currency": "₹",
        "index": "^NSEI",
        "label": "India (NSE)",
    },
    "US": {
        "suffix": "",
        "currency": "$",
        "index": "^GSPC",
        "label": "US",
    },
}


def get_market_config(market: str = "IN") -> dict:
    return MARKET_CONFIG.get(market.upper(), MARKET_CONFIG["IN"])
