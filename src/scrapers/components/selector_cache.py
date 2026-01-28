"""
Selector caching for performance optimization

Caches successful selectors to avoid retrying failed ones.
"""

from typing import Dict, List, Optional
from ...utils.logger import get_logger

logger = get_logger(__name__)


class SelectorCache:
    """
    Cache for successful CSS selectors

    When multiple selectors are tried, cache the one that works
    to avoid retrying failed selectors on subsequent elements.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str, selectors: List[str], test_func=None) -> str:
        """
        Get cached selector or find working one

        Args:
            key: Cache key (e.g., 'product_title')
            selectors: List of selectors to try
            test_func: Optional function to test if selector works

        Returns:
            Working selector (either cached or newly found)
        """
        # Check cache first
        if key in self._cache:
            self._hits += 1
            logger.debug("selector_cache_hit", key=key, selector=self._cache[key])
            return self._cache[key]

        # Cache miss - find working selector
        self._misses += 1

        if test_func:
            # Use test function to find working selector
            for selector in selectors:
                if test_func(selector):
                    self._cache[key] = selector
                    logger.debug("selector_cached", key=key, selector=selector)
                    return selector

        # No test function or none worked - return first
        if selectors:
            self._cache[key] = selectors[0]
            return selectors[0]

        return ""

    def set(self, key: str, selector: str) -> None:
        """Manually set a cached selector"""
        self._cache[key] = selector
        logger.debug("selector_manually_cached", key=key, selector=selector)

    def clear(self) -> None:
        """Clear all cached selectors"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.debug("selector_cache_cleared")

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": round(hit_rate, 2),
            "cached_selectors": len(self._cache),
        }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"SelectorCache(cached={stats['cached_selectors']}, hit_rate={stats['hit_rate']}%)"
