"""Tests for Selector value objects."""

import pytest

from src.scrapers.domain.value_objects.selector import Selector, SelectorSet


class TestSelector:
    """Test suite for Selector value object."""

    def test_create_selector_with_valid_css(self):
        """Test creating selector with valid CSS."""
        selector = Selector(css=".product-card", description="Product card")

        assert selector.css == ".product-card"
        assert selector.description == "Product card"

    def test_selector_css_cannot_be_empty(self):
        """Test that CSS selector cannot be empty."""
        with pytest.raises(ValueError, match="CSS selector cannot be empty"):
            Selector(css="")

        with pytest.raises(ValueError, match="CSS selector cannot be empty"):
            Selector(css="   ")

    def test_selector_str_representation(self):
        """Test string representation."""
        selector = Selector(css=".product")
        assert str(selector) == ".product"

    def test_selector_is_immutable(self):
        """Test that selector is immutable."""
        selector = Selector(css=".product")

        with pytest.raises(Exception):  # FrozenInstanceError
            selector.css = ".other"


class TestSelectorSet:
    """Test suite for SelectorSet value object."""

    def test_create_selector_set_with_multiple_selectors(self):
        """Test creating selector set with multiple selectors."""
        selector_set = SelectorSet(
            selectors=[".product", ".item", ".card"], description="Product selectors"
        )

        assert len(selector_set) == 3
        assert selector_set.description == "Product selectors"

    def test_selector_set_cannot_be_empty(self):
        """Test that selector set must have at least one selector."""
        with pytest.raises(ValueError, match="must have at least one selector"):
            SelectorSet(selectors=[])

    def test_selector_set_cannot_have_empty_selector(self):
        """Test that selector set cannot contain empty selectors."""
        with pytest.raises(ValueError, match="Selector in set cannot be empty"):
            SelectorSet(selectors=[".product", "", ".item"])

    def test_from_single(self):
        """Test creating selector set from single selector."""
        selector_set = SelectorSet.from_single(".product", "Product")

        assert len(selector_set) == 1
        assert selector_set.get_primary() == ".product"
        assert selector_set.description == "Product"

    def test_get_primary(self):
        """Test getting primary selector."""
        selector_set = SelectorSet(selectors=[".primary", ".fallback1", ".fallback2"])

        assert selector_set.get_primary() == ".primary"

    def test_get_fallbacks(self):
        """Test getting fallback selectors."""
        selector_set = SelectorSet(selectors=[".primary", ".fallback1", ".fallback2"])

        fallbacks = selector_set.get_fallbacks()
        assert len(fallbacks) == 2
        assert fallbacks == [".fallback1", ".fallback2"]

    def test_has_fallbacks(self):
        """Test checking if has fallback selectors."""
        single = SelectorSet.from_single(".product")
        multiple = SelectorSet(selectors=[".product", ".item"])

        assert single.has_fallbacks() is False
        assert multiple.has_fallbacks() is True

    def test_iteration(self):
        """Test iterating over selectors."""
        selector_set = SelectorSet(selectors=[".a", ".b", ".c"])

        selectors = list(selector_set)
        assert selectors == [".a", ".b", ".c"]

    def test_length(self):
        """Test getting length."""
        selector_set = SelectorSet(selectors=[".a", ".b", ".c"])

        assert len(selector_set) == 3

    def test_indexing(self):
        """Test accessing by index."""
        selector_set = SelectorSet(selectors=[".a", ".b", ".c"])

        assert selector_set[0] == ".a"
        assert selector_set[1] == ".b"
        assert selector_set[2] == ".c"

    def test_selector_set_is_immutable(self):
        """Test that selector set is immutable."""
        selector_set = SelectorSet(selectors=[".product"])

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            selector_set.selectors = [".other"]

    def test_selectors_converted_to_tuple(self):
        """Test that selectors list is converted to tuple for immutability."""
        selector_set = SelectorSet(selectors=[".a", ".b"])

        assert isinstance(selector_set.selectors, tuple)

    def test_str_representation(self):
        """Test string representation."""
        selector_set = SelectorSet(selectors=[".a", ".b", ".c"])

        assert "3 selectors" in str(selector_set)
