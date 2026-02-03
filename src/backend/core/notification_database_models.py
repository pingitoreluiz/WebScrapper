"""
Notification Database Models
"""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Float, Integer, DateTime, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column

from .database_models import Base

class NotificationChannel(str, PyEnum):
    """Available notification channels"""
    TELEGRAM = "telegram"
    DISCORD = "discord"
    EMAIL = "email"

class Alert(Base):
    """
    User Alert preferences
    
    Stores trigger conditions for price alerts.
    """
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User identification (chat_id for telegram, webhook_url/id for discord, email address)
    recipient: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Channel type
    channel: Mapped[str] = mapped_column(
        SQLEnum(NotificationChannel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    
    # Trigger conditions
    keyword: Mapped[str] = mapped_column(String(200), nullable=False) # e.g., "RTX 4060"
    target_price: Mapped[float] = mapped_column(Float, nullable=False) # Alert if price < target
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_alert_recipient", "recipient"),
        Index("idx_alert_keyword", "keyword"),
        Index("idx_alert_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Alert(to={self.recipient}, keyword='{self.keyword}', target={self.target_price})>"
