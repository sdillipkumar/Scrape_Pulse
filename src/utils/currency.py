# src/utils/currency.py
from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from forex_python.converter import CurrencyRates, RatesNotAvailableError

_PRICE_RE = re.compile(r"[-+]?\d[\d,]*\.?\d*")

def parse_gbp_text(price_text: str) -> Optional[float]:
    """
    Normalize strings like '£51.77', 'Â£51.77', 'GBP 51.77' -> 51.77
    """
    if not price_text:
        return None
    t = (price_text.replace("Â", "")         # fix mojibake
                    .replace("£", "")
                    .replace("GBP", "")
                    .strip())
    m = _PRICE_RE.search(t)
    if not m:
        return None
    # remove thousands separators, keep decimal point
    return float(m.group(0).replace(",", ""))

@dataclass
class _FxCache:
    rate: float
    fetched_at: datetime

class LiveFx:
    """
    Small wrapper around forex-python with TTL caching.
    """
    def __init__(self, base: str = "GBP", target: str = "INR", ttl_seconds: int = 3600):
        self.base = base
        self.target = target
        self.ttl = timedelta(seconds=ttl_seconds)
        self._cache: Optional[_FxCache] = None
        self._client = CurrencyRates()

    def _expired(self) -> bool:
        if not self._cache:
            return True
        return (datetime.utcnow() - self._cache.fetched_at) > self.ttl

    def get_rate(self) -> float:
        if self._expired():
            rate = self._client.get_rate(self.base, self.target)  # raises RatesNotAvailableError on failure
            self._cache = _FxCache(rate=rate, fetched_at=datetime.utcnow())
        return self._cache.rate  # type: ignore

    def convert(self, amount: float) -> float:
        return amount * self.get_rate()
