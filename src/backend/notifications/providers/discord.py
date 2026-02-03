"""
Discord Webhook Provider
"""

import aiohttp
import logging
from typing import Optional
from datetime import datetime

from .base import NotificationProvider

logger = logging.getLogger(__name__)

class DiscordWebhookProvider(NotificationProvider):
    """
    Sends notifications via Discord Webhooks
    """

    async def send_alert(self, recipient: str, message: str, title: Optional[str] = None, image_url: Optional[str] = None, product_url: Optional[str] = None) -> bool:
        """
        Send Discord Webhook
        
        Args:
            recipient: Discord Webhook URL
        """
        if not recipient.startswith("http"):
            logger.error(f"Invalid Discord webhook URL: {recipient}")
            return False

        embed = {
            "description": message,
            "color": 5814783, # Discord Blue/Blurple
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "GPU Price Scraper • Alerta de Preço"
            }
        }
        
        if title:
            embed["title"] = title
            
        if product_url:
            embed["url"] = product_url
            
        if image_url:
            embed["thumbnail"] = {"url": image_url}

        payload = {
            "username": "GPU Scraper Bot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2362/2362363.png", # Generic chip icon
            "embeds": [embed]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(recipient, json=payload) as response:
                    if response.status in (200, 204):
                        logger.info("Discord alert sent successfully")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Failed to send Discord alert. Status: {response.status}, Response: {text}")
                        return False
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {e}")
            return False
