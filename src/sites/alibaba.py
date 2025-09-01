import asyncio
from typing import AsyncGenerator, Iterable, Optional, Union

import httpx
from parsel import Selector

from src.common.models import ProductItem  # your existing model


def _jittered_delay(base: float, jitter: float) -> float:
    import random
    return max(0.05, base + random.uniform(-jitter, jitter))


def _load_settings(settings_or_path: Optional[Union[str, dict]]) -> dict:
    """
    Accepts either a dict or a YAML file path and returns a dict.
    """
    if isinstance(settings_or_path, dict) or settings_or_path is None:
        return settings_or_path or {}
    try:
        import yaml  # PyYAML
        with open(settings_or_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


class AlibabaFetcher:
    """
    Lightweight HTML fetcher for Alibaba showroom/category pages.

    Compatible signature with CLI:
        AlibabaFetcher(settings_cfg, proxy=..., respect_robots=...)

    - Accepts settings as dict OR YAML path.
    - HTTP/2 disabled to avoid 'h2' dependency.
    - Resilient per-URL try/except around network access.
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
        """
        Minimal retry loop for a single GET; respects global timeout.
        """
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

    # -------------------- public iterators --------------------

    async def iter_showroom_pages(
        self,
        showroom_urls: Iterable[str],
        label: str,
        base_delay: float = 1.2,
        jitter: float = 1.0,
    ) -> AsyncGenerator[ProductItem, None]:
        """
        Iterate showroom pages and yield lightweight ProductItem stubs.
        """
        async with httpx.AsyncClient(
            http2=False,  # IMPORTANT: avoid requiring 'h2'
            headers=self._headers(),
            follow_redirects=True,
            proxies=self.proxy,
        ) as client:
            for url in showroom_urls:
                if not url:
                    continue
                try:
                    html = await self._get(client, url)
                except Exception as e:
                    print(f"[Alibaba] showroom error: {url} -> {e}")
                    await asyncio.sleep(_jittered_delay(base_delay, jitter))
                    continue

                sel = Selector(html)

                # product tiles typically link to '/product-detail/'
                for a_html in sel.css("a[href*='/product-detail/']").getall():
                    s = Selector(text=a_html)
                    href = s.css("a::attr(href)").get()
                    title = s.css("a::attr(title), a::text").get()
                    if href:
                        yield ProductItem(
                            site="alibaba",
                            category=label,
                            title=(title or "").strip() or None,
                            product_page_url=href,
                            url=url,
                        )

                await asyncio.sleep(_jittered_delay(base_delay, jitter))

    # ---- compatibility aliases (match CLI expectations) ----

    async def iter_category_pages(
        self,
        category_urls: Iterable[str],
        label: str,
        base_delay: float = 1.2,
        jitter: float = 1.0,
    ) -> AsyncGenerator[ProductItem, None]:
        """
        Some CLIs call this name. Delegate to iter_showroom_pages.
        """
        async for item in self.iter_showroom_pages(
            showroom_urls=category_urls,
            label=label,
            base_delay=base_delay,
            jitter=jitter,
        ):
            yield item

    async def iter_showrooms(
        self,
        showroom_urls: Iterable[str],
        label: str,
        base_delay: float = 1.2,
        jitter: float = 1.0,
    ) -> AsyncGenerator[ProductItem, None]:
        """
        Some CLIs call this name. Delegate to iter_showroom_pages.
        """
        async for item in self.iter_showroom_pages(
            showroom_urls=showroom_urls,
            label=label,
            base_delay=base_delay,
            jitter=jitter,
        ):
            yield item
