# Database Setup Guide

## Overview

Warehouse Neuron uses PostgreSQL 15 with SQLAlchemy ORM for data persistence. This guide covers database initialization, migrations, and maintenance.

---

## Quick Start

### 1. Start Database Container

```bash
docker compose up -d postgres
```

### 2. Run Initial Migration

```bash
# Connect to the database
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron

# Run the init script
\i /docker-entrypoint-initdb.d/0001_init.sql

# Or from host:
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

### 3. Verify Tables Created

```sql
-- List all tables
\dt

-- Expected output:
--  Schema |      Name       | Type  |  Owner
-- --------+-----------------+-------+---------
--  public | locations       | table | wn_user
--  public | skus            | table | wn_user
--  public | sku_barcodes    | table | wn_user
--  public | stock_ledger    | table | wn_user
--  public | stock_movements | table | wn_user
```

---

## Schema Overview

### Database Design Principles

- **UUID Primary Keys:** All tables use UUID for globally unique identifiers
- **Timestamps:** All tables track `created_at` and `updated_at`
- **Soft Deletes:** Use `deleted_at` column instead of hard deletes (future)
- **Audit Trail:** `stock_movements` provides complete transaction history
- **Normalization:** Proper foreign key relationships prevent data anomalies

---

## Table Schemas

### 1. Locations Table

Stores warehouse locations (zones, aisles, bins).

```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Track physical locations in the warehouse  
**Key Field:** `code` (e.g., "WH-A-01-B" for Warehouse A, Aisle 01, Bin B)

**Example Data:**

```sql
INSERT INTO locations (code, name) VALUES
    ('RECV-01', 'Receiving Dock 1'),
    ('WH-A-01', 'Main Warehouse - Aisle A1'),
    ('WH-B-05', 'Main Warehouse - Aisle B5'),
    ('SHIP-01', 'Shipping Dock 1'),
    ('HOLD-01', 'Quality Hold Area');
```

---

### 2. SKUs Table

Stores Stock Keeping Unit (product) information.

```sql
CREATE TABLE skus (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Master product catalog  
**Key Field:** `sku_code` (internal product identifier)

**Example Data:**

```sql
INSERT INTO skus (sku_code, title, description) VALUES
    ('WIDGET-001', 'Standard Widget', 'Basic widget for general use'),
    ('GADGET-001', 'Premium Gadget', 'High-end gadget with advanced features'),
    ('SPROCKET-001', 'Industrial Sprocket', '10-inch industrial grade sprocket');
```

---

### 3. SKU Barcodes Table

Maps multiple barcodes to SKUs (many-to-one relationship).

```sql
CREATE TABLE sku_barcodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID NOT NULL REFERENCES skus(id) ON DELETE CASCADE,
    barcode VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(barcode)
);
```

**Purpose:** Allow multiple barcodes per product (UPC, EAN, internal codes)  
**Key Field:** `barcode` (scanned code)

**Example Data:**

```sql
INSERT INTO sku_barcodes (sku_id, barcode) VALUES
    ((SELECT id FROM skus WHERE sku_code = 'WIDGET-001'), '123456789012'),
    ((SELECT id FROM skus WHERE sku_code = 'WIDGET-001'), 'WGT001'),
    ((SELECT id FROM skus WHERE sku_code = 'GADGET-001'), '987654321098');
```

---

### 4. Stock Ledger Table

Tracks current inventory levels per SKU per location.

```sql
CREATE TABLE stock_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID NOT NULL REFERENCES skus(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
    on_hand INTEGER DEFAULT 0,
    reserved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sku_id, location_id)
);
```

**Purpose:** Real-time inventory snapshot  
**Key Fields:**
- `on_hand`: Physical quantity available
- `reserved`: Quantity allocated but not yet shipped

**Indexes:**

```sql
CREATE INDEX idx_stock_ledger_sku ON stock_ledger(sku_id);
CREATE INDEX idx_stock_ledger_location ON stock_ledger(location_id);
```

**Example Data:**

```sql
INSERT INTO stock_ledger (sku_id, location_id, on_hand, reserved) VALUES
    ((SELECT id FROM skus WHERE sku_code = 'WIDGET-001'),
     (SELECT id FROM locations WHERE code = 'WH-A-01'),
     100, 25),
    ((SELECT id FROM skus WHERE sku_code = 'GADGET-001'),
     (SELECT id FROM locations WHERE code = 'WH-B-05'),
     50, 0);
