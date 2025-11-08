-- 0001_init.sql


CREATE TABLE IF NOT EXISTS locations (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
code TEXT NOT NULL UNIQUE,
name TEXT
);


CREATE TABLE IF NOT EXISTS skus (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
sku_code TEXT NOT NULL UNIQUE,
title TEXT,
description TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


CREATE TABLE IF NOT EXISTS sku_barcodes (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
barcode TEXT NOT NULL UNIQUE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


CREATE TABLE IF NOT EXISTS stock_ledger (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
on_hand BIGINT DEFAULT 0,
reserved BIGINT DEFAULT 0,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
UNIQUE (sku_id, location_id)
);


CREATE TABLE IF NOT EXISTS stock_movements (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
location_id UUID REFERENCES locations(id) ON DELETE SET NULL,
qty BIGINT NOT NULL,
movement_type TEXT NOT NULL, -- IN, OUT, ADJUSTMENT
barcode TEXT,
batch TEXT,
reference_id TEXT,
created_by TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- extension helper (for gen_random_uuid)
CREATE EXTENSION IF NOT EXISTS pgcrypto;