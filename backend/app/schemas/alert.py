from datetime import datetime
from pydantic import BaseModel
from app.models.alert import AlertType


class AlertRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    alert_type: AlertType
    message: str
    is_read: bool
    created_at: datetime
