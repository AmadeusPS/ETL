from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CompetitorProduct(Base):
    """A product URL from a competitor store being monitored."""

    __tablename__ = "competitor_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=True)
    sku: Mapped[str] = mapped_column(String(128), nullable=True)
    current_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    previous_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="EUR")
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=True)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=True)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    store: Mapped["Store"] = relationship(back_populates="competitor_products")
    price_snapshots: Mapped[list["PriceSnapshot"]] = relationship(back_populates="competitor_product")
