"""
Custom exceptions for scrapers

Defines specific exceptions for better error handling and control flow.
"""


class ScraperError(Exception):
    """Base exception for all scraper errors"""
    pass


class CaptchaDetected(ScraperError):
    """Raised when a CAPTCHA or human verification is detected"""
    
    def __init__(self, message: str = "CAPTCHA or human verification detected"):
        self.message = message
        super().__init__(self.message)


class PageLoadError(ScraperError):
    """Raised when a page fails to load properly"""
    
    def __init__(self, url: str, message: str = "Failed to load page"):
        self.url = url
        self.message = f"{message}: {url}"
        super().__init__(self.message)


class SelectorNotFound(ScraperError):
    """Raised when a required selector is not found on the page"""
    
    def __init__(self, selector: str, message: str = "Selector not found"):
        self.selector = selector
        self.message = f"{message}: {selector}"
        super().__init__(self.message)


class ExtractionError(ScraperError):
    """Raised when data extraction fails"""
    
    def __init__(self, field: str, message: str = "Failed to extract"):
        self.field = field
        self.message = f"{message} field '{field}'"
        super().__init__(self.message)


class ValidationError(ScraperError):
    """Raised when extracted data fails validation"""
    
    def __init__(self, field: str, value: any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        self.message = f"Validation failed for '{field}' with value '{value}': {reason}"
        super().__init__(self.message)


class BrowserError(ScraperError):
    """Raised when browser operations fail"""
    
    def __init__(self, message: str = "Browser operation failed"):
        self.message = message
        super().__init__(self.message)


class MaxRetriesExceeded(ScraperError):
    """Raised when maximum retry attempts are exceeded"""
    
    def __init__(self, attempts: int, operation: str = "operation"):
        self.attempts = attempts
        self.operation = operation
        self.message = f"Max retries ({attempts}) exceeded for {operation}"
        super().__init__(self.message)
