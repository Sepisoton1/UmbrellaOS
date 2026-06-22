"""
settings_client.py — Single source of truth for bot-side config.

Every cog that needs a dashboard-managed setting (API keys, feature flags,
etc.) should call get_setting() here instead of reading os.environ or
hitting the backend directly. This keeps:
  - one cache (short TTL, avoids hammering the backend on every message)
  - one place to look when something's misconfigured
  - one code path if the backend auth/URL ever changes

Cogs should NOT keep their own os.getenv() copies of dashboard-managed
settings going forward — fetch them here instead.
"""
import time
import httpx
from config import config

_cache: dict[str, tuple[str, float]] = {}
CACHE_TTL = 60  # seconds — matches the backend's own settings cache window


async def get_setting(key: str, default: str = "") -> str:
    """Fetch a setting's current value, using a short-lived cache."""
    now = time.time()
    cached = _cache.get(key)
    if cached and (now - cached[1]) < CACHE_TTL:
        return cached[0]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{config.UMBRELLA_API_URL}/api/v1/settings/{key}",
                headers={"X-Admin-Key": config.UMBRELLA_ADMIN_KEY},
            )
            if r.status_code == 200:
                value = r.json().get("value", default)
                _cache[key] = (value, now)
                return value
            else:
                print(f"[SettingsClient] GET {key} -> HTTP {r.status_code}")
    except Exception as e:
        print(f"[SettingsClient] Failed to fetch '{key}': {e}")

    # Backend unreachable / error: serve last known value if we have one,
    # rather than silently falling back to an empty/placeholder default.
    if cached:
        return cached[0]
    return default


def invalidate(key: str | None = None) -> None:
    """Drop a cached value (or everything) to force a fresh fetch next call."""
    if key is None:
        _cache.clear()
    else:
        _cache.pop(key, None)
