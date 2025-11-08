from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.validators import (
    validate_barcode,
    validate_location_code,
    validate_quantity,
    validate_movement_type
)


class IntakeRequest(BaseModel):
    barcode: str
    qty: int = 1
    location_code: Optional[str] = None
    movement_type: Optional[str] = "IN"
    auto_create_sku: Optional[bool] = False
    created_by: Optional[str] = None
    
    @field_validator('barcode')
    @classmethod
    def validate_barcode_field(cls, v):
        """Validate and normalize barcode format."""
        return validate_barcode(v)
    
    @field_validator('qty')
    @classmethod
    def validate_qty_field(cls, v):
        """Validate quantity is positive and reasonable."""
        return validate_quantity(v)
    
    @field_validator('location_code')
    @classmethod
    def validate_location_field(cls, v):
        """Validate and normalize location code format."""
        if v is None:
            return v
        return validate_location_code(v)
    
    @field_validator('movement_type')
    @classmethod
    def validate_movement_field(cls, v):
        """Validate movement type is allowed."""
        if v is None:
            return "IN"
        return validate_movement_type(v)


class IntakeResponse(BaseModel):
    movement_id: UUID
    sku_id: UUID
    sku_code: str
    on_hand: int


class SKUResponse(BaseModel):
    id: UUID
    sku_code: str
    title: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StockLevelDetail(BaseModel):
    location_code: Optional[str]
    location_name: Optional[str]
    on_hand: int
    reserved: int


class SKUDetailResponse(BaseModel):
    id: UUID
    sku_code: str
    title: Optional[str]
    description: Optional[str]
    created_at: datetime
    barcodes: List[str]
    stock_levels: List[StockLevelDetail]

    class Config:
        from_attributes = True


class SKUListResponse(BaseModel):
    items: List[SKUResponse]
    total: int
    skip: int
    limit: int


class StockLevelResponse(BaseModel):
    sku_id: UUID
    sku_code: str
    location_id: Optional[UUID]
    location_code: Optional[str]
    on_hand: int
    reserved: int
    available: int


class MovementResponse(BaseModel):
    id: UUID
    sku_id: UUID
    sku_code: str
    location_id: Optional[UUID]
    location_code: Optional[str]
    qty: int
    movement_type: str
    barcode: Optional[str]
    batch: Optional[str]
    reference_id: Optional[str]
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MovementListResponse(BaseModel):
    items: List[MovementResponse]
    total: int
    skip: int
    limit: int