```

---

### 5. Stock Movements Table

Immutable audit log of all inventory transactions.

```sql
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id UUID NOT NULL REFERENCES skus(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
    qty INTEGER NOT NULL,
    movement_type VARCHAR(50),
    created_by VARCHAR(200),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Complete transaction history for auditing  
**Key Fields:**
- `qty`: Change in quantity (positive = increase, negative = decrease)
- `movement_type`: IN, OUT, TRANSFER, ADJUSTMENT, etc.
- `metadata`: Additional context as JSON

**Indexes:**

```sql
CREATE INDEX idx_stock_movements_sku ON stock_movements(sku_id);
CREATE INDEX idx_stock_movements_created ON stock_movements(created_at DESC);
```

**Example Data:**

```sql
INSERT INTO stock_movements (sku_id, location_id, qty, movement_type, created_by) VALUES
    ((SELECT id FROM skus WHERE sku_code = 'WIDGET-001'),
     (SELECT id FROM locations WHERE code = 'RECV-01'),
     100, 'IN', 'receiver@warehouse.com'),
    ((SELECT id FROM skus WHERE sku_code = 'WIDGET-001'),
     (SELECT id FROM locations WHERE code = 'WH-A-01'),
     100, 'TRANSFER', 'stocker@warehouse.com');
```

---

## Database Connection

### Connection String Format

```
postgresql+asyncpg://username:password@host:port/database
```

### Development Environment

```bash
# Environment variables (already set in docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://wn_user:wn_pass@postgres:5432/warehouse_neuron
```

### From Host Machine

```bash
# For tools like DBeaver or psql
Host: localhost
Port: 5434
Database: warehouse_neuron
Username: wn_user
Password: wn_pass
```

**Note:** External port is `5434`, internal Docker network uses `5432`

---

## Database Operations

### Using psql (PostgreSQL CLI)

#### Connect to Database

```bash
# From host
psql -h localhost -p 5434 -U wn_user -d warehouse_neuron

# From Docker container
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron
```

#### Common Commands

```sql
-- List all databases
\l

-- List all tables
\dt

-- Describe table structure
\d skus
\d+ skus  -- With more details

-- List all indexes
\di

-- List all foreign keys
SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Show table sizes
SELECT 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Exit
\q
```

---

## Database Maintenance

### Backup Database

```bash
# Full database backup
docker exec warehouse-neuron_postgres_1 pg_dump -U wn_user warehouse_neuron > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker exec warehouse-neuron_postgres_1 pg_dump -U wn_user warehouse_neuron | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Schema only (no data)
docker exec warehouse-neuron_postgres_1 pg_dump -U wn_user --schema-only warehouse_neuron > schema_backup.sql

# Data only (no schema)
docker exec warehouse-neuron_postgres_1 pg_dump -U wn_user --data-only warehouse_neuron > data_backup.sql
```

### Restore Database

```bash
# From SQL file
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user warehouse_neuron < backup.sql

# From compressed file
gunzip -c backup.sql.gz | docker exec -i warehouse-neuron_postgres_1 psql -U wn_user warehouse_neuron
```

### Reset Database (Development Only)

```bash
# Drop and recreate database
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d postgres -c "DROP DATABASE warehouse_neuron;"
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d postgres -c "CREATE DATABASE warehouse_neuron;"
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

---

## Alembic Migrations (Future)

### Setup Alembic

```bash
cd services/backend
alembic init alembic
```

### Configure Alembic

Edit `alembic.ini`:

```ini
sqlalchemy.url = postgresql+asyncpg://wn_user:wn_pass@localhost:5434/warehouse_neuron
```

### Create Migration

```bash
# Auto-generate migration from models
alembic revision --autogenerate -m "description"

# Manual migration
alembic revision -m "description"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

## Performance Optimization

### Recommended Indexes

```sql
-- Stock ledger lookups
CREATE INDEX idx_stock_ledger_sku ON stock_ledger(sku_id);
CREATE INDEX idx_stock_ledger_location ON stock_ledger(location_id);
CREATE INDEX idx_stock_ledger_updated ON stock_ledger(updated_at DESC);

-- Stock movements queries
CREATE INDEX idx_stock_movements_sku ON stock_movements(sku_id);
CREATE INDEX idx_stock_movements_location ON stock_movements(location_id);
CREATE INDEX idx_stock_movements_created ON stock_movements(created_at DESC);
CREATE INDEX idx_stock_movements_type ON stock_movements(movement_type);

-- Barcode lookups (most critical)
CREATE INDEX idx_sku_barcodes_barcode ON sku_barcodes(barcode);
CREATE INDEX idx_sku_barcodes_sku ON sku_barcodes(sku_id);

-- Location lookups
CREATE INDEX idx_locations_code ON locations(code);
```

### Analyze Query Performance

```sql
-- Enable timing
\timing on

-- Explain query plan
EXPLAIN ANALYZE
SELECT s.sku_code, sl.on_hand 
FROM stock_ledger sl
JOIN skus s ON sl.sku_id = s.id
WHERE sl.location_id = 'some-uuid';

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Vacuum and Analyze

```sql
-- Update statistics
ANALYZE;

-- Reclaim space
VACUUM;

-- Full vacuum (requires downtime)
VACUUM FULL;

-- Auto-vacuum settings
SHOW autovacuum;
```

---

## Monitoring

### Database Size

```sql
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'warehouse_neuron';
```

### Active Connections

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'warehouse_neuron';
```

### Lock Information

```sql
SELECT * FROM pg_locks WHERE database = (SELECT oid FROM pg_database WHERE datname = 'warehouse_neuron');
```

### Table Statistics

```sql
SELECT schemaname, tablename, n_live_tup, n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

---

## Troubleshooting

### Cannot Connect to Database

**Check container is running:**

```bash
docker ps | grep postgres
```

**Check logs:**

```bash
docker logs warehouse-neuron_postgres_1
```

**Test connection:**

```bash
docker exec warehouse-neuron_postgres_1 pg_isready -U wn_user
```

### Tables Not Created

**Manually run init script:**

```bash
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql
```

### Permission Denied

**Grant permissions:**

```sql
GRANT ALL PRIVILEGES ON DATABASE warehouse_neuron TO wn_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wn_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wn_user;
```

### Disk Space Issues

**Check database size:**

```sql
SELECT pg_database_size('warehouse_neuron');
```

**Clean up:**

```sql
VACUUM FULL;
REINDEX DATABASE warehouse_neuron;
```

---

## Security Best Practices

### Production Recommendations

1. **Change Default Password**
   ```sql
   ALTER USER wn_user WITH PASSWORD 'strong_random_password';
   ```

2. **Use SSL/TLS**
   ```ini
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
   ```

3. **Restrict Network Access**
   ```yaml
   # docker-compose.yml
   postgres:
     ports:
       - "127.0.0.1:5434:5432"  # Bind to localhost only
   ```

4. **Read-Only User for Reporting**
   ```sql
   CREATE USER reporter WITH PASSWORD 'reporter_password';
   GRANT CONNECT ON DATABASE warehouse_neuron TO reporter;
   GRANT USAGE ON SCHEMA public TO reporter;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO reporter;
   ```

5. **Regular Backups**
   ```bash
   # Daily backup cron job
   0 2 * * * /path/to/backup_script.sh
   ```

---

## Next Steps

1. **Run Initial Migration:** Apply `0001_init.sql` to create tables
2. **Verify Schema:** Check tables exist with `\dt`
3. **Seed Sample Data:** Insert test locations and SKUs
4. **Test API:** Use Postman to create stock movements
5. **Monitor Performance:** Check query times and optimize as needed

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [DBeaver Documentation](https://dbeaver.com/docs/)

---

**Last Updated:** November 8, 2025  
**Database Version:** PostgreSQL 15  
**Schema Version:** 0001_init.sql
