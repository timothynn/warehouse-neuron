"""Unit tests for CRUD operations."""
import pytest
from uuid import uuid4

from app import crud
from app.models import SKU, Location, SKUBarcode, StockLedger, StockMovement


@pytest.mark.asyncio
async def test_create_sku_with_barcode(session):
    """Test creating a SKU with a barcode."""
    barcode = "TEST123"
    sku = await crud.create_sku_with_barcode(session, barcode)
    
    assert sku.sku_code == barcode
    assert sku.title == barcode
    assert sku.id is not None
    
    # Verify barcode was created
    barcodes = await crud.get_barcodes_for_sku(session, sku.id)
    assert len(barcodes) == 1
    assert barcodes[0].barcode == barcode


@pytest.mark.asyncio
async def test_find_sku_by_barcode(session):
    """Test finding a SKU by barcode."""
    barcode = "FIND123"
    created_sku = await crud.create_sku_with_barcode(session, barcode)
    await session.commit()
    
    found_sku = await crud.find_sku_by_barcode(session, barcode)
    
    assert found_sku is not None
    assert found_sku.id == created_sku.id
    assert found_sku.sku_code == barcode


@pytest.mark.asyncio
async def test_find_sku_by_barcode_not_found(session):
    """Test finding a non-existent SKU returns None."""
    found_sku = await crud.find_sku_by_barcode(session, "NONEXISTENT")
    assert found_sku is None


@pytest.mark.asyncio
async def test_get_or_create_location(session):
    """Test creating a new location."""
    code = "WH-A-01"
    location = await crud.get_or_create_location(session, code)
    
    assert location.code == code
    assert location.name == code
    assert location.id is not None


@pytest.mark.asyncio
async def test_get_or_create_location_existing(session):
    """Test getting an existing location."""
    code = "WH-B-01"
    location1 = await crud.get_or_create_location(session, code)
    await session.commit()
    
    location2 = await crud.get_or_create_location(session, code)
    
    assert location1.id == location2.id


@pytest.mark.asyncio
async def test_upsert_stock_ledger_new(session):
    """Test creating a new stock ledger entry."""
    sku = await crud.create_sku_with_barcode(session, "LEDGER123")
    location = await crud.get_or_create_location(session, "WH-TEST")
    
    ledger = await crud.upsert_stock_ledger(session, sku.id, location.id, 10)
    
    assert ledger.sku_id == sku.id
    assert ledger.location_id == location.id
    assert ledger.on_hand == 10


@pytest.mark.asyncio
async def test_upsert_stock_ledger_update(session):
    """Test updating an existing stock ledger entry."""
    sku = await crud.create_sku_with_barcode(session, "UPDATE123")
    location = await crud.get_or_create_location(session, "WH-TEST2")
    
    # Create initial entry
    ledger1 = await crud.upsert_stock_ledger(session, sku.id, location.id, 10)
    await session.commit()
    
    # Update entry
    ledger2 = await crud.upsert_stock_ledger(session, sku.id, location.id, 5)
    
    assert ledger2.id == ledger1.id
    assert ledger2.on_hand == 15  # 10 + 5


@pytest.mark.asyncio
async def test_create_stock_movement(session):
    """Test creating a stock movement record."""
    sku = await crud.create_sku_with_barcode(session, "MOVE123")
    location = await crud.get_or_create_location(session, "WH-MOVE")
    
    movement = await crud.create_stock_movement(
        session,
        sku_id=sku.id,
        location_id=location.id,
        qty=5,
        movement_type="IN",
        barcode="MOVE123",
        created_by="test_user",
    )
    
    assert movement.sku_id == sku.id
    assert movement.location_id == location.id
    assert movement.qty == 5
    assert movement.movement_type == "IN"
    assert movement.barcode == "MOVE123"
    assert movement.created_by == "test_user"


@pytest.mark.asyncio
async def test_list_skus_empty(session):
    """Test listing SKUs when none exist."""
    skus, total = await crud.list_skus(session)
    
    assert len(skus) == 0
    assert total == 0


@pytest.mark.asyncio
async def test_list_skus_with_data(session):
    """Test listing SKUs with data."""
    # Create test SKUs
    await crud.create_sku_with_barcode(session, "SKU001")
    await crud.create_sku_with_barcode(session, "SKU002")
    await crud.create_sku_with_barcode(session, "SKU003")
    await session.commit()
    
    skus, total = await crud.list_skus(session, skip=0, limit=10)
    
    assert len(skus) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_list_skus_pagination(session):
    """Test SKU pagination."""
    # Create 5 test SKUs
    for i in range(5):
        await crud.create_sku_with_barcode(session, f"PAGE{i:03d}")
    await session.commit()
    
    # Get first page
    skus_page1, total = await crud.list_skus(session, skip=0, limit=2)
    assert len(skus_page1) == 2
    assert total == 5
    
    # Get second page
    skus_page2, _ = await crud.list_skus(session, skip=2, limit=2)
    assert len(skus_page2) == 2
    
    # Verify different results
    assert skus_page1[0].id != skus_page2[0].id


@pytest.mark.asyncio
async def test_list_skus_search(session):
    """Test SKU search functionality."""
    await crud.create_sku_with_barcode(session, "APPLE123")
    await crud.create_sku_with_barcode(session, "BANANA456")
    await crud.create_sku_with_barcode(session, "APPLE789")
    await session.commit()
    
    skus, total = await crud.list_skus(session, search="APPLE")
    
    assert len(skus) == 2
    assert total == 2
    assert all("APPLE" in sku.sku_code for sku in skus)


@pytest.mark.asyncio
async def test_get_stock_levels(session):
    """Test getting stock levels."""
    sku = await crud.create_sku_with_barcode(session, "LEVEL123")
    location = await crud.get_or_create_location(session, "WH-LEVEL")
    await crud.upsert_stock_ledger(session, sku.id, location.id, 25)
    await session.commit()
    
    levels = await crud.get_stock_levels(session)
    
    assert len(levels) > 0
    assert any(level.sku_id == sku.id for level in levels)


@pytest.mark.asyncio
async def test_list_movements(session):
    """Test listing stock movements."""
    sku = await crud.create_sku_with_barcode(session, "LISTMOVE123")
    location = await crud.get_or_create_location(session, "WH-LIST")
    
    await crud.create_stock_movement(
        session, sku_id=sku.id, location_id=location.id, qty=10, movement_type="IN"
    )
    await crud.create_stock_movement(
        session, sku_id=sku.id, location_id=location.id, qty=-5, movement_type="OUT"
    )
    await session.commit()
    
    movements, total = await crud.list_movements(session)
    
    assert len(movements) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_list_movements_filter_by_type(session):
    """Test filtering movements by type."""
    sku = await crud.create_sku_with_barcode(session, "FILTER123")
    location = await crud.get_or_create_location(session, "WH-FILTER")
    
    await crud.create_stock_movement(
        session, sku_id=sku.id, location_id=location.id, qty=10, movement_type="IN"
    )
    await crud.create_stock_movement(
        session, sku_id=sku.id, location_id=location.id, qty=-5, movement_type="OUT"
    )
    await crud.create_stock_movement(
        session, sku_id=sku.id, location_id=location.id, qty=3, movement_type="IN"
    )
    await session.commit()
    
    movements, total = await crud.list_movements(session, movement_type="IN")
    
    assert len(movements) == 2
    assert total == 2
    assert all(m.movement_type == "IN" for m in movements)
