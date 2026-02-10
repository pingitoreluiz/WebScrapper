"""Tests for ProductUrl value object."""

import pytest

from src.scrapers.domain.value_objects.url import ProductUrl


class TestProductUrl:
    """Test suite for ProductUrl value object."""

    def test_create_url_with_valid_https(self):
        """Test creating URL with valid HTTPS."""
        url = ProductUrl("https://example.com/product/123")

        assert url.url == "https://example.com/product/123"
        assert url.normalized is not None

    def test_create_url_with_valid_http(self):
        """Test creating URL with valid HTTP."""
        url = ProductUrl("http://example.com/product/123")

        assert url.url == "http://example.com/product/123"

    def test_url_cannot_be_empty(self):
        """Test that URL cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProductUrl("")

        with pytest.raises(ValueError, match="cannot be empty"):
            ProductUrl("   ")

    def test_url_must_have_scheme(self):
        """Test that URL must have a scheme."""
        with pytest.raises(ValueError, match="must have a scheme"):
            ProductUrl("example.com/product")

    def test_url_scheme_must_be_http_or_https(self):
        """Test that URL scheme must be http or https."""
        with pytest.raises(ValueError, match="must be http or https"):
            ProductUrl("ftp://example.com/file")

    def test_url_must_have_domain(self):
        """Test that URL must have a domain."""
        with pytest.raises(ValueError, match="must have a domain"):
            ProductUrl("https://")

    def test_url_normalization_removes_trailing_slash(self):
        """Test that normalization removes trailing slash."""
        url1 = ProductUrl("https://example.com/product/")
        url2 = ProductUrl("https://example.com/product")

        assert url1.normalized == url2.normalized

    def test_url_normalization_lowercases_scheme_and_domain(self):
        """Test that normalization lowercases scheme and domain."""
        url = ProductUrl("HTTPS://EXAMPLE.COM/Product")

        assert url.normalized.startswith("https://example.com")

    def test_url_normalization_removes_default_ports(self):
        """Test that normalization removes default ports."""
        url_http = ProductUrl("http://example.com:80/product")
        url_https = ProductUrl("https://example.com:443/product")

        assert ":80" not in url_http.normalized
        assert ":443" not in url_https.normalized

    def test_get_domain(self):
        """Test extracting domain from URL."""
        url = ProductUrl("https://www.example.com/product/123")

        assert url.get_domain() == "www.example.com"

    def test_get_path(self):
        """Test extracting path from URL."""
        url = ProductUrl("https://example.com/product/123")

        assert url.get_path() == "/product/123"

    def test_is_same_domain(self):
        """Test checking if URLs are from same domain."""
        url1 = ProductUrl("https://example.com/product/1")
        url2 = ProductUrl("https://example.com/product/2")
        url3 = ProductUrl("https://other.com/product/1")

        assert url1.is_same_domain(url2) is True
        assert url1.is_same_domain(url3) is False

    def test_url_equality_based_on_normalized(self):
        """Test that URL equality is based on normalized URL."""
        url1 = ProductUrl("https://example.com/product/")
        url2 = ProductUrl("https://example.com/product")
        url3 = ProductUrl("https://example.com/other")

        assert url1 == url2  # Same after normalization
        assert url1 != url3

    def test_url_hash(self):
        """Test that URL can be used in sets/dicts."""
        url1 = ProductUrl("https://example.com/product/1")
        url2 = ProductUrl("https://example.com/product/2")

        url_set = {url1, url2}
        assert len(url_set) == 2

    def test_str_representation(self):
        """Test string representation."""
        url = ProductUrl("https://example.com/product")

        assert str(url) == "https://example.com/product"

    def test_url_is_immutable(self):
        """Test that URL is immutable (frozen dataclass)."""
        url = ProductUrl("https://example.com/product")

        with pytest.raises(Exception):  # FrozenInstanceError
            url.url = "https://other.com"
