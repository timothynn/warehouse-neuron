# Phase A Implementation Checklist

**Phase A Goal:** Foundations — Shipable Core

Create a minimal but functional inventory tracking system with barcode scanning capability.

---

## ✅ Backend Foundations

### Infrastructure
- [x] Nix flake development environment
- [x] direnv automatic activation
- [x] Docker Compose multi-service setup
- [x] PostgreSQL 15 container
- [x] Redis 7 container
- [x] FastAPI backend container
- [x] Environment variables configuration
- [x] .gitignore for Python projects

### Database Schema
- [x] SQLAlchemy models created
  - [x] `locations` table
  - [x] `skus` table
  - [x] `sku_barcodes` table
  - [x] `stock_ledger` table
  - [x] `stock_movements` table
- [x] Initial migration script (`0001_init.sql`)
- [x] Run migration to create tables ✓ (All 5 tables exist)
- [x] Add database indexes for performance ✓ (9 indexes including PKs, UNIQUEs, and FKs)
- [x] Seed sample data for testing ✓ (4 SKUs exist from testing)

### API Endpoints
- [x] FastAPI application structure ✓
- [x] Root endpoint (`GET /`) ✓ Returns {"message":"Warehouse Neuron API","status":"running"}
- [x] Health check endpoint (`GET /health`) ✓ Returns {"status":"healthy"}
- [x] Stock intake endpoint (`POST /api/v1/stock/intake`) ✓ Fully functional
  - [x] Barcode lookup ✓
  - [x] Auto-create SKU functionality ✓
  - [x] Location creation/lookup ✓
  - [x] Stock ledger updates ✓
  - [x] Movement recording ✓
  - [x] Redis event emission ✓
- [x] Get SKU details endpoint (`GET /api/v1/skus/{id}`) ✓ NEW
- [x] List SKUs endpoint (`GET /api/v1/skus`) ✓ NEW with pagination & search
- [x] Get stock levels by location (`GET /api/v1/stock/levels`) ✓ NEW with filters
- [x] List stock movements (`GET /api/v1/stock/movements`) ✓ NEW with filtering & pagination
- [x] Search functionality ✓ Integrated into list endpoints

### Data Validation
- [x] Pydantic schemas for requests ✓ (IntakeRequest with BaseModel)
- [x] Pydantic schemas for responses ✓ (IntakeResponse with BaseModel)
- [x] Request validation (barcode, qty, location) ✓ (FastAPI automatic validation)
- [x] Response error handling standardization ✓ (HTTPException with 404, detail messages)
- [x] Input sanitization ✓ (Pydantic handles type validation and coercion)

### Code Quality
- [x] Black code formatter setup ✓ (Available in dev environment)
- [x] isort import organizer ✓ (Available in dev environment)
- [x] All Python files formatted ✓ (9 Python files in clean structure)
- [x] Unit tests for CRUD operations ✓ NEW (20+ test cases in test_crud.py)
- [x] Integration tests for API endpoints ✓ NEW (25+ test cases in test_api.py)
- [x] Test coverage reporting ✓ NEW (pytest-cov configured in pyproject.toml)

---

## 🚧 Authentication & Authorization

- [ ] User model
- [ ] JWT token generation
- [ ] Login endpoint
- [ ] Logout endpoint
- [ ] Token validation middleware
- [ ] Protected routes
- [ ] Role-based access control (RBAC)
- [ ] Password hashing (bcrypt)

---

## 🚧 Frontend - Flutter Mobile App

### Setup
- [ ] Create Flutter project structure
- [ ] Setup state management (Riverpod/Provider/Bloc)
- [ ] Setup HTTP client (Dio)
- [ ] Configure API base URL
- [ ] Add dependencies (camera, barcode scanner)

### UI Screens
- [ ] Login screen
- [ ] Home/Dashboard screen
- [ ] Scanning screen
  - [ ] Camera barcode scanner integration
  - [ ] Manual barcode entry fallback
  - [ ] Quantity input
  - [ ] Location selector
  - [ ] Movement type selector
- [ ] Stock levels view
  - [ ] List view with search
  - [ ] Location filter
  - [ ] Detail view
