"""
BrowserService interface - Contract for browser operations.

This interface defines what the application layer needs from a browser service.
Infrastructure will provide the concrete implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BrowserService(ABC):
    """
    Interface for browser operations.
    
    This abstracts away browser implementation details (Playwright, Selenium, etc.)
    from the application layer.
    """
    
    @abstractmethod
    async def initialize(self, headless: bool = True, **kwargs) -> None:
        """
        Initialize the browser.
        
        Args:
            headless: Run in headless mode
            **kwargs: Additional browser configuration
        """
        pass
    
    @abstractmethod
    async def navigate(self, url: str, timeout: int = 30000) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            timeout: Navigation timeout in milliseconds
            
        Raises:
            BrowserError: If navigation fails
        """
        pass
    
    @abstractmethod
    async def get_page_content(self) -> str:
        """
        Get the current page HTML content.
        
        Returns:
            HTML content as string
        """
        pass
    
    @abstractmethod
    async def find_elements(self, selector: str) -> list[Any]:
        """
        Find elements matching a CSS selector.
        
        Args:
            selector: CSS selector
            
        Returns:
            List of matching elements
        """
        pass
    
    @abstractmethod
    async def get_element_text(self, element: Any) -> Optional[str]:
        """
        Get text content of an element.
        
        Args:
            element: Element to get text from
            
        Returns:
            Text content or None
        """
        pass
    
    @abstractmethod
    async def get_element_attribute(
        self, element: Any, attribute: str
    ) -> Optional[str]:
        """
        Get attribute value of an element.
        
        Args:
            element: Element to get attribute from
            attribute: Attribute name
            
        Returns:
            Attribute value or None
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Check if browser is initialized.
        
        Returns:
            True if initialized
        """
        pass
