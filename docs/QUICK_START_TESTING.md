# Phase A - Quick Start & Testing Guide

This guide will get you from zero to fully testing the Warehouse Neuron backend in under 10 minutes.

---

## 🚀 Prerequisites Check

Before starting, ensure you have:

```bash
# Check Nix is installed
nix --version

# Check direnv is installed
direnv version

# Check Docker/Podman is running
docker ps
```

If any are missing, see [README.md](../README.md#prerequisites) for installation instructions.

---

## ⚡ 5-Minute Setup

### Step 1: Clone & Enter Directory (30 seconds)

```bash
cd /home/tim/dev/warehouse-neuron
direnv allow
```

You should see:
```
direnv: loading ~/dev/warehouse-neuron/.envrc
direnv: using flake
```

### Step 2: Start Services (2 minutes)

```bash
docker compose up -d
```

Wait for all containers to start. Check with:
```bash
docker ps
```

You should see 3 containers running:
- `warehouse-neuron_postgres_1`
- `warehouse-neuron_redis_1`
- `warehouse-neuron_backend_1`

### Step 3: Initialize Database (30 seconds)

```bash
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

Verify tables created:
```bash
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c '\dt'
```

Expected output:
```
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+---------
 public | locations       | table | wn_user
 public | skus            | table | wn_user
 public | sku_barcodes    | table | wn_user
 public | stock_ledger    | table | wn_user
 public | stock_movements | table | wn_user
```

### Step 4: Test API (30 seconds)

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

**✅ Setup Complete! Total time: ~3 minutes**

---

## 🧪 Testing Scenarios

### Scenario 1: Receive New Product

**Story:** A new product arrives at the warehouse receiving dock. Scan the barcode to create a new SKU and record the receipt.

```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "WIDGET-12345",
    "qty": 50,
    "location_code": "RECV-01",
    "movement_type": "IN",
    "auto_create_sku": true,
    "created_by": "receiver@warehouse.com"
  }'
```

**Expected Response:**
```json
{
  "movement_id": "uuid-here",
  "sku_id": "uuid-here",
  "sku_code": "WIDGET-12345",
  "on_hand": 50
}
```

**Verify in Database:**
```bash
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c "
SELECT s.sku_code, l.code, sl.on_hand 
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
JOIN locations l ON sl.location_id = l.id
WHERE s.sku_code = 'WIDGET-12345';"
```

---

### Scenario 2: Transfer to Main Warehouse

**Story:** Product is verified and ready to be moved from receiving to main warehouse storage.

```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "WIDGET-12345",
    "qty": 50,
    "location_code": "WH-A-01",
    "movement_type": "TRANSFER",
    "created_by": "stocker@warehouse.com"
  }'
```

**Verify Stock Levels:**
```bash
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c "
SELECT l.code as location, sl.on_hand 
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
JOIN locations l ON sl.location_id = l.id
WHERE s.sku_code = 'WIDGET-12345';"
```

Expected: 50 units at `WH-A-01`

---

### Scenario 3: Additional Receipt

**Story:** Another shipment of the same product arrives.

```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "WIDGET-12345",
    "qty": 25,
    "location_code": "WH-A-01",
    "movement_type": "IN",
    "created_by": "receiver@warehouse.com"
  }'
```

**Expected:** `on_hand` increases to 75

---

### Scenario 4: Barcode Mapping

**Story:** Same product has multiple barcodes (UPC, EAN, internal code).

```bash
# Add with different barcode (simulated via direct DB insert for now)
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c "
INSERT INTO sku_barcodes (sku_id, barcode)
SELECT id, 'UPC-999888777' FROM skus WHERE sku_code = 'WIDGET-12345';"

# Now scan with the new barcode
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "UPC-999888777",
    "qty": 10,
    "location_code": "WH-A-01",
    "movement_type": "IN",
    "created_by": "receiver@warehouse.com"
  }'
```

**Expected:** Stock increases for the same SKU

---

### Scenario 5: Stock Adjustment (Cycle Count)

**Story:** Physical count reveals 2 units are damaged and must be written off.

```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "WIDGET-12345",
    "qty": -2,
    "location_code": "WH-A-01",
    "movement_type": "ADJUSTMENT",
    "created_by": "manager@warehouse.com"
  }'
```

**Verify Movement History:**
```bash
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c "
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
WHERE s.sku_code = 'WIDGET-12345'
ORDER BY sm.created_at DESC;"
```

You should see all movements in chronological order.

---

### Scenario 6: Error Handling

**Story:** Try to add stock for a barcode that doesn't exist without auto-create.

```bash
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "UNKNOWN-BARCODE",
    "qty": 10,
    "auto_create_sku": false,
    "created_by": "test@warehouse.com"
  }'
