# Warehouse Neuron API Documentation & Testing Guide

## Phase A - Core Functionality

### Overview

Phase A implements the foundational inventory tracking system with barcode scanning, SKU management, and stock movements.

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Root Endpoint
**GET** `/`

Returns API status information.

**Response:**
```json
{
  "message": "Warehouse Neuron API",
  "status": "running"
}
```

---

### 2. Health Check
**GET** `/health`

Returns service health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 3. Stock Intake (Main Feature)
**POST** `/api/v1/stock/intake`

Process a stock intake event from barcode scanning.

**Request Body:**
```json
{
  "barcode": "1234567890123",
  "qty": 1,
  "location_code": "A-01-B",
  "movement_type": "IN",
  "auto_create_sku": true,
  "created_by": "john.doe@example.com"
}
```

**Request Fields:**
- `barcode` (string, required): The scanned barcode
- `qty` (integer, optional): Quantity to add (default: 1)
- `location_code` (string, optional): Location code for the stock
- `movement_type` (string, optional): Type of movement (default: "IN")
- `auto_create_sku` (boolean, optional): Auto-create SKU if not found (default: false)
- `created_by` (string, optional): User who performed the action

**Response (Success - 200):**
```json
{
  "movement_id": "123e4567-e89b-12d3-a456-426614174000",
  "sku_id": "123e4567-e89b-12d3-a456-426614174001",
  "sku_code": "1234567890123",
  "on_hand": 5
}
```

**Response (Error - 404):**
```json
{
  "detail": "SKU not found for barcode. Set auto_create_sku to true to create a new SKU."
}
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

### Swagger UI (Recommended)
```
http://localhost:8000/docs
```
- Interactive interface to test all endpoints
- See request/response schemas
- Execute API calls directly from browser

### ReDoc (Alternative)
```
http://localhost:8000/redoc
```
- Clean, professional documentation view
- Better for reading and understanding API structure

---

## Database Connection with DBeaver

### Step 1: Install DBeaver
Download from: https://dbeaver.io/download/

### Step 2: Create New Connection

1. Open DBeaver
2. Click **Database** → **New Database Connection**
3. Select **PostgreSQL**
4. Click **Next**

### Step 3: Configure Connection

**Connection Settings:**
```
Host: localhost
Port: 5434
Database: warehouse_neuron
Username: wn_user
Password: wn_pass
```

**Connection Details:**
- **Connection Name:** Warehouse Neuron
- **Connect at startup:** ✓ (optional)

### Step 4: Test & Connect

1. Click **Test Connection**
2. If successful, click **Finish**
3. Expand the connection in the Database Navigator

### Step 5: Explore Database

**Tables to explore:**
- `locations` - Warehouse locations
- `skus` - Stock Keeping Units
- `sku_barcodes` - Barcode mappings
- `stock_ledger` - Current inventory levels
- `stock_movements` - All stock transactions

**Sample Queries:**

```sql
-- View all SKUs
SELECT * FROM skus ORDER BY created_at DESC LIMIT 10;

-- View current stock levels
SELECT 
    s.sku_code,
    l.code as location,
    sl.on_hand,
    sl.reserved
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
LEFT JOIN locations l ON sl.location_id = l.id;

-- View recent stock movements
SELECT 
    sm.created_at,
    s.sku_code,
    l.code as location,
    sm.qty,
    sm.movement_type,
    sm.created_by
FROM stock_movements sm
JOIN skus s ON sm.sku_id = s.id
LEFT JOIN locations l ON sm.location_id = l.id
ORDER BY sm.created_at DESC
LIMIT 20;

-- Check barcode mappings
SELECT 
    sb.barcode,
    s.sku_code,
    s.title
FROM sku_barcodes sb
JOIN skus s ON sb.sku_id = s.id;
```

---

## Testing with Postman

### Step 1: Install Postman
Download from: https://www.postman.com/downloads/

### Step 2: Create New Collection

1. Open Postman
2. Click **New** → **Collection**
3. Name it "Warehouse Neuron API"

### Step 3: Add Requests

#### Test 1: Health Check

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/health`
- Click **Send**

**Expected Response:**
```json
{
  "status": "healthy"
}
```

#### Test 2: Stock Intake (Auto-Create SKU)

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/v1/stock/intake`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "barcode": "TEST-001",
  "qty": 10,
  "location_code": "WH-A-01",
  "movement_type": "IN",
  "auto_create_sku": true,
  "created_by": "test_user"
}
```

**Expected Response:**
```json
{
  "movement_id": "uuid-here",
  "sku_id": "uuid-here",
  "sku_code": "TEST-001",
  "on_hand": 10
}
```

#### Test 3: Stock Intake (Existing SKU)

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/v1/stock/intake`
- Body:

```json
{
  "barcode": "TEST-001",
  "qty": 5,
  "location_code": "WH-A-01",
  "movement_type": "IN",
  "created_by": "test_user"
}
```

**Expected Response:**
```json
{
  "movement_id": "uuid-here",
  "sku_id": "uuid-here",
  "sku_code": "TEST-001",
  "on_hand": 15
}
```

#### Test 4: Stock Intake (Error Case)

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/v1/stock/intake`
- Body:

