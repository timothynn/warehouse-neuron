# warehouse-neuron

Next-gen AI-first inventory + supply chain brain.

A unified cross-platform system (mobile + web + desktop) for live inventory capture, AI forecasting, anomaly detection, smart reordering and eventual auto-pilot procurement.

## vision

Warehouses and retail inventory systems today are basically glorified spreadsheets with barcode inputs. This is the neural upgrade.

Barcode → event stream → brain.

Then forecasting, anomaly detection, and auto reordering become native features.

## tech stack

Backend: **Python FastAPI**
DB: **Postgres** (Timescale later)
Cache + Streams: **Redis**
Frontend: **Flutter** (mobile + web)
Desktop wrapper: **Tauri**
Auth: Supabase / Auth0
Infra: Docker / Fly / AWS
AI agents: Python (LangGraph style later)

## phases

### Phase A — foundations

shipable core

* monorepo + CI
* backend scaffold (FastAPI) + schema (SKU, barcode mapping, stock movements, ledger)
* auth
* Flutter app (mobile + web) + Tauri desktop wrapper
* scanning screen sends barcode → backend → ledger
* simple dashboard shows on_hand by location

### Phase B — reliability & integrations

enterprise ready

* Redis cache + background jobs
* event bus (Redis streams / Kafka)
* POS / eCommerce integration (Shopify example)
* barcode/lot/batch UX
* audit logs + RBAC

### Phase C — AI & automation

this is where the brain wakes up

* forecasting pipeline
* anomaly detection
* reorder engine + rule service
* agent orchestration (human in the loop by default)

### Phase D — optimization & scale

multi-echelon + digital twin

* multi warehouse optimization
* simulation environment
* full supplier automation (PO lifecycle + payments)
* observability + chaos testing

### Phase E — polish

* localization
* accessibility
* compliance + backup strategy
* SDKs and webhooks

## detailed task list by component

### repo / infra

* monorepo with `/apps/flutter-app`, `/apps/web-dashboard`, `/desktop/tauri`, `/services/backend`, `/infra`, `/ml`
* README, issue templates, CODEOWNERS
* CI build: backend + flutter
* IaC skeleton

### backend

* scaffold FastAPI
* env config + logging + health check
* Postgres schema
* `/api/v1/stock/intake` endpoint
* tests for intake flow

### schema

* `skus`
* `sku_barcodes`
* `locations`
* `stock_ledger`
* `stock_movements`

### frontend

* Flutter scaffold
* scan UX
* offline queue
* send scan to backend

### dashboard

* SKU list
* movements list
* simple search/filter

### infra

* Postgres instance
* Redis
* dockerfiles
* metrics endpoints

## how scanning works

scanner acts like a keyboard.
warehouse UI stays auto-focused on scan box.
scanner emits barcode + ENTER.
frontend immediately sends to backend.
backend resolves sku or auto-creates it.
stock movement + ledger update happen.

## license

MIT (will add file later)

## status

currently building Phase A foundations.
Next steps: backend tests.
