"""
URL value object - Immutable representation of a product URL.

Handles URL validation and normalization.
"""

from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse
from typing import Optional


@dataclass(frozen=True)
class ProductUrl:
    """
    ProductUrl value object representing a product's web address.
    
    This is an immutable value object with validation.
    
    Attributes:
        url: The URL string
        normalized: Normalized version of URL
    """
    
    url: str
    normalized: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize URL after initialization."""
        self._validate()
        
        # Normalize URL
        if self.normalized is None:
            object.__setattr__(self, 'normalized', self._normalize(self.url))
    
    def _validate(self) -> None:
        """
        Validate URL business rules.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.url or not self.url.strip():
            raise ValueError("URL cannot be empty")
        
        # Parse URL
        parsed = urlparse(self.url)
        
        if not parsed.scheme:
            raise ValueError("URL must have a scheme (http/https)")
        
        if parsed.scheme not in ('http', 'https'):
            raise ValueError("URL scheme must be http or https")
        
        if not parsed.netloc:
            raise ValueError("URL must have a domain")
    
    def _normalize(self, url: str) -> str:
        """
        Normalize URL for comparison.
        
        - Removes trailing slashes
        - Lowercases scheme and domain
        - Removes default ports
        - Sorts query parameters
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        parsed = urlparse(url)
        
        # Lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        
        # Remove default ports
        if netloc.endswith(':80') and scheme == 'http':
            netloc = netloc[:-3]
        elif netloc.endswith(':443') and scheme == 'https':
            netloc = netloc[:-4]
        
        # Remove trailing slash from path
        path = parsed.path.rstrip('/')
        if not path:
            path = '/'
        
        # Reconstruct URL
        normalized = urlunparse((
            scheme,
            netloc,
            path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        return normalized
    
    def get_domain(self) -> str:
        """
        Extract domain from URL.
        
        Returns:
            Domain name
        """
        parsed = urlparse(self.url)
        return parsed.netloc
    
    def get_path(self) -> str:
        """
        Extract path from URL.
        
        Returns:
            URL path
        """
        parsed = urlparse(self.url)
        return parsed.path
    
    def is_same_domain(self, other: "ProductUrl") -> bool:
        """
        Check if this URL is from the same domain as another.
        
        Args:
            other: Another ProductUrl
            
        Returns:
            True if same domain
        """
        return self.get_domain() == other.get_domain()
    
    def __str__(self) -> str:
        """String representation."""
        return self.url
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"ProductUrl('{self.url}')"
    
    def __eq__(self, other) -> bool:
        """Equality based on normalized URL."""
        if not isinstance(other, ProductUrl):
            return False
        return self.normalized == other.normalized
    
    def __hash__(self) -> int:
        """Hash based on normalized URL."""
        return hash(self.normalized)