- [ ] Movement history
  - [ ] List with infinite scroll
  - [ ] Filter by date/type/user
  - [ ] Detail view
- [ ] Settings screen

### Offline Support
- [ ] Local database (SQLite/Hive)
- [ ] Queue failed requests
- [ ] Retry mechanism
- [ ] Sync status indicator
- [ ] Conflict resolution strategy

---

## ✅ Frontend - Flutter Web

- [x] Responsive layout for web ✓ (Wide/narrow layouts, breakpoint at 900px)
- [x] Desktop-optimized navigation ✓ (AppBar with actions, settings)
- [x] Dashboard screen ✓ (Stats, intake form, activity feed)
- [x] Stock intake form ✓ (Barcode, qty, location, movement type)
- [x] Real-time stats display ✓ (Total SKUs, locations, movements, units)
- [x] Recent activity feed ✓ (Shows up to 50 recent movements)
- [x] Toast notifications ✓ (Bottom-right animated popups)
- [x] Settings screen ✓ (API config, notifications, dashboard settings)
- [x] State management ✓ (Provider pattern with DashboardProvider)
- [x] Material Design 3 theming ✓
- [x] CORS configured ✓ (Backend middleware active)
- [ ] Keyboard shortcuts (Future enhancement)
- [ ] Webcam barcode scanning (Future enhancement)
- [ ] Enhanced data tables (Phase B)
- [ ] Export functionality (CSV, Excel) (Phase B)
- [ ] Advanced filters and search (Phase B)

---

## 🚧 Desktop - Tauri Wrapper

- [ ] Tauri project setup
- [ ] Package Flutter web build
- [ ] System tray integration
- [ ] Auto-update functionality
- [ ] USB barcode scanner support
- [ ] Print label integration
- [ ] Native file dialogs
- [ ] Desktop notifications

---

## 📚 Documentation

- [x] README.md with quick start
- [x] API_GUIDE.md with complete reference
  - [x] Endpoint documentation
  - [x] DBeaver connection guide
  - [x] Postman testing guide
  - [x] Example requests/responses
  - [x] Troubleshooting section
- [x] DATABASE_SETUP.md
  - [x] Schema documentation
  - [x] Migration guide
  - [x] Sample queries
  - [x] Backup/restore procedures
  - [x] Performance optimization
- [x] Postman collection export
- [ ] Architecture diagram
- [ ] Deployment guide
- [ ] Development workflow guide
- [ ] API changelog
- [ ] User guide (end users)

---

## 🔧 DevOps & Deployment

### CI/CD
- [ ] GitHub Actions workflow
- [ ] Automated tests on PR
- [ ] Code quality checks (linting, formatting)
- [ ] Docker image build
- [ ] Automated deployment to staging
- [ ] Manual approval for production

### Deployment
- [ ] Production Docker Compose config
- [ ] Environment-specific configs
- [ ] SSL/TLS certificates
- [ ] Database backup automation
- [ ] Log aggregation (Loki/ELK)
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Health check endpoints
- [ ] Graceful shutdown handling

### Infrastructure
- [ ] VPS/Cloud provider selection
- [ ] Domain name setup
- [ ] DNS configuration
- [ ] Reverse proxy (Nginx/Traefik)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] Firewall rules

---

## 🧪 Testing

### Backend Testing
- [ ] Unit tests for models
- [ ] Unit tests for CRUD functions
- [ ] Unit tests for schemas
- [ ] Integration tests for API endpoints
- [ ] Database transaction tests
- [ ] Redis integration tests
- [ ] Load testing (Locust/K6)
- [ ] Security testing (OWASP)

### Frontend Testing
- [ ] Widget tests
- [ ] Integration tests
- [ ] Golden/snapshot tests
- [ ] End-to-end tests
- [ ] Accessibility tests

### Test Coverage
- [ ] Setup coverage reporting
- [ ] Target: >80% coverage
- [ ] Coverage badges in README

---

## 🎯 Performance Optimization

### Database
- [ ] Add indexes on foreign keys
- [ ] Add indexes on frequently queried columns
- [ ] Query optimization (EXPLAIN ANALYZE)
- [ ] Connection pooling tuning
- [ ] Database vacuum schedule

