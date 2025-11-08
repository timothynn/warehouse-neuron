from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IntakeRequest(BaseModel):
    barcode: str
    qty: int = 1
    location_code: Optional[str] = None
    movement_type: Optional[str] = "IN"
    auto_create_sku: Optional[bool] = False
    created_by: Optional[str] = None


class IntakeResponse(BaseModel):
    movement_id: UUID
    sku_id: UUID
    sku_code: str
    on_hand: int
