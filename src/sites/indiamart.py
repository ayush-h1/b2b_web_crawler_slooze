import asyncio
from urllib.parse import urlencode
from typing import AsyncGenerator, Iterable, Optional, Union

import httpx
from parsel import Selector

from src.common.models import ProductItem  # your existing model


def _jittered_delay(base: float, jitter: float) -> float:
    import random
    return max(0.05, base + random.uniform(-jitter, jitter))


def _load_settings(settings_or_path: Optional[Union[str, dict]]) -> dict:
    if isinstance(settings_or_path, dict) or settings_or_path is None:
        return settings_or_path or {}
    # string path -> YAML
    try:
        import yaml  # PyYAML
        with open(settings_or_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


class IndiaMartFetcher:
    """
    Lightweight HTML fetcher for IndiaMART category/search pages.

    Compatible signature with CLI:
        IndiaMartFetcher(settings_cfg, proxy=..., respect_robots=...)

    - Accepts settings as dict OR YAML path.
    - http2 disabled to avoid 'h2' dependency on Windows.
    - Resilient: per-request try/except.
    """

    def __init__(
        self,
        settings: Optional[Union[str, dict]] = None,
        proxy: Optional[str] = None,
        respect_robots: bool = True,
    ):
        self.settings = _load_settings(settings)
        self.user_agent_pool = self.settings.get("user_agent_pool", [])
        self.timeout = float(self.settings.get("timeout_seconds", 20))
        self.proxy = proxy or (self.settings.get("proxy") or "").strip() or None
        self.respect_robots = bool(respect_robots)

    # -------------------- helpers --------------------

    def _headers(self) -> dict:
        import random
        ua = random.choice(self.user_agent_pool) if self.user_agent_pool else (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
        return {
            "user-agent": ua,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
        }

    async def _get(self, client: httpx.AsyncClient, url: str) -> str:
        last_err = None
        retries = int(self.settings.get("max_retries", 3))
        for _ in range(max(1, retries)):
            try:
                r = await client.get(url, timeout=self.timeout)
                r.raise_for_status()
                return r.text
            except Exception as e:
                last_err = e
                await asyncio.sleep(0.75)
        raise last_err or RuntimeError("request failed")

    def _build_search_url(self, query: str, page: int = 1) -> str:
        return f"https://dir.indiamart.com/search.mp?{urlencode({'ss': query, 'pg': page})}"

    # -------------------- public iterators --------------------

    async def iter_search(
        self,
        query: str,
        max_pages: int = 1,
        base_delay: float = 1.2,
        jitter: float = 1.0,
    ) -> AsyncGenerator[ProductItem, None]:
        async with httpx.AsyncClient(
            http2=False,  # avoid h2
            headers=self._headers(),
            follow_redirects=True,
            proxies=self.proxy,
        ) as client:
            for page in range(1, max_pages + 1):
                url = self._build_search_url(query, page)
                try:
                    html = await self._get(client, url)
                except Exception as e:
                    print(f"[IndiaMART] search error: {url} -> {e}")
                    await asyncio.sleep(_jittered_delay(base_delay, jitter))
                    continue

                sel = Selector(html)
                for a_html in sel.css("a[href*='/proddetail/']").getall():
                    s = Selector(text=a_html)
                    href = s.css("a::attr(href)").get()
                    title = s.css("a::attr(title), a::text").get()
                    if href:
                        yield ProductItem(
                            site="indiamart",
                            category=query,
                            title=(title or "").strip() or None,
                            product_page_url=href,
                            url=url,
                        )

                await asyncio.sleep(_jittered_delay(base_delay, jitter))

    async def iter_category_pages(
        self,
        category_urls: Iterable[str],
        label: str,
        base_delay: float = 1.2,
        jitter: float = 1.0,
    ) -> AsyncGenerator[ProductItem, None]:
        async with httpx.AsyncClient(
            http2=False,
            headers=self._headers(),
            follow_redirects=True,
            proxies=self.proxy,
        ) as client:
            for url in category_urls:
                if not url:
                    continue
                try:
                    html = await self._get(client, url)
                except Exception as e:
                    print(f"[IndiaMART] category error: {url} -> {e}")
                    await asyncio.sleep(_jittered_delay(base_delay, jitter))
                    continue

                sel = Selector(html)
                for a_html in sel.css("a[href*='/proddetail/']").getall():
                    s = Selector(text=a_html)
                    href = s.css("a::attr(href)").get()
                    title = s.css("a::attr(title), a::text").get()
                    if href:
                        yield ProductItem(
                            site="indiamart",
                            category=label,
                            title=(title or "").strip() or None,
                            product_page_url=href,
                            url=url,
                        )

                await asyncio.sleep(_jittered_delay(base_delay, jitter))



