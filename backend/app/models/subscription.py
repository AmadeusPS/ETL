import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PlanTier(str, enum.Enum):
    basic = "basic"          # 3 stores, 50 products, 1 scrape/day
    pro = "pro"              # 10 stores, 500 products, 2 scrapes/day + AI
    enterprise = "enterprise"  # unlimited, priority support, white-label


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    plan: Mapped[PlanTier] = mapped_column(Enum(PlanTier), default=PlanTier.basic, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active")  # active, cancelled, past_due
    stripe_customer_id: Mapped[str] = mapped_column(String(128), nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(128), nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="subscription")
