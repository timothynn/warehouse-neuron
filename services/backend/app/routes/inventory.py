from typing import Optional
from uuid import UUID

from app import crud
from app.database import get_session
from app.schema import StockLevelResponse, MovementListResponse, MovementResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/stock")


@router.get("/levels", response_model=list[StockLevelResponse])
async def get_stock_levels(
    location_code: Optional[str] = Query(None, description="Filter by location code"),
    sku_code: Optional[str] = Query(None, description="Filter by SKU code"),
    session: AsyncSession = Depends(get_session),
):
    """Get stock levels, optionally filtered by location or SKU."""
    levels = await crud.get_stock_levels(
        session, location_code=location_code, sku_code=sku_code
    )

    return [
        StockLevelResponse(
            sku_id=level.sku_id,
            sku_code=level.sku.sku_code,
            location_id=level.location_id,
            location_code=level.location.code if level.location else None,
            on_hand=level.on_hand,
            reserved=level.reserved,
            available=level.on_hand - level.reserved,
        )
        for level in levels
    ]


@router.get("/movements", response_model=MovementListResponse)
async def list_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    sku_code: Optional[str] = Query(None, description="Filter by SKU code"),
    location_code: Optional[str] = Query(None, description="Filter by location code"),
    created_by: Optional[str] = Query(None, description="Filter by user"),
    session: AsyncSession = Depends(get_session),
):
    """List stock movements with filtering and pagination."""
    movements, total = await crud.list_movements(
        session,
        skip=skip,
        limit=limit,
        movement_type=movement_type,
        sku_code=sku_code,
        location_code=location_code,
        created_by=created_by,
    )

    items = [
        MovementResponse(
            id=mov.id,
            sku_id=mov.sku_id,
            sku_code=mov.sku.sku_code,
            location_id=mov.location_id,
            location_code=mov.location.code if mov.location else None,
            qty=mov.qty,
            movement_type=mov.movement_type,
            barcode=mov.barcode,
            batch=mov.batch,
            reference_id=mov.reference_id,
            created_by=mov.created_by,
            created_at=mov.created_at,
        )
        for mov in movements
    ]

    return MovementListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
