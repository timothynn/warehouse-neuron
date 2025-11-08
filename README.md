# Warehouse Neuron 🧠

> A neural upgrade for traditional warehouse management systems

**Modern inventory tracking with barcode scanning, real-time updates, and intelligent workflows.**

[![Phase](https://img.shields.io/badge/Phase-A-blue)]() 
[![Backend](https://img.shields.io/badge/Backend-Ready-green)]() 
[![Frontend](https://img.shields.io/badge/Frontend-Ready-green)]()
[![Web Dashboard](https://img.shields.io/badge/Web-Live-brightgreen)]()
---

## 🎯 Project Vision

Transform inventory management from a chore into an intelligent, responsive system:

- **📱 Mobile-First:** Scan barcodes anywhere in the warehouse
- **⚡ Real-Time:** Instant stock updates via Redis streams
- **🔍 Complete Audit Trail:** Every movement tracked and traceable
- **🌐 Multi-Platform:** Web, mobile, and desktop from one codebase
- **🚀 Cloud-Ready:** Designed for scale and reliability

**Current Status:** Phase A - Backend + Web Dashboard Complete!

---

## 🌐 Access Points

- **Web Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Database (DBeaver):** localhost:5434

---

## 📋 Phase A Progress

### ✅ Completed

- [x] Nix flake development environment with automatic venv
- [x] Docker Compose multi-service setup (Postgres, Redis, FastAPI)
- [x] SQLAlchemy schema with 5 core tables
- [x] FastAPI backend with stock intake endpoint
- [x] Redis event streaming for real-time updates
- [x] Database connection pooling
- [x] Code formatting (Black + isort)
- [x] API documentation (Swagger UI)
- [x] Comprehensive testing guides
- [x] **Flutter web dashboard with stock intake interface**
- [x] **CORS middleware for web access**

### 🚧 In Progress

- [ ] Database migrations (Alembic)
- [ ] Flutter mobile app (Android + iOS)
- [ ] Tauri desktop wrapper
- [ ] Authentication system
- [ ] Unit and integration tests
- [ ] Real-time statistics dashboard

### 📚 Documentation

- [API Guide](./docs/API_GUIDE.md) - Complete API reference with Postman/DBeaver guides
- [Database Setup](./docs/DATABASE_SETUP.md) - Schema, migrations, and maintenance
- [Web Dashboard README](./apps/warehouse_web/README.md) - Flutter web app guide
- [APP.md](./APP.md) - Full project vision and roadmap

---

## 🚀 Quick Start

### Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- [direnv](https://direnv.net/) (optional but recommended)
- Docker or Podman

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd warehouse-neuron

# Allow direnv (automatic environment)
direnv allow

# Or manually activate Nix environment
nix develop
```

The Nix environment provides:
- Python 3.13.8 with venv
- Black & isort formatters
- All backend dependencies

### 2. Start Services

```bash
# Start all services (Postgres, Redis, Backend)
docker compose up -d

# View logs
docker compose logs -f backend
```

### 3. Initialize Database

```bash
# Run initial migration
docker exec -i warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron < services/migrations/0001_init.sql

# Verify tables created
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c '\dt'
```

### 4. Test API

Open http://localhost:8000/docs in your browser to access the interactive API documentation.

**Quick test:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI 0.121.0 - Modern async web framework
- PostgreSQL 15 - Primary data store
- Redis 7 - Event streaming and caching
- SQLAlchemy 2.0 - Async ORM
- Pydantic 2.12 - Data validation

**Frontend (Coming):**
- Flutter - Cross-platform UI (mobile + web)
- Tauri - Desktop wrapper (Windows, macOS, Linux)

**DevOps:**
- Nix Flakes - Reproducible environments
- Docker Compose - Local development
- GitHub Actions - CI/CD (future)

### Database Schema

```
locations          → Warehouse zones/bins
skus               → Product catalog
sku_barcodes       → Barcode mappings (many-to-one)
stock_ledger       → Current inventory levels
stock_movements    → Complete transaction history
```

See [DATABASE_SETUP.md](./docs/DATABASE_SETUP.md) for detailed schema documentation.

---

## 📁 Project Structure

```
warehouse-neuron/
├── flake.nix                   # Nix development environment
├── .envrc                      # direnv auto-activation
├── docker-compose.yml          # Multi-service orchestration
├── README.md                   # This file
├── APP.md                      # Project vision & roadmap
├── docs/
│   ├── API_GUIDE.md           # Complete API documentation
│   └── DATABASE_SETUP.md      # Database guide
├── apps/                       # Frontend applications (future)
└── services/
    ├── backend/                # FastAPI backend
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py         # Application entry point
    │       ├── config.py       # Settings management
    │       ├── database.py     # DB connection pool
    │       ├── models.py       # SQLAlchemy models
    │       ├── schema.py       # Pydantic schemas
    │       ├── crud.py         # Database operations
    │       └── routes/
    │           └── stock.py    # Stock management API
    └── migrations/
        └── 0001_init.sql       # Initial schema
```

---

## 🔧 Development Workflow

### Code Formatting

```bash
# Format all Python files
black .
isort .

# Check without changes
black --check .
isort --check-only .
```

### Docker Operations

```bash
# Start services
docker compose up -d

# Rebuild after code changes
docker compose up -d --build --no-cache

# View logs
docker compose logs -f backend

# Stop services
docker compose down

# Reset everything
docker compose down -v  # Removes volumes too
```

### Database Access

```bash
# Connect via psql
psql -h localhost -p 5434 -U wn_user -d warehouse_neuron

# Or via Docker
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron

# Run query
docker exec -it warehouse-neuron_postgres_1 psql -U wn_user -d warehouse_neuron -c 'SELECT * FROM skus;'
```

---

## 🌐 Service Endpoints

### Backend API
- **Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Database (PostgreSQL)
- **Host:** localhost
- **Port:** 5434 (external), 5432 (internal)
- **Database:** warehouse_neuron
- **User:** wn_user
- **Password:** wn_pass

### Redis
- **Host:** localhost
- **Port:** 6379

---

## 📚 API Reference

### Key Endpoints

**Health Check**
```bash
GET /health
```

**Stock Intake (Main Feature)**
```bash
POST /api/v1/stock/intake
Content-Type: application/json

{
  "barcode": "123456789012",
  "qty": 10,
  "location_code": "WH-A-01",
  "movement_type": "IN",
  "auto_create_sku": true,
  "created_by": "user@example.com"
}
```

**Interactive Documentation**
- Full API reference: http://localhost:8000/docs
- Complete testing guide: [docs/API_GUIDE.md](./docs/API_GUIDE.md)

---

## 🧪 Testing

### API Testing with Postman
See [API_GUIDE.md](./docs/API_GUIDE.md) for:
- Postman collection setup
- Example requests
- Complete testing scenarios

### Database Testing with DBeaver
See [DATABASE_SETUP.md](./docs/DATABASE_SETUP.md) for:
- Connection setup
- Sample queries
- Performance monitoring

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test stock intake
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{"barcode":"TEST-001","qty":10,"auto_create_sku":true}'
```

---

## 📦 Environment Variables

Backend service configuration (set in `docker-compose.yml`):

```env
DATABASE_URL=postgresql+asyncpg://wn_user:wn_pass@postgres:5432/warehouse_neuron
REDIS_URL=redis://redis:6379
APP_ENV=development
```

---

## 🛠️ Troubleshooting

### Services won't start
```bash
# Check container status
docker ps -a

# View logs
docker compose logs backend
docker compose logs postgres

# Restart services
docker compose restart
```

### Port conflicts
```bash
# Check what's using port 5434
netstat -tuln | grep 5434

# Or use different port in docker-compose.yml
```

### Database connection failed
```bash
# Test from host
psql -h localhost -p 5434 -U wn_user -d warehouse_neuron

# Test from container
docker exec warehouse-neuron_postgres_1 pg_isready -U wn_user
```

See troubleshooting sections in:
- [API_GUIDE.md](./docs/API_GUIDE.md#troubleshooting)
- [DATABASE_SETUP.md](./docs/DATABASE_SETUP.md#troubleshooting)

---

## 🗺️ Roadmap

### Phase A - Foundations (Current)
Backend scaffold, schema, basic scanning

### Phase B - Reliability
Error handling, offline queue, retry logic

### Phase C - Intelligence
AI-powered predictions, anomaly detection

### Phase D - Optimization
Multi-warehouse, advanced analytics

### Phase E - Polish
UI/UX refinement, performance tuning

See [APP.md](./APP.md) for complete roadmap details.

---

## 🤝 Contributing

1. Follow existing code style (Black + isort)
2. Run formatters before committing
3. Test changes locally with Docker Compose
4. Update documentation for new features
5. Write tests for new functionality

---

## 📄 License

[License TBD]

---

## 📞 Support

- **Documentation:** [docs/](./docs/)
- **Issues:** [GitHub Issues](https://github.com/your-repo/warehouse-neuron/issues)
- **API Docs:** http://localhost:8000/docs

---

**Built with ❤️ for modern warehouse operations**
