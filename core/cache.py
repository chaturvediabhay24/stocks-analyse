"""Market-aware in-memory cache for stock data.

IN stocks invalidate after Indian market close (4:00 PM IST daily).
US stocks invalidate after US market close  (5:00 AM IST daily).
Failed fetches are never cached — they retry fresh on the next call.
"""

import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

IST = ZoneInfo("Asia/Kolkata")

# Refresh boundaries in IST
REFRESH_TIMES = {
    "IN": time(3, 0),  # 3:00 AM IST — after Indian market close
    # "US": time(5, 0),   # 5:00 AM IST — after US market close
}

# {cache_key: (data, fetched_at)}
_store: dict[tuple, tuple] = {}


def _make_key(func_name: str, symbol: str, market: str, **kwargs) -> tuple:
    extras = tuple(sorted(kwargs.items()))
    return (func_name, symbol.upper(), market.upper(), extras)


def _last_refresh_boundary(market: str) -> datetime:
    """Return the most recent refresh boundary for the given market."""
    now = datetime.now(IST)
    refresh_time = REFRESH_TIMES.get(market.upper(), REFRESH_TIMES["IN"])
    boundary_today = datetime.combine(now.date(), refresh_time, tzinfo=IST)

    if now >= boundary_today:
        return boundary_today
    else:
        return boundary_today - timedelta(days=1)


def get(func_name: str, symbol: str, market: str, **kwargs):
    """Return cached data if still valid, otherwise None."""
    key = _make_key(func_name, symbol, market, **kwargs)
    entry = _store.get(key)
    if entry is None:
        logger.debug("CACHE MISS  %s", key)
        return None

    data, fetched_at = entry
    boundary = _last_refresh_boundary(market)

    if fetched_at < boundary:
        # Data was fetched before the last refresh boundary — stale
        del _store[key]
        logger.debug("CACHE STALE %s (fetched %s, boundary %s)", key, fetched_at, boundary)
        return None

    logger.debug("CACHE HIT   %s (fetched %s)", key, fetched_at)
    return data


def _purge_stale() -> int:
    """Remove all expired entries from the cache. Returns count purged."""
    now = datetime.now(IST)
    stale_keys = []
    for key, (_, fetched_at) in _store.items():
        # market is the 3rd element in the key tuple
        market = key[2]
        refresh_time = REFRESH_TIMES.get(market, REFRESH_TIMES["IN"])
        boundary_today = datetime.combine(now.date(), refresh_time, tzinfo=IST)
        boundary = boundary_today if now >= boundary_today else boundary_today - timedelta(days=1)
        if fetched_at < boundary:
            stale_keys.append(key)
    for key in stale_keys:
        logger.debug("CACHE PURGE %s", key)
        del _store[key]
    return len(stale_keys)


def set(func_name: str, symbol: str, market: str, data, **kwargs):
    """Store data in cache with the current timestamp. Purges stale entries."""
    purged = _purge_stale()
    key = _make_key(func_name, symbol, market, **kwargs)
    _store[key] = (data, datetime.now(IST))
    logger.debug("CACHE SET   %s (store size: %d, purged: %d)", key, len(_store), purged)
