from sqlalchemy import insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from .models import SKU, Location, SKUBarcode, StockLedger, StockMovement


async def find_sku_by_barcode(session: AsyncSession, barcode: str):
    q = select(SKU).join(SKUBarcode).where(SKUBarcode.barcode == barcode)
    res = await session.execute(q)
    sku = res.scalars().first()
    return sku


async def get_or_create_location(session: AsyncSession, code: str):
    q = select(Location).where(Location.code == code)
    res = await session.execute(q)
    loc = res.scalars().first()
    if loc:
        return loc
    loc = Location(code=code, name=code)
    session.add(loc)
    await session.flush()
    return loc


async def create_sku_with_barcode(session: AsyncSession, barcode: str):
    sku = SKU(sku_code=barcode, title=barcode)
    session.add(sku)
    await session.flush()
    sku_barcode = SKUBarcode(sku_id=sku.id, barcode=barcode)
    session.add(sku_barcode)
    await session.flush()
    return sku


async def upsert_stock_ledger(
    session: AsyncSession, sku_id, location_id, delta_qty: int
):
    # attempt to select row
    q = select(StockLedger).where(
        StockLedger.sku_id == sku_id, StockLedger.location_id == location_id
    )
    res = await session.execute(q)
    row = res.scalars().first()
    if row:
        row.on_hand = (row.on_hand or 0) + delta_qty
        session.add(row)
        await session.flush()
        return row
    # create new ledger row
    ledger = StockLedger(sku_id=sku_id, location_id=location_id, on_hand=delta_qty)
    session.add(ledger)
    await session.flush()
    return ledger


async def create_stock_movement(
    session: AsyncSession,
    sku_id,
    location_id,
    qty,
    movement_type,
    barcode=None,
    batch=None,
    created_by=None,
    reference_id=None,
):
    mv = StockMovement(
        sku_id=sku_id,
        location_id=location_id,
        qty=qty,
        movement_type=movement_type,
        barcode=barcode,
        batch=batch,
        created_by=created_by,
        reference_id=reference_id,
    )
    session.add(mv)
    await session.flush()
    return mv
