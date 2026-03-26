import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RecommendationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    applied = "applied"


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    context_input: Mapped[str] = mapped_column(Text, nullable=False)   # JSON snapshot sent to Claude
    claude_output: Mapped[str] = mapped_column(Text, nullable=False)   # Raw Claude response
    suggested_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus), default=RecommendationStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    product: Mapped["Product"] = relationship(back_populates="ai_recommendations")
