from __future__ import annotations
import urllib.robotparser as urobot
from urllib.parse import urlparse
from functools import lru_cache

@lru_cache(maxsize=64)
def _get_parser(origin: str) -> urobot.RobotFileParser:
    rp = urobot.RobotFileParser()
    rp.set_url(f"{origin}/robots.txt")
    try: rp.read()
    except Exception: pass
    return rp

def allowed(url: str, user_agent: str = "slooze-b2b-crawler") -> bool:
    from urllib.parse import urlparse
    parsed = urlparse(url); origin = f"{parsed.scheme}://{parsed.netloc}"
    rp = _get_parser(origin)
    try: return bool(rp.can_fetch(user_agent, url))
    except Exception: return False
