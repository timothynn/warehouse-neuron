-- Database Performance Indexes Migration
-- Migration: 0003_indexes.sql
-- Description: Add indexes for frequently queried columns to improve performance

-- ============================================================================
-- Stock Movements Indexes
-- ============================================================================

-- Index for querying recent movements (most common query)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_created_at 
    ON stock_movements(created_at DESC);

-- Index for filtering by movement type
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_movement_type 
    ON stock_movements(movement_type);

-- Index for filtering by creator
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_created_by 
    ON stock_movements(created_by);

-- Composite index for common queries (SKU + Location)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_movements_sku_location 
    ON stock_movements(sku_id, location_id);

-- Composite index for date range queries by location
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_movements_by_date_location 
    ON stock_movements(created_at DESC, location_id);

-- ============================================================================
-- Stock Ledger Indexes
-- ============================================================================

-- Partial index for items with stock (most common query)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_ledger_on_hand 
    ON stock_ledger(on_hand) 
    WHERE on_hand > 0;

-- Index for recently updated stock
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_ledger_updated 
    ON stock_ledger(updated_at DESC);

-- Composite index for active stock by SKU and location
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ledger_sku_location_active 
    ON stock_ledger(sku_id, location_id) 
    WHERE on_hand > 0;

-- Index for reserved stock queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_ledger_reserved 
    ON stock_ledger(reserved) 
    WHERE reserved > 0;

-- ============================================================================
-- SKUs Indexes
-- ============================================================================

-- Full-text search index on SKU title (PostgreSQL GIN index)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_title_search 
    ON skus USING gin(to_tsvector('english', title));

-- Partial index for active SKUs
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_active 
    ON skus(is_active) 
    WHERE is_active = true;

-- Index for SKU code lookups (case-insensitive)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skus_code_lower 
    ON skus(LOWER(sku_code));

-- ============================================================================
-- SKU Barcodes Indexes
-- ============================================================================

-- Index for barcode lookups (most common query)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sku_barcodes_barcode 
    ON sku_barcodes(barcode);

-- Composite index for barcode validation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sku_barcodes_sku_barcode 
    ON sku_barcodes(sku_id, barcode);

-- ============================================================================
-- Locations Indexes
-- ============================================================================

-- Index for location code lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_locations_code 
    ON locations(code);

-- Partial index for active locations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_locations_active 
    ON locations(is_active) 
    WHERE is_active = true;

-- ============================================================================
-- Auth Tables Indexes (if auth is enabled)
-- ============================================================================

-- Users table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username 
    ON users(username);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email 
    ON users(email);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role 
    ON users(role);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active 
    ON users(is_active) 
    WHERE is_active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_manager 
    ON users(manager_id) 
    WHERE manager_id IS NOT NULL;

-- Refresh tokens indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_refresh_tokens_user 
    ON refresh_tokens(user_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_refresh_tokens_expires 
    ON refresh_tokens(expires_at) 
    WHERE revoked_at IS NULL;

-- Audit log indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_user 
    ON audit_log(user_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_action 
    ON audit_log(action);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_created 
    ON audit_log(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_log_resource 
    ON audit_log(resource_type, resource_id);

-- ============================================================================
-- Verification
-- ============================================================================

-- Query to check index usage
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan as index_scans,
--     idx_tup_read as tuples_read,
--     idx_tup_fetch as tuples_fetched
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
-- ORDER BY idx_scan DESC;

COMMENT ON INDEX idx_stock_movements_created_at IS 'Index for querying recent stock movements';
COMMENT ON INDEX idx_stock_ledger_on_hand IS 'Partial index for items with available stock';
COMMENT ON INDEX idx_skus_title_search IS 'Full-text search index for SKU titles';
COMMENT ON INDEX idx_sku_barcodes_barcode IS 'Index for fast barcode lookups';
