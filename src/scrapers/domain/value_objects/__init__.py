"""
Value objects package.

Value objects are immutable objects defined by their attributes rather than identity.
They contain validation logic and are compared by value.
"""

from .price import Price
from .url import ProductUrl
from .selector import Selector, SelectorSet

__all__ = ["Price", "ProductUrl", "Selector", "SelectorSet"]
