"""
Service interfaces package.

Interfaces define contracts for services that the application layer needs.
These will be implemented by the infrastructure layer.
"""

from .browser_service import BrowserService
from .extractor_service import ExtractorService

__all__ = ["BrowserService", "ExtractorService"]
