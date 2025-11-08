"""Integration tests for API endpoints."""
import pytest


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_stock_intake_new_sku(client):
    """Test stock intake with auto-create SKU."""
    response = client.post(
        "/api/v1/stock/intake",
        json={
            "barcode": "NEWSKU001",
            "qty": 10,
            "location_code": "WH-A-01",
            "movement_type": "IN",
            "auto_create_sku": True,
            "created_by": "test_user",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "sku_code" in data
    assert data["sku_code"] == "NEWSKU001"
    assert data["on_hand"] == 10


@pytest.mark.asyncio
async def test_stock_intake_without_auto_create(client):
    """Test stock intake without auto-create should fail."""
    response = client.post(
        "/api/v1/stock/intake",
        json={
            "barcode": "NONEXISTENT",
            "qty": 5,
            "auto_create_sku": False,
        },
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_stock_intake_existing_sku(client):
    """Test stock intake with existing SKU."""
    # Create SKU first
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "EXISTING001", "qty": 5, "auto_create_sku": True},
    )
    
    # Add more stock
    response = client.post(
        "/api/v1/stock/intake",
        json={"barcode": "EXISTING001", "qty": 3, "auto_create_sku": False},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["on_hand"] == 8  # 5 + 3


@pytest.mark.asyncio
async def test_list_skus(client):
    """Test listing SKUs."""
    # Create some SKUs
    for i in range(3):
        client.post(
            "/api/v1/stock/intake",
            json={"barcode": f"LIST{i:03d}", "qty": 1, "auto_create_sku": True},
        )
    
    response = client.get("/api/v1/skus")
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 3
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_list_skus_pagination(client):
    """Test SKU pagination."""
    # Create 5 SKUs
    for i in range(5):
        client.post(
            "/api/v1/stock/intake",
            json={"barcode": f"PAGE{i:03d}", "qty": 1, "auto_create_sku": True},
        )
    
    # Get first page
    response = client.get("/api/v1/skus?skip=0&limit=2")
    data = response.json()
    assert len(data["items"]) == 2
    
    # Get second page
    response = client.get("/api/v1/skus?skip=2&limit=2")
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_skus_search(client):
    """Test SKU search."""
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "SEARCH_APPLE", "qty": 1, "auto_create_sku": True},
    )
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "SEARCH_BANANA", "qty": 1, "auto_create_sku": True},
    )
    
    response = client.get("/api/v1/skus?search=APPLE")
    data = response.json()
    
    assert len(data["items"]) >= 1
    assert any("APPLE" in item["sku_code"] for item in data["items"])


@pytest.mark.asyncio
async def test_get_sku_detail(client):
    """Test getting SKU details."""
    # Create SKU
    create_response = client.post(
        "/api/v1/stock/intake",
        json={
            "barcode": "DETAIL001",
            "qty": 10,
            "location_code": "WH-D-01",
            "auto_create_sku": True,
        },
    )
    sku_id = create_response.json()["sku_id"]
    
    # Get details
    response = client.get(f"/api/v1/skus/{sku_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["sku_code"] == "DETAIL001"
    assert "barcodes" in data
    assert "stock_levels" in data
    assert len(data["barcodes"]) > 0
    assert len(data["stock_levels"]) > 0


@pytest.mark.asyncio
async def test_get_sku_detail_not_found(client):
    """Test getting details of non-existent SKU."""
    from uuid import uuid4
    
    response = client.get(f"/api/v1/skus/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stock_levels(client):
    """Test getting stock levels."""
    # Create some stock
    client.post(
        "/api/v1/stock/intake",
        json={
            "barcode": "LEVEL001",
            "qty": 25,
            "location_code": "WH-L-01",
            "auto_create_sku": True,
        },
    )
    
    response = client.get("/api/v1/stock/levels")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("sku_code" in item for item in data)
    assert all("on_hand" in item for item in data)


@pytest.mark.asyncio
async def test_get_stock_levels_filter_by_location(client):
    """Test filtering stock levels by location."""
    client.post(
        "/api/v1/stock/intake",
        json={
            "barcode": "FILTER001",
            "qty": 10,
            "location_code": "WH-F-01",
            "auto_create_sku": True,
        },
    )
    
    response = client.get("/api/v1/stock/levels?location_code=WH-F-01")
    data = response.json()
    
    assert len(data) > 0
    assert all(item["location_code"] == "WH-F-01" for item in data)


@pytest.mark.asyncio
async def test_list_movements(client):
    """Test listing stock movements."""
    # Create some movements
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "MOVE001", "qty": 10, "movement_type": "IN", "auto_create_sku": True},
    )
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "MOVE001", "qty": -5, "movement_type": "OUT", "auto_create_sku": False},
    )
    
    response = client.get("/api/v1/stock/movements")
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_list_movements_filter_by_type(client):
    """Test filtering movements by type."""
    # Create mixed movements
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "TYPE001", "qty": 10, "movement_type": "IN", "auto_create_sku": True},
    )
    client.post(
        "/api/v1/stock/intake",
        json={"barcode": "TYPE001", "qty": -3, "movement_type": "OUT", "auto_create_sku": False},
    )
    
    response = client.get("/api/v1/stock/movements?movement_type=IN")
    data = response.json()
    
    assert all(item["movement_type"] == "IN" for item in data["items"])


@pytest.mark.asyncio
async def test_api_validation_missing_barcode(client):
    """Test API validation for missing required fields."""
    response = client.post(
        "/api/v1/stock/intake",
        json={"qty": 5},  # Missing barcode
    )
    
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_api_validation_invalid_qty(client):
    """Test API validation for invalid quantity."""
    response = client.post(
        "/api/v1/stock/intake",
        json={"barcode": "TEST", "qty": "not_a_number"},
    )
    
    assert response.status_code == 422
