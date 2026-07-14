"""
SQLAlchemy database models definition.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy declarative models.
    """
    pass


class RawListing(Base):
    """
    SQLAlchemy model representing a raw scraped real estate listing.
    
    This acts as a historical log, keeping all scrapes (no deduplication at this stage).
    """
    __tablename__ = "raw_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    external_id: Mapped[str] = mapped_column(String(100), index=True)
    url: Mapped[str] = mapped_column(String(500))
    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bedrooms: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    area: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    amenities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<RawListing(id={self.id}, source={self.source}, external_id={self.external_id}, price={self.price})>"
