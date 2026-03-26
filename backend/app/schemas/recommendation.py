from datetime import datetime
from pydantic import BaseModel
from app.models.ai_recommendation import RecommendationStatus


class RecommendationRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    product_id: int
    suggested_price: float | None
    reasoning: str | None
    status: RecommendationStatus
    created_at: datetime


class RecommendationAction(BaseModel):
    status: RecommendationStatus  # accepted | rejected | applied
