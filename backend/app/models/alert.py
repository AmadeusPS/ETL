import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AlertType(str, enum.Enum):
    price_drop = "price_drop"
    price_increase = "price_increase"
    new_product = "new_product"
    out_of_stock = "out_of_stock"
    back_in_stock = "back_in_stock"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=True)
    competitor_product_id: Mapped[int] = mapped_column(ForeignKey("competitor_products.id"), nullable=True)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_email: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user: Mapped["User"] = relationship(back_populates="alerts")
    product: Mapped["Product"] = relationship(back_populates="alerts")
