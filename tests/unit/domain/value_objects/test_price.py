"""Tests for Price value object."""

import pytest
from decimal import Decimal

from src.scrapers.domain.value_objects.price import Price


class TestPrice:
    """Test suite for Price value object."""
    
    def test_create_price_with_decimal(self):
        """Test creating price with Decimal."""
        price = Price(amount=Decimal("1500.50"), currency="BRL")
        
        assert price.amount == Decimal("1500.50")
        assert price.currency == "BRL"
    
    def test_create_price_with_float_converts_to_decimal(self):
        """Test that float is converted to Decimal."""
        price = Price(amount=1500.50, currency="BRL")
        
        assert isinstance(price.amount, Decimal)
        assert price.amount == Decimal("1500.50")
    
    def test_price_amount_cannot_be_negative(self):
        """Test that price amount cannot be negative."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Price(amount=Decimal("-100"), currency="BRL")
    
    def test_price_amount_cannot_be_zero(self):
        """Test that price amount cannot be zero."""
        with pytest.raises(ValueError, match="cannot be zero"):
            Price(amount=Decimal("0"), currency="BRL")
    
    def test_currency_cannot_be_empty(self):
        """Test that currency cannot be empty."""
        with pytest.raises(ValueError, match="Currency cannot be empty"):
            Price(amount=Decimal("100"), currency="")
    
    def test_currency_must_be_3_letters(self):
        """Test that currency must be 3-letter code."""
        with pytest.raises(ValueError, match="must be 3-letter code"):
            Price(amount=Decimal("100"), currency="US")
        
        with pytest.raises(ValueError, match="must be 3-letter code"):
            Price(amount=Decimal("100"), currency="USDD")
    
    def test_from_string_brazilian_format(self):
        """Test parsing Brazilian price format."""
        price = Price.from_string("R$ 1.234,56")
        
        assert price.amount == Decimal("1234.56")
        assert price.currency == "BRL"
        assert price.raw_string == "R$ 1.234,56"
    
    def test_from_string_us_format(self):
        """Test parsing US price format."""
        price = Price.from_string("1,234.56", currency="USD")
        
        assert price.amount == Decimal("1234.56")
        assert price.currency == "USD"
    
    def test_from_string_simple_format(self):
        """Test parsing simple number format."""
        price = Price.from_string("1234.56")
        
        assert price.amount == Decimal("1234.56")
    
    def test_from_string_with_only_comma(self):
        """Test parsing format with only comma (Brazilian)."""
        price = Price.from_string("1234,56")
        
        assert price.amount == Decimal("1234.56")
    
    def test_from_string_invalid_format(self):
        """Test that invalid format raises error."""
        with pytest.raises(ValueError, match="Cannot parse price"):
            Price.from_string("invalid")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            Price.from_string("")
    
    def test_from_float(self):
        """Test creating price from float."""
        price = Price.from_float(1234.56, currency="USD")
        
        assert price.amount == Decimal("1234.56")
        assert price.currency == "USD"
    
    def test_to_float(self):
        """Test converting price to float."""
        price = Price(amount=Decimal("1234.56"), currency="BRL")
        
        assert price.to_float() == 1234.56
        assert isinstance(price.to_float(), float)
    
    def test_format_brazilian_locale(self):
        """Test formatting price in Brazilian locale."""
        price = Price(amount=Decimal("1234.56"), currency="BRL")
        
        formatted = price.format(locale="pt_BR")
        assert formatted == "R$ 1.234,56"
    
    def test_format_us_locale(self):
        """Test formatting price in US locale."""
        price = Price(amount=Decimal("1234.56"), currency="USD")
        
        formatted = price.format(locale="en_US")
        assert formatted == "$1,234.56"
    
    def test_str_representation(self):
        """Test string representation."""
        price = Price(amount=Decimal("1234.56"), currency="BRL")
        
        assert str(price) == "R$ 1.234,56"
    
    def test_price_comparison_less_than(self):
        """Test price less than comparison."""
        price1 = Price(amount=Decimal("100"), currency="BRL")
        price2 = Price(amount=Decimal("200"), currency="BRL")
        
        assert price1 < price2
        assert not price2 < price1
    
    def test_price_comparison_greater_than(self):
        """Test price greater than comparison."""
        price1 = Price(amount=Decimal("200"), currency="BRL")
        price2 = Price(amount=Decimal("100"), currency="BRL")
        
        assert price1 > price2
        assert not price2 > price1
    
    def test_price_comparison_different_currencies_raises_error(self):
        """Test that comparing different currencies raises error."""
        price_brl = Price(amount=Decimal("100"), currency="BRL")
        price_usd = Price(amount=Decimal("100"), currency="USD")
        
        with pytest.raises(ValueError, match="different currencies"):
            price_brl < price_usd
    
    def test_price_equality(self):
        """Test price equality."""
        price1 = Price(amount=Decimal("100"), currency="BRL")
        price2 = Price(amount=Decimal("100"), currency="BRL")
        price3 = Price(amount=Decimal("200"), currency="BRL")
        
        assert price1 == price2
        assert price1 != price3
    
    def test_price_is_immutable(self):
        """Test that price is immutable (frozen dataclass)."""
        price = Price(amount=Decimal("100"), currency="BRL")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            price.amount = Decimal("200")
