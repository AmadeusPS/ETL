from datetime import datetime
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    sku: str | None = None
    category: str | None = None
    current_price: float | None = None
    currency: str = "EUR"
    target_margin: float | None = None


class ProductRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    sku: str | None
    category: str | None
    current_price: float | None
    currency: str
    target_margin: float | None
    created_at: datetime


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    current_price: float | None = None
    target_margin: float | None = None


class CompetitorProductCreate(BaseModel):
    store_id: int
    url: str
    name: str | None = None
    sku: str | None = None


class CompetitorProductRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    store_id: int
    url: str
    name: str | None
    current_price: float | None
    previous_price: float | None
    currency: str
    in_stock: bool | None
    last_scraped_at: datetime | None