```json
{
  "barcode": "UNKNOWN-001",
  "qty": 5,
  "auto_create_sku": false
}
```

**Expected Response (404 Error):**
```json
{
  "detail": "SKU not found for barcode. Set auto_create_sku to true to create a new SKU."
}
```

### Step 4: Save Collection

1. Click **Save** on each request
2. Organize requests in folders (e.g., "Health", "Stock Operations")

### Step 5: Export Collection (Optional)

1. Right-click collection
2. **Export**
3. Choose **Collection v2.1**
4. Save as `warehouse-neuron-api.postman_collection.json`

---

## Testing Flow: Complete Scenario

### Scenario: Receiving New Inventory

**Step 1: Check API Health**
```bash
curl http://localhost:8000/health
```

**Step 2: Scan First Item (Auto-Create)**
```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "8901234567890",
    "qty": 50,
    "location_code": "RECV-01",
    "movement_type": "IN",
    "auto_create_sku": true,
    "created_by": "receiver@warehouse.com"
  }'
```

**Step 3: Verify in Database (DBeaver)**
```sql
SELECT * FROM skus WHERE sku_code = '8901234567890';
SELECT * FROM stock_movements ORDER BY created_at DESC LIMIT 1;
SELECT * FROM stock_ledger WHERE location_id = (
    SELECT id FROM locations WHERE code = 'RECV-01'
);
```

**Step 4: Move to Main Warehouse**
```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "8901234567890",
    "qty": 50,
    "location_code": "WH-A-05",
    "movement_type": "TRANSFER",
    "created_by": "warehouse@warehouse.com"
  }'
```

**Step 5: Check Final Stock Levels**
```sql
SELECT 
    s.sku_code,
    l.code as location,
    sl.on_hand,
    sl.updated_at
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
JOIN locations l ON sl.location_id = l.id
WHERE s.sku_code = '8901234567890';
```

---

## Web Access (Coming Soon)

### Web Dashboard
- **URL:** `http://localhost:3000` (Phase A - Not yet implemented)
- **Features:**
  - View all SKUs
  - Search inventory
  - View stock movements
  - Location management

**Current Status:** Backend API ready, Flutter web app pending.

---

## Mobile Access (Coming Soon)

### Flutter Mobile App
- **Platform:** iOS & Android
- **Features:**
  - Camera barcode scanning
  - Quick stock intake
  - Offline queue
  - Real-time sync

**Current Status:** Backend API ready, Flutter app pending.

---

## Desktop Access (Coming Soon)

### Tauri Desktop App
- **Platform:** Windows, macOS, Linux
- **Features:**
  - Full dashboard functionality
  - Bulk operations
  - Advanced reporting
  - USB barcode scanner support

**Current Status:** Backend API ready, Tauri wrapper pending.

---

## Redis Monitoring

### Access Redis CLI
```bash
docker exec -it warehouse-neuron_redis_1 redis-cli
```

### Monitor Events
```redis
MONITOR
```

### Check Stock Events Stream
```redis
XLEN stock_events
XREAD COUNT 10 STREAMS stock_events 0
```

---

## Troubleshooting

### API Not Responding

**Check container status:**
```bash
docker ps
```

**Check backend logs:**
```bash
docker logs warehouse-neuron_backend_1
```

**Restart services:**
```bash
docker compose restart
```

### Database Connection Failed

**Verify PostgreSQL is running:**
```bash
docker ps | grep postgres
```

**Check port availability:**
```bash
netstat -tuln | grep 5434
```

**Test connection:**
```bash
psql -h localhost -p 5434 -U wn_user -d warehouse_neuron
```
Password: `wn_pass`

### Cannot Create New SKU

**Common causes:**
- `auto_create_sku` is set to `false`
- Barcode already exists but mapped to different SKU

**Solution:**
```json
{
  "barcode": "your-barcode",
  "auto_create_sku": true
}
```

---

## Next Steps for Phase A

### Backend Improvements
- [ ] Add pagination to list endpoints
- [ ] Add GET endpoints for SKUs and movements
- [ ] Add search/filter capabilities
- [ ] Add authentication
- [ ] Add comprehensive error handling
- [ ] Add request validation
- [ ] Add API rate limiting

### Database
- [ ] Run initial migration (0001_init.sql)
- [ ] Add indexes for performance
- [ ] Add database backup strategy
- [ ] Add audit logging

### Testing
- [ ] Unit tests for CRUD operations
- [ ] Integration tests for API endpoints
- [ ] Load testing
- [ ] Security testing

### Documentation
- [ ] OpenAPI schema completion
- [ ] Deployment guide
- [ ] Development workflow guide
- [ ] Architecture documentation

---

## Support & Resources

- **API Documentation:** http://localhost:8000/docs
- **GitHub Repository:** https://github.com/timothynn/warehouse-neuron
- **Issues:** https://github.com/timothynn/warehouse-neuron/issues

---

**Last Updated:** November 8, 2025  
**Phase:** A - Foundations (Backend Complete)
