"""
Base Notification Provider
"""

from abc import ABC, abstractmethod
from typing import Optional

class NotificationProvider(ABC):
    """Abstract base class for notification providers"""

    @abstractmethod
    async def send_alert(self, recipient: str, message: str, title: Optional[str] = None, image_url: Optional[str] = None, product_url: Optional[str] = None) -> bool:
        """
        Send an alert message
        
        Args:
            recipient: The destination (webhook URL, chat ID, email address)
            message: The main content of the alert
            title: Optional title (for embeds/emails)
            image_url: Optional product image URL
            product_url: Optional link to the deal
            
        Returns:
            bool: True if sent successfully
        """
        pass
