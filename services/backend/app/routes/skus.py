from typing import Optional
from uuid import UUID

from app import crud
from app.database import get_session
from app.schema import SKUResponse, SKUListResponse, SKUDetailResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/skus")


@router.get("/{sku_id}", response_model=SKUDetailResponse)
async def get_sku(sku_id: UUID, session: AsyncSession = Depends(get_session)):
    """Get detailed information about a specific SKU including stock levels."""
    sku = await crud.get_sku_by_id(session, sku_id)
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # Get barcodes
    barcodes = await crud.get_barcodes_for_sku(session, sku_id)

    # Get stock levels by location
    stock_levels = await crud.get_stock_levels_by_sku(session, sku_id)

    return SKUDetailResponse(
        id=sku.id,
        sku_code=sku.sku_code,
        title=sku.title,
        description=sku.description,
        created_at=sku.created_at,
        barcodes=[b.barcode for b in barcodes],
        stock_levels=[
            {
                "location_code": sl.location.code if sl.location else None,
                "location_name": sl.location.name if sl.location else None,
                "on_hand": sl.on_hand,
                "reserved": sl.reserved,
            }
            for sl in stock_levels
        ],
    )


@router.get("", response_model=SKUListResponse)
async def list_skus(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by SKU code or title"),
    session: AsyncSession = Depends(get_session),
):
    """List all SKUs with pagination and optional search."""
    skus, total = await crud.list_skus(session, skip=skip, limit=limit, search=search)

    items = [
        SKUResponse(
            id=sku.id,
            sku_code=sku.sku_code,
            title=sku.title,
            description=sku.description,
            created_at=sku.created_at,
        )
        for sku in skus
    ]

    return SKUListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
    )
