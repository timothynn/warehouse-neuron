-- Migration: Add performance indexes
-- Created: 2025-11-08
-- Description: Add indexes on frequently queried columns for improved performance

-- Stock movements indexes
-- Index on created_at for date range queries and sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_created_at 
    ON stock_movements(created_at DESC);

-- Index on movement type for filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_movement_type 
    ON stock_movements(movement_type);

-- Index on created_by for user activity tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_created_by 
    ON stock_movements(created_by);

-- Composite index for common SKU+location queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_sku_location 
    ON stock_movements(sku_id, location_id);

-- Composite index for date+location filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_movements_by_date_location 
    ON stock_movements(created_at DESC, location_id);

-- Stock ledger indexes
-- Partial index for non-zero stock levels
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_ledger_on_hand 
    ON stock_ledger(on_hand) 
    WHERE on_hand > 0;

-- Index on updated_at for recent changes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_ledger_updated 
    ON stock_ledger(updated_at DESC);

-- Composite index for active stock by SKU and location
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ledger_sku_location_active 
    ON stock_ledger(sku_id, location_id) 
    WHERE on_hand > 0;

-- SKUs indexes
-- Full-text search index on title
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_title_search 
    ON skus USING gin(to_tsvector('english', title));

-- Partial index for active SKUs only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_active 
    ON skus(is_active) 
    WHERE is_active = true;

-- Index on created_at for recent SKUs
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_created_at 
    ON skus(created_at DESC);

-- SKU barcodes indexes
-- Index on barcode for fast lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sku_barcodes_barcode 
    ON sku_barcodes(barcode);

-- Composite index for barcode+SKU queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sku_barcodes_barcode_sku 
    ON sku_barcodes(barcode, sku_id);

-- Locations indexes
-- Index on code for fast lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_locations_code 
    ON locations(code);

-- Index on name for search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_locations_name 
    ON locations(name);

-- Add comments for documentation
COMMENT ON INDEX idx_stock_movements_created_at IS 'Improves date range queries and sorting';
COMMENT ON INDEX idx_stock_movements_movement_type IS 'Speeds up filtering by movement type (IN/OUT/ADJUST)';
COMMENT ON INDEX idx_stock_movements_sku_location IS 'Optimizes queries for specific SKU+location combinations';
COMMENT ON INDEX idx_stock_ledger_on_hand IS 'Partial index for non-zero stock levels only';
COMMENT ON INDEX idx_skus_title_search IS 'Full-text search on SKU titles';
COMMENT ON INDEX idx_skus_active IS 'Partial index for active SKUs only';

-- Analyze tables to update statistics after index creation
ANALYZE stock_movements;
ANALYZE stock_ledger;
ANALYZE skus;
ANALYZE sku_barcodes;
ANALYZE locations;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Performance indexes created successfully!';
    RAISE NOTICE 'Tables analyzed and statistics updated.';
END $$;
