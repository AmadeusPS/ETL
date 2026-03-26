from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PriceSnapshot(Base):
    """Historical price record for a competitor product."""

    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    competitor_product_id: Mapped[int] = mapped_column(ForeignKey("competitor_products.id"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="EUR")
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    competitor_product: Mapped["CompetitorProduct"] = relationship(back_populates="price_snapshots")
