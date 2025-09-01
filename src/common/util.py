
from __future__ import annotations
import random, re
from typing import Optional, Tuple

CURRENCY_SYMBOLS = {"₹":"INR","$":"USD","US$":"USD","€":"EUR","£":"GBP","CN¥":"CNY","¥":"CNY"}

def jittered_delay(base: float, jitter: float) -> float:
    return max(0.0, base + random.uniform(0, jitter))

def parse_price(price_text: Optional[str]) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not price_text: return None, None, None
    txt = price_text.replace(",", " ").strip()
    cur = next((code for sym,code in CURRENCY_SYMBOLS.items() if sym in txt), None)
    if not cur:
        m = re.search(r"\b(INR|USD|EUR|GBP|CNY|JPY|AED)\b", txt, re.I)
        if m: cur = m.group(1).upper()
    nums = [float(n.replace(" ", "")) for n in re.findall(r"(?<!\w)(\d+(?:\.\d+)?)", txt)]
    if not nums: return None, None, cur
    if len(nums)==1: return nums[0], nums[0], cur
    return min(nums[0], nums[1]), max(nums[0], nums[1]), cur
