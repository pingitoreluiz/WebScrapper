"""Tests for Product entity."""

import pytest
from datetime import datetime
from uuid import uuid4

from src.scrapers.domain.entities.product import Product
from src.scrapers.domain.value_objects.price import Price
from src.scrapers.domain.value_objects.url import ProductUrl


class TestProduct:
    """Test suite for Product entity."""

    def test_create_product_with_valid_data(self):
        """Test creating a product with valid data."""
        price = Price.from_string("R$ 2.500,00")
        url = ProductUrl("https://example.com/product/123")

        product = Product(
            title="ASUS RTX 4070 DUAL OC",
            price=price,
            url=url,
            store="Pichau",
            chip_brand="NVIDIA",
            manufacturer="ASUS",
            model="RTX 4070",
        )

        assert product.title == "ASUS RTX 4070 DUAL OC"
        assert product.price == price
        assert product.url == url
        assert product.store == "Pichau"
        assert product.chip_brand == "NVIDIA"
        assert product.manufacturer == "ASUS"
        assert product.model == "RTX 4070"
        assert product.available is True
        assert isinstance(product.id, type(uuid4()))

    def test_product_title_cannot_be_empty(self):
        """Test that product title cannot be empty."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        with pytest.raises(ValueError, match="title cannot be empty"):
            Product(title="", price=price, url=url, store="Test")

        with pytest.raises(ValueError, match="title cannot be empty"):
            Product(title="   ", price=price, url=url, store="Test")

    def test_product_title_max_length(self):
        """Test that product title has max length."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        long_title = "A" * 501
        with pytest.raises(ValueError, match="title too long"):
            Product(title=long_title, price=price, url=url, store="Test")

    def test_product_store_cannot_be_empty(self):
        """Test that product store cannot be empty."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        with pytest.raises(ValueError, match="store cannot be empty"):
            Product(title="Test", price=price, url=url, store="")

    def test_update_price(self):
        """Test updating product price."""
        price1 = Price.from_string("R$ 2.000,00")
        price2 = Price.from_string("R$ 1.800,00")
        url = ProductUrl("https://example.com/product/1")

        product = Product(title="Test", price=price1, url=url, store="Test")
        original_updated_at = product.updated_at

        product.update_price(price2)

        assert product.price == price2
        assert product.updated_at > original_updated_at

    def test_mark_unavailable(self):
        """Test marking product as unavailable."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        product = Product(title="Test", price=price, url=url, store="Test")
        assert product.available is True

        product.mark_unavailable()
        assert product.available is False

    def test_mark_available(self):
        """Test marking product as available."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        product = Product(
            title="Test", price=price, url=url, store="Test", available=False
        )
        assert product.available is False

        product.mark_available()
        assert product.available is True

    def test_is_gpu(self):
        """Test checking if product is a GPU."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        gpu_product = Product(
            title="RTX 4070", price=price, url=url, store="Test", chip_brand="NVIDIA"
        )
        assert gpu_product.is_gpu() is True

        non_gpu_product = Product(
            title="Some Product", price=price, url=url, store="Test"
        )
        assert non_gpu_product.is_gpu() is False

    def test_get_display_name(self):
        """Test getting formatted display name."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        product = Product(
            title="Long product title",
            price=price,
            url=url,
            store="Test",
            manufacturer="ASUS",
            chip_brand="NVIDIA",
            model="RTX 4070",
        )

        assert product.get_display_name() == "ASUS NVIDIA RTX 4070"

    def test_product_equality(self):
        """Test product equality based on ID."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        product1 = Product(title="Test", price=price, url=url, store="Test")
        product2 = Product(title="Test", price=price, url=url, store="Test")

        assert product1 != product2  # Different IDs
        assert product1 == product1  # Same instance

    def test_product_hash(self):
        """Test product can be used in sets/dicts."""
        price = Price.from_string("R$ 1.000,00")
        url = ProductUrl("https://example.com/product/1")

        product1 = Product(title="Test1", price=price, url=url, store="Test")
        product2 = Product(title="Test2", price=price, url=url, store="Test")

        product_set = {product1, product2}
        assert len(product_set) == 2
