"""
Price value object - Immutable representation of a monetary value.

Handles currency, validation, and comparison logic.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional
import re


@dataclass(frozen=True)
class Price:
    """
    Price value object representing a monetary amount.
    
    This is an immutable value object with validation and business logic.
    
    Attributes:
        amount: Decimal amount (always positive)
        currency: Currency code (default: BRL)
        raw_string: Original string representation (optional)
    """
    
    amount: Decimal
    currency: str = "BRL"
    raw_string: Optional[str] = None
    
    def __post_init__(self):
        """Validate price after initialization."""
        # Use object.__setattr__ because dataclass is frozen
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate price business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if self.amount < 0:
            raise ValueError("Price amount cannot be negative")
        
        if self.amount == 0:
            raise ValueError("Price amount cannot be zero")
        
        if not self.currency or not self.currency.strip():
            raise ValueError("Currency cannot be empty")
        
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code (e.g., BRL, USD)")
    
    @classmethod
    def from_string(cls, price_str: str, currency: str = "BRL") -> "Price":
        """
        Create Price from a string representation.
        
        Handles various formats:
        - "R$ 1.234,56"
        - "1234.56"
        - "1,234.56"
        
        Args:
            price_str: String representation of price
            currency: Currency code
            
        Returns:
            Price value object
            
        Raises:
            ValueError: If string cannot be parsed
        """
        if not price_str or not price_str.strip():
            raise ValueError("Price string cannot be empty")
        
        # Remove currency symbols and whitespace
        cleaned = price_str.strip()
        cleaned = re.sub(r'[R$\s]', '', cleaned)
        
        # Handle Brazilian format (1.234,56)
        if ',' in cleaned and '.' in cleaned:
            # Check which comes last
            if cleaned.rindex(',') > cleaned.rindex('.'):
                # Brazilian format: 1.234,56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US format: 1,234.56
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma, assume Brazilian format
            cleaned = cleaned.replace(',', '.')
        
        try:
            amount = Decimal(cleaned)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Cannot parse price from '{price_str}': {e}")
        
        return cls(amount=amount, currency=currency, raw_string=price_str)
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "BRL") -> "Price":
        """
        Create Price from a float value.
        
        Args:
            amount: Float amount
            currency: Currency code
            
        Returns:
            Price value object
        """
        return cls(amount=Decimal(str(amount)), currency=currency)
    
    def to_float(self) -> float:
        """
        Convert price to float.
        
        Returns:
            Price as float
        """
        return float(self.amount)
    
    def format(self, locale: str = "pt_BR") -> str:
        """
        Format price for display.
        
        Args:
            locale: Locale for formatting (pt_BR or en_US)
            
        Returns:
            Formatted price string
        """
        if locale == "pt_BR":
            # Brazilian format: R$ 1.234,56
            amount_str = f"{self.amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"R$ {amount_str}"
        else:
            # US format: $1,234.56
            return f"${self.amount:,.2f}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.format()
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Price(amount={self.amount}, currency='{self.currency}')"
    
    def __lt__(self, other: "Price") -> bool:
        """Less than comparison."""
        if not isinstance(other, Price):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare prices with different currencies")
        return self.amount < other.amount
    
    def __le__(self, other: "Price") -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Price):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare prices with different currencies")
        return self.amount <= other.amount
    
    def __gt__(self, other: "Price") -> bool:
        """Greater than comparison."""
        if not isinstance(other, Price):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare prices with different currencies")
        return self.amount > other.amount
    
    def __ge__(self, other: "Price") -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Price):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError("Cannot compare prices with different currencies")
        return self.amount >= other.amount