### API
- [ ] Response caching (Redis)
- [ ] Pagination for list endpoints
- [ ] Field selection (sparse fields)
- [ ] Compression (gzip)
- [ ] Rate limiting per user

### Frontend
- [ ] Image optimization
- [ ] Code splitting
- [ ] Lazy loading
- [ ] Service worker for PWA
- [ ] Asset caching strategy

---

## 🔒 Security

### API Security
- [ ] HTTPS enforcement
- [ ] Input validation
- [ ] SQL injection prevention (using ORM properly)
- [ ] XSS prevention
- [ ] CSRF tokens
- [ ] API rate limiting
- [ ] Request size limits
- [ ] Security headers (HSTS, CSP, etc.)

### Authentication
- [ ] Secure password storage (bcrypt)
- [ ] Token expiration
- [ ] Refresh token rotation
- [ ] Account lockout after failed attempts
- [ ] Password strength requirements
- [ ] Two-factor authentication (future)

### Database Security
- [ ] Encrypted connections (SSL)
- [ ] Least privilege access
- [ ] Separate read-only user for reporting
- [ ] Regular backups with encryption
- [ ] Secrets management (environment variables)

---

## 📊 Monitoring & Observability

- [ ] Application logs
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Database query monitoring
- [ ] API response time tracking
- [ ] User activity analytics
- [ ] Uptime monitoring
- [ ] Alert system for critical errors

---

## 🚀 Phase A MVP Criteria

To complete Phase A and move to Phase B, the following must be true:

### Core Functionality
- [x] Backend API running and accessible
- [ ] Database tables created and indexed
- [ ] Stock intake works end-to-end
- [ ] Flutter mobile app can scan and submit
- [ ] Data persists correctly
- [ ] Movement history viewable

### Quality
- [ ] No critical bugs
- [ ] Basic error handling in place
- [ ] API documentation complete
- [ ] User guide available
- [ ] Code formatted and clean

### Deployment
- [ ] Can deploy to production server
- [ ] Database backups working
- [ ] Basic monitoring in place
- [ ] SSL/HTTPS configured

---

## 📝 Notes

### Current Blockers
1. ~~Database migration not run yet - tables don't exist~~ ✅ RESOLVED
2. ~~Frontend not started - need to initialize Flutter project~~ ✅ RESOLVED
3. Authentication not implemented - API is currently open (Deferred to Phase B)

### Next Immediate Steps
1. ~~Run `0001_init.sql` migration to create tables~~ ✅ COMPLETED
2. ~~Test stock intake endpoint with real database~~ ✅ COMPLETED
3. ~~Initialize Flutter project structure~~ ✅ COMPLETED
4. ~~Create basic scanning UI mockup~~ ✅ COMPLETED (Full dashboard with intake form)
5. Add unit tests for CRUD operations
6. Add integration tests for API endpoints
7. Implement authentication (JWT) - Phase B priority

### Known Issues
- None currently - all services healthy ✓
- Backend API fully operational ✓
- Database tables created and indexed ✓
- Flutter web dashboard functional ✓
- CORS properly configured ✓

### Technical Debt
- Need unit and integration tests (Priority: HIGH)
- Need comprehensive error handling in edge cases
- Need request/response logging middleware
- Need API versioning strategy (v2, v3 planning)
- Need database migration tool (Alembic) instead of raw SQL
- Need authentication system (JWT) - Phase B
- Need API documentation (Swagger UI already available at /docs)

---

## 🎓 Learning Resources

### Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [Redis Streams](https://redis.io/docs/data-types/streams/)

### Frontend
- [Flutter Documentation](https://docs.flutter.dev/)
- [Flutter Barcode Scanner](https://pub.dev/packages/mobile_scanner)
- [State Management](https://docs.flutter.dev/data-and-backend/state-mgmt)

### DevOps
- [Docker Compose](https://docs.docker.com/compose/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Last Updated:** November 8, 2025  
**Phase:** A - Foundations (Backend ✅ Complete, Frontend Web ✅ Complete)  
**Completion:** ~75% (Backend infrastructure ✅, Web dashboard ✅, Testing pending, Mobile app pending)
