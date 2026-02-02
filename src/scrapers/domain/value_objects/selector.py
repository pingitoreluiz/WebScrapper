"""
Selector value objects - CSS selectors for web scraping.

Immutable representations of CSS selectors with fallback support.
"""

from dataclasses import dataclass, field
from typing import List, Iterator


@dataclass(frozen=True)
class Selector:
    """
    Selector value object representing a single CSS selector.
    
    Attributes:
        css: CSS selector string
        description: Human-readable description
    """
    
    css: str
    description: str = ""
    
    def __post_init__(self):
        """Validate selector after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate selector business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.css or not self.css.strip():
            raise ValueError("CSS selector cannot be empty")
    
    def __str__(self) -> str:
        """String representation."""
        return self.css
    
    def __repr__(self) -> str:
        """Developer representation."""
        if self.description:
            return f"Selector('{self.css}', '{self.description}')"
        return f"Selector('{self.css}')"


@dataclass(frozen=True)
class SelectorSet:
    """
    SelectorSet value object representing multiple selectors with fallback.
    
    Allows trying multiple selectors in order until one matches.
    
    Attributes:
        selectors: List of CSS selectors to try (in order)
        description: Human-readable description of what this set selects
    """
    
    selectors: List[str]
    description: str = ""
    
    def __post_init__(self):
        """Validate selector set after initialization."""
        # Convert to tuple for immutability
        if not isinstance(self.selectors, tuple):
            object.__setattr__(self, 'selectors', tuple(self.selectors))
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate selector set business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.selectors:
            raise ValueError("SelectorSet must have at least one selector")
        
        for selector in self.selectors:
            if not selector or not selector.strip():
                raise ValueError("Selector in set cannot be empty")
    
    @classmethod
    def from_single(cls, selector: str, description: str = "") -> "SelectorSet":
        """
        Create SelectorSet from a single selector.
        
        Args:
            selector: CSS selector
            description: Description
            
        Returns:
            SelectorSet with single selector
        """
        return cls(selectors=[selector], description=description)
    
    def get_primary(self) -> str:
        """
        Get the primary (first) selector.
        
        Returns:
            Primary CSS selector
        """
        return self.selectors[0]
    
    def get_fallbacks(self) -> List[str]:
        """
        Get fallback selectors (all except first).
        
        Returns:
            List of fallback selectors
        """
        return list(self.selectors[1:])
    
    def has_fallbacks(self) -> bool:
        """
        Check if this set has fallback selectors.
        
        Returns:
            True if has more than one selector
        """
        return len(self.selectors) > 1
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over selectors."""
        return iter(self.selectors)
    
    def __len__(self) -> int:
        """Get number of selectors."""
        return len(self.selectors)
    
    def __getitem__(self, index: int) -> str:
        """Get selector by index."""
        return self.selectors[index]
    
    def __str__(self) -> str:
        """String representation."""
        return f"SelectorSet({len(self.selectors)} selectors)"
    
    def __repr__(self) -> str:
        """Developer representation."""
        selectors_str = ", ".join(f"'{s}'" for s in self.selectors)
        if self.description:
            return f"SelectorSet([{selectors_str}], '{self.description}')"
        return f"SelectorSet([{selectors_str}])"
