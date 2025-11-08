from sqlalchemy import insert, select, update, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import SKU, Location, SKUBarcode, StockLedger, StockMovement


async def find_sku_by_barcode(session: AsyncSession, barcode: str):
    q = select(SKU).join(SKUBarcode).where(SKUBarcode.barcode == barcode)
    res = await session.execute(q)
    sku = res.scalars().first()
    return sku


async def get_sku_by_id(session: AsyncSession, sku_id):
    """Get SKU by ID."""
    q = select(SKU).where(SKU.id == sku_id)
    res = await session.execute(q)
    return res.scalars().first()


async def get_barcodes_for_sku(session: AsyncSession, sku_id):
    """Get all barcodes for a SKU."""
    q = select(SKUBarcode).where(SKUBarcode.sku_id == sku_id)
    res = await session.execute(q)
    return res.scalars().all()


async def get_stock_levels_by_sku(session: AsyncSession, sku_id):
    """Get all stock levels for a SKU across locations."""
    q = (
        select(StockLedger)
        .options(selectinload(StockLedger.location))
        .where(StockLedger.sku_id == sku_id)
    )
    res = await session.execute(q)
    return res.scalars().all()


async def list_skus(session: AsyncSession, skip: int = 0, limit: int = 50, search: str = None):
    """List SKUs with pagination and optional search."""
    q = select(SKU)
    
    if search:
        search_pattern = f"%{search}%"
        q = q.where(
            (SKU.sku_code.ilike(search_pattern)) | (SKU.title.ilike(search_pattern))
        )
    
    # Get total count
    count_q = select(func.count()).select_from(q.subquery())
    total_res = await session.execute(count_q)
    total = total_res.scalar()
    
    # Get paginated results
    q = q.offset(skip).limit(limit).order_by(SKU.created_at.desc())
    res = await session.execute(q)
    skus = res.scalars().all()
    
    return skus, total


async def get_stock_levels(
    session: AsyncSession, location_code: str = None, sku_code: str = None
):
    """Get stock levels with optional filters."""
    q = (
        select(StockLedger)
        .options(selectinload(StockLedger.sku), selectinload(StockLedger.location))
    )
    
    if location_code:
        q = q.join(Location).where(Location.code == location_code)
    
    if sku_code:
        q = q.join(SKU).where(SKU.sku_code == sku_code)
    
    res = await session.execute(q)
    return res.scalars().all()


async def list_movements(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    movement_type: str = None,
    sku_code: str = None,
    location_code: str = None,
    created_by: str = None,
):
    """List stock movements with filtering and pagination."""
    q = (
        select(StockMovement)
        .options(selectinload(StockMovement.sku), selectinload(StockMovement.location))
    )
    
    if movement_type:
        q = q.where(StockMovement.movement_type == movement_type)
    
    if sku_code:
        q = q.join(SKU).where(SKU.sku_code == sku_code)
    
    if location_code:
        q = q.join(Location).where(Location.code == location_code)
    
    if created_by:
        q = q.where(StockMovement.created_by == created_by)
    
    # Get total count
    count_q = select(func.count()).select_from(q.subquery())
    total_res = await session.execute(count_q)
    total = total_res.scalar()
    
    # Get paginated results
    q = q.offset(skip).limit(limit).order_by(StockMovement.created_at.desc())
    res = await session.execute(q)
    movements = res.scalars().all()
    
    return movements, total


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