```

**Expected Response (404 Error):**
```json
{
  "detail": "SKU not found for barcode. Set auto_create_sku to true to create a new SKU."
}
```

---

## 🔍 Exploring the System

### View API Documentation

Open in browser:
```
http://localhost:8000/docs
```

This provides:
- Interactive API testing
- Request/response schemas
- Try-it-out functionality

### Connect with DBeaver

1. Open DBeaver
2. New Connection → PostgreSQL
3. Settings:
   - Host: `localhost`
   - Port: `5434`
   - Database: `warehouse_neuron`
   - Username: `wn_user`
   - Password: `wn_pass`
4. Test Connection → Finish

Now you can:
- Browse tables visually
- Run custom queries
- View relationships
- Export data

### Monitor Redis Events

```bash
# Connect to Redis
docker exec -it warehouse-neuron_redis_1 redis-cli

# Monitor all commands
MONITOR

# View stock events stream
XLEN stock_events
XREAD COUNT 10 STREAMS stock_events 0
```

---

## 📊 Useful Database Queries

### Current Stock Summary
```sql
SELECT 
    s.sku_code,
    s.title,
    l.code as location,
    sl.on_hand,
    sl.reserved,
    sl.updated_at
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
LEFT JOIN locations l ON sl.location_id = l.id
ORDER BY sl.updated_at DESC;
```

### Recent Activity (Last 24 hours)
```sql
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
WHERE sm.created_at > NOW() - INTERVAL '24 hours'
ORDER BY sm.created_at DESC;
```

### All Barcodes for a SKU
```sql
SELECT 
    s.sku_code,
    s.title,
    sb.barcode,
    sb.created_at
FROM sku_barcodes sb
JOIN skus s ON sb.sku_id = s.id
WHERE s.sku_code = 'WIDGET-12345';
```

### Locations with Stock
```sql
SELECT 
    l.code,
    l.name,
    COUNT(DISTINCT sl.sku_id) as unique_skus,
    SUM(sl.on_hand) as total_units
FROM locations l
LEFT JOIN stock_ledger sl ON l.id = sl.location_id
GROUP BY l.id, l.code, l.name
ORDER BY total_units DESC;
```

---

## 🧹 Cleanup & Reset

### Reset Database Only
```bash
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d postgres -c "
DROP DATABASE warehouse_neuron;
CREATE DATABASE warehouse_neuron;"

docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

### Reset All Services
```bash
docker compose down -v
docker compose up -d
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check what's running
docker ps -a

# View logs
docker compose logs backend
docker compose logs postgres

# Check for port conflicts
netstat -tuln | grep -E '8000|5434|6379'
```

### Database Connection Failed

```bash
# Test from inside container
docker exec warehouse-neuron_postgres_1 pg_isready -U wn_user

# Test from host
psql -h localhost -p 5434 -U wn_user -d warehouse_neuron
```

### API Returns 500 Error

```bash
# View backend logs in real-time
docker compose logs -f backend

# Check database connectivity from backend
docker exec -it warehouse-neuron_backend_1 env | grep DATABASE_URL
```

### Redis Not Working

```bash
# Test Redis
docker exec -it warehouse-neuron_redis_1 redis-cli PING
# Expected: PONG

# Check backend can reach Redis
docker exec -it warehouse-neuron_backend_1 env | grep REDIS_URL
```

---

## 📚 Next Steps

After testing Phase A backend:

1. **Add More Endpoints**
   - GET `/api/v1/skus` - List all SKUs
   - GET `/api/v1/skus/{id}` - Get SKU details
   - GET `/api/v1/stock/levels` - Get stock by location
   - GET `/api/v1/stock/movements` - List movements with filters

2. **Implement Authentication**
   - User registration
   - Login with JWT tokens
   - Protected routes

3. **Start Frontend Development**
   - Initialize Flutter project
   - Build scanning screen
   - Connect to API

4. **Add Testing**
   - Unit tests for CRUD operations
   - Integration tests for API
   - Test coverage reporting

---

## 📖 Documentation

For more details, see:
- [README.md](../README.md) - Project overview
- [API_GUIDE.md](./API_GUIDE.md) - Complete API documentation
- [DATABASE_SETUP.md](./DATABASE_SETUP.md) - Database reference
- [PHASE_A_CHECKLIST.md](./PHASE_A_CHECKLIST.md) - Full Phase A tasks

---

**Happy Testing! 🎉**

*If you find any issues or have questions, check the troubleshooting section or review the logs.*
