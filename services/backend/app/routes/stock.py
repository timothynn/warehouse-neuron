import redis.asyncio as redis
from app import crud
from app.config import settings
from app.database import get_session
from app.schema import IntakeRequest, IntakeResponse
from app.cache import invalidate_stock_cache, invalidate_sku_cache
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/stock")


async def emit_event(event: dict):
    # simple Redis stream push; replace or expand with Kafka/Pulsar later
    client = redis.from_url(settings.redis_url)
    await client.xadd("stock_events", event)
    await client.aclose()


@router.post("/intake", response_model=IntakeResponse)
async def intake(payload: IntakeRequest, session: AsyncSession = Depends(get_session)):
    # find location (create if missing)
    location = None
    if payload.location_code:
        location = await crud.get_or_create_location(session, payload.location_code)

    sku = await crud.find_sku_by_barcode(session, payload.barcode)

    if not sku and not payload.auto_create_sku:
        raise HTTPException(
            status_code=404,
            detail="SKU not found for barcode. Set auto_create_sku to true to create a new SKU.",
        )

    if not sku:
        sku = await crud.create_sku_with_barcode(session, payload.barcode)

    # Update stock ledger
    ledger = await crud.upsert_stock_ledger(
        session, sku.id, location.id if location else None, payload.qty
    )

    # Record movement
    movement = await crud.create_stock_movement(
        session,
        sku_id=sku.id,
        location_id=location.id if location else None,
        qty=payload.qty,
        movement_type=payload.movement_type,
        barcode=payload.barcode,
        created_by=payload.created_by,
    )

    await session.commit()

    # Invalidate relevant caches
    await invalidate_stock_cache()
    await invalidate_sku_cache()

    # Emit event
    await emit_event(
        {
            "event_type": "stock_intake",
            "movement_id": str(movement.id),
            "sku_id": str(sku.id),
            "location_id": str(location.id) if location else None,
            "qty": payload.qty,
        }
    )

    return IntakeResponse(
        movement_id=movement.id,
        sku_id=sku.id,
        sku_code=sku.sku_code,
        on_hand=ledger.on_hand,
    )
