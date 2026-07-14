"""
SQLAlchemy database models definition.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, UniqueConstraint
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


class FeaturedListing(Base):
    """
    SQLAlchemy model representing a cleaned and feature-engineered listing.
    
    This table stores processed features ready for model training/prediction.
    Each row is unique for a given external_id and feature_set_version.
    """
    __tablename__ = "featured_listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(100), index=True)
    feature_set_version: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[float] = mapped_column()
    bedrooms: Mapped[int] = mapped_column()
    area: Mapped[float] = mapped_column()
    neighborhood: Mapped[str] = mapped_column(String(255), index=True)
    has_central_air: Mapped[int] = mapped_column(default=0)
    has_garage: Mapped[int] = mapped_column(default=0)
    has_pool: Mapped[int] = mapped_column(default=0)
    fireplace_count: Mapped[int] = mapped_column(default=0)
    price_per_sqft: Mapped[float] = mapped_column()
    description_length: Mapped[int] = mapped_column(default=0)
    has_luxury_keywords: Mapped[int] = mapped_column(default=0)
    is_below_market_value: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("external_id", "feature_set_version", name="uq_external_id_version"),
    )

    def __repr__(self) -> str:
        return f"<FeaturedListing(id={self.id}, external_id={self.external_id}, version={self.feature_set_version}, price={self.price})>"

