# Warehouse Neuron Web Dashboard

Phase A web dashboard implementation using Flutter for web.

## 🌐 Live Demo

**Web Dashboard:** http://localhost:3000 (when running)  
**Backend API:** http://localhost:8000

## Features

- ✅ **Real-time API Health Monitoring** - Visual indicator showing backend connection status
- ✅ **Stock Intake Interface** - Submit barcode scans with quantity, location, and movement type
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile browsers
- ✅ **Material Design 3** - Modern, clean UI with proper theming
- ⏳ **Statistics Overview** - Dashboard cards (connected to real data in Phase B)
- ⏳ **Recent Activity Feed** - View latest stock movements (Phase B)

## Quick Start

### 1. Build the Web App

```bash
cd apps/warehouse_web
flutter build web
```

### 2. Serve the App

```bash
python -m http.server 3000 --directory build/web
```

### 3. Open in Browser

Navigate to: **http://localhost:3000**

## Backend Connection

The web dashboard connects to: **http://localhost:8000**

Ensure the backend is running:
```bash
docker ps | grep backend
```

## Usage

### Stock Intake Form

1. **Enter Barcode:** Type or scan barcode code
2. **Set Quantity:** Number of units (default: 1)
3. **Select Movement Type:**
   - IN - Receiving new stock
   - OUT - Shipping/removing stock
   - TRANSFER - Moving between locations
   - ADJUSTMENT - Cycle count corrections
4. **Location:** Warehouse location code (e.g., WH-A-01)
5. **User:** Your identifier for audit trail
6. **Auto-create SKU:** Enable to create new SKUs automatically
7. **Submit:** Process the stock movement

### Testing the Dashboard

```bash
# Test with curl first
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "TEST-WEB-001",
    "qty": 25,
    "location_code": "WH-A-01",
    "auto_create_sku": true,
    "created_by": "web_user"
  }'

# Then try the same in the web dashboard
```

## Project Structure

```
lib/
├── main.dart                      # App entry point
├── models/
│   └── stock_models.dart         # Data models
├── screens/
│   └── dashboard_screen.dart     # Main dashboard
├── services/
│   └── api_service.dart          # API client
└── widgets/
    ├── stats_card.dart           # Statistics cards
    ├── stock_intake_card.dart    # Stock intake form
    └── recent_activity_card.dart # Activity feed
```

## Development

### Hot Reload (Development Mode)

```bash
flutter run -d chrome
# or
flutter run -d web-server --web-port 3000
```

### Production Build

```bash
flutter build web --release
```

## Troubleshooting

### CORS Errors

If you see CORS errors, the backend needs to allow web app requests.

Add to `services/backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Failed

1. Check backend is running: `docker ps`
2. Check backend logs: `docker compose logs backend`
3. Verify API URL in `lib/services/api_service.dart`
4. Test API directly: `curl http://localhost:8000/health`

## Phase A Status

- ✅ Web dashboard built and running
- ✅ Stock intake form functional
- ✅ API health monitoring
- ✅ Responsive layout
- ⏳ Real-time statistics (Phase B)
- ⏳ Activity feed with real data (Phase B)
- ⏳ Authentication (Phase B)

## Documentation

- [Main README](../../README.md)
- [API Guide](../../docs/API_GUIDE.md)
- [Database Setup](../../docs/DATABASE_SETUP.md)
- [Phase A Checklist](../../docs/PHASE_A_CHECKLIST.md)

---

**Phase A - Web Dashboard Complete!** 🎉
