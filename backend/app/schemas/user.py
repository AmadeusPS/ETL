from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.subscription import PlanTier


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    cognito_sub: str


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None


class SubscriptionRead(BaseModel):
    model_config = {"from_attributes": True}

    plan: PlanTier
    status: str
    current_period_end: datetime | None
