# Authentication & Authorization - Next Steps

## Status Overview

✅ **Completed:** Database schema, models, schemas, permissions, CRUD ops, routes, dependencies  
⏳ **Pending:** Container rebuild with dependencies, testing, endpoint protection, UI integration

---

## 🚨 Immediate Steps (Required - Complete First)

### 1. Rebuild Backend Container with Auth Dependencies

**Priority:** CRITICAL  
**Time Estimate:** 5-10 minutes  
**Status:** ⏳ Pending

The backend container needs to be rebuilt to install authentication dependencies.

```bash
cd /home/tim/dev/warehouse-neuron
docker compose build backend
docker compose up -d
```

**Dependencies to be installed:**
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing with bcrypt
- `python-multipart` - Form data parsing support

**Verification:**
```bash
# Check if backend started successfully
docker compose logs backend | tail -20

# Verify auth endpoints are available
curl http://localhost:8000/docs
```

---

### 2. Test Authentication System

**Priority:** HIGH  
**Time Estimate:** 10 minutes  
**Status:** ⏳ Pending (blocked by #1)

Run comprehensive tests to verify the auth system works correctly.

**Test Script:**
```bash
chmod +x /home/tim/dev/warehouse-neuron/scripts/test_auth.sh
./scripts/test_auth.sh
```

**Manual Testing:**
```bash
# Test 1: Login with default admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123"}'

# Extract token from response
TOKEN="eyJ..." # Copy from response

# Test 2: Get current user info
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Test 3: Check permissions
curl http://localhost:8000/api/v1/auth/permissions \
  -H "Authorization: Bearer $TOKEN"

# Test 4: Create a new user
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.staff",
    "email": "john@warehouse.local",
    "password": "Staff123",
    "role": "STAFF",
    "full_name": "John Staff"
  }'
```

**Expected Results:**
- ✅ Login returns JWT tokens
- ✅ Token authentication works
- ✅ Permission checks enforce access control
- ✅ User creation respects hierarchy
- ✅ Audit logs are created

---

### 3. Change Default Admin Password

**Priority:** CRITICAL  
**Time Estimate:** 2 minutes  
**Status:** ⏳ Pending (blocked by #1)

**⚠️ SECURITY:** The default admin password MUST be changed immediately.

```bash
# After first login, change password
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin123",
    "new_password": "YourSecurePassword123"
  }'
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

**After changing password:**
- ✅ All refresh tokens are revoked
- ✅ Must login again with new password
- ✅ `must_change_password` flag is set to false

---

### 4. Create Initial User Accounts

**Priority:** HIGH  
**Time Estimate:** 5 minutes per user  
**Status:** ⏳ Pending (blocked by #1)

Create user accounts for your team based on the hierarchy.

**Example Users:**

```bash
# 1. DB Manager (for you as technical manager)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tim.dbmanager",
    "email": "tim@warehouse.local",
    "password": "TempPass123",
    "role": "DB_MANAGER",
    "full_name": "Tim (DB Manager)"
  }'

# 2. Manager (for your boss)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "boss.manager",
    "email": "boss@warehouse.local",
    "password": "TempPass123",
    "role": "MANAGER",
    "full_name": "Boss (Manager)"
  }'

# 3. Supervisor (team lead)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "lead.supervisor",
    "email": "supervisor@warehouse.local",
    "password": "TempPass123",
    "role": "SUPERVISOR",
    "full_name": "Team Lead",
    "manager_id": "MANAGER_UUID_HERE"
  }'

# 4. Staff (warehouse workers)
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "worker1.staff",
    "email": "worker1@warehouse.local",
    "password": "TempPass123",
    "role": "STAFF",
    "full_name": "Worker 1",
    "manager_id": "SUPERVISOR_UUID_HERE"
  }'
```

**Note:** All users must change their password on first login.

---

## 📋 Short Term Steps (Recommended - Complete Within 1 Week)

### 5. Protect Existing API Endpoints

**Priority:** HIGH  
**Time Estimate:** 2 hours  
**Status:** ⏳ Pending

Add authentication and authorization to existing endpoints.

**Endpoints to Protect:**

#### Stock Operations (`app/routes/stock.py`)

```python
from app.auth_dependencies import get_current_user
from app.permissions import require_permission
from app.models_auth import User

@router.post("/api/v1/stock/intake")
@require_permission("stock.intake")
async def stock_intake(
    request: IntakeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Add current_user.id to audit trail
    # ... existing code ...
    pass
```

**Permissions Mapping:**
- `POST /api/v1/stock/intake` → `stock.intake`
- `GET /api/v1/stock/levels` → `stock.view`
- `GET /api/v1/stock/movements` → `stock.view`
- `POST /api/v1/stock/adjustment` → `stock.adjustment`
- `POST /api/v1/stock/transfer` → `stock.transfer`

#### SKU Management (`app/routes/skus.py`)

```python
@router.post("/api/v1/skus")
@require_permission("inventory.sku.create")
async def create_sku(
    sku_data: SKUCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pass

@router.get("/api/v1/skus")
@require_permission("inventory.sku.view")
async def list_skus(...):
    pass
```

**Permissions Mapping:**
- `POST /api/v1/skus` → `inventory.sku.create`
- `GET /api/v1/skus` → `inventory.sku.view`
- `GET /api/v1/skus/{id}` → `inventory.sku.view`
- `PUT /api/v1/skus/{id}` → `inventory.sku.update`
- `DELETE /api/v1/skus/{id}` → `inventory.sku.delete`

#### Inventory Operations (`app/routes/inventory.py`)

**Permissions Mapping:**
- `GET /api/v1/stock/levels` → `stock.view`
- `GET /api/v1/stock/movements` → `stock.view`

**Implementation Checklist:**
- [ ] Import auth dependencies in each route file
- [ ] Add `@require_permission` decorators
- [ ] Add `current_user: User = Depends(get_current_user)` parameter
- [ ] Update CRUD functions to track `created_by` / `updated_by`
- [ ] Update stock_movements table to link to users table
- [ ] Test each protected endpoint with different roles
- [ ] Update API documentation

---

### 6. Add Rate Limiting Middleware

**Priority:** MEDIUM  
**Time Estimate:** 1 hour  
**Status:** ⏳ Pending

Implement rate limiting to prevent abuse.

**Install Dependencies:**
```bash
# Add to requirements.txt
slowapi>=0.1.9
```

**Implementation (`app/main.py`):**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rate limits:
# - Login: 5 attempts per 15 minutes per IP
# - API calls: 100 per minute per user
# - Password reset: 3 per hour per email
```

**Rate Limit Examples:**
```python
@router.post("/api/v1/auth/login")
@limiter.limit("5/15minutes")
async def login(...):
    pass

@router.post("/api/v1/stock/intake")
@limiter.limit("100/minute")
async def stock_intake(...):
    pass
```

**Configuration:**
- Create `app/rate_limits.py` with limit definitions
- Add Redis storage backend for distributed rate limiting
- Add rate limit headers to responses
- Add monitoring for rate limit hits

---

### 7. Build Login UI in Flutter Web

**Priority:** HIGH  
**Time Estimate:** 4 hours  
**Status:** ⏳ Pending

Create authentication screens in the Flutter web dashboard.

**Screens to Create:**

#### a. Login Screen (`lib/screens/login_screen.dart`)

```dart
class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);
    
    try {
      final response = await ApiService.login(
        _usernameController.text,
        _passwordController.text,
      );
      
      // Store tokens
      await SecureStorage.saveTokens(
        response['access_token'],
        response['refresh_token'],
      );
      
      // Navigate to dashboard
      Navigator.pushReplacementNamed(context, '/dashboard');
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Login failed: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Card(
          child: Container(
            width: 400,
            padding: EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Warehouse Neuron', style: TextStyle(fontSize: 24)),
                SizedBox(height: 32),
                TextField(
                  controller: _usernameController,
                  decoration: InputDecoration(labelText: 'Username'),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _passwordController,
                  decoration: InputDecoration(labelText: 'Password'),
                  obscureText: true,
                ),
                SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  child: _isLoading
                      ? CircularProgressIndicator()
                      : Text('Login'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

#### b. Change Password Screen

For first-time login when `must_change_password` is true.

#### c. Secure Storage (`lib/services/secure_storage.dart`)

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  static const _storage = FlutterSecureStorage();
  
  static Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }
  
  static Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }
  
  static Future<void> clearTokens() async {
    await _storage.deleteAll();
  }
}
```

#### d. Update API Service

Add authentication header to all requests:

```dart
class ApiService {
  static Future<http.Response> _authenticatedRequest(
    String method,
    String endpoint,
    {Map<String, dynamic>? body}
  ) async {
    final token = await SecureStorage.getAccessToken();
    
    final headers = {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
    
    // Make request with headers
    // Handle 401 (token expired) by refreshing token
  }
}
```

**Dependencies to Add:**
```yaml
# pubspec.yaml
dependencies:
  flutter_secure_storage: ^9.0.0
```

**Implementation Checklist:**
- [ ] Create login screen
- [ ] Create change password screen
- [ ] Add secure storage for tokens
- [ ] Update API service with auth headers
- [ ] Handle token expiration and refresh
- [ ] Add logout functionality
- [ ] Add remember me option
- [ ] Show user info in app bar
- [ ] Protect routes with auth guard

---

### 8. Implement Email Notifications

**Priority:** MEDIUM  
**Time Estimate:** 3 hours  
**Status:** ⏳ Pending

Send emails for important auth events.

**Install Dependencies:**
```bash
# Add to requirements.txt
fastapi-mail>=1.4.1
```

**Events to Send Emails:**
- New user created (send credentials)
- Password reset requested
- Password changed successfully
- Failed login attempts (after 3 failures)
- Account deactivated

**Implementation (`app/email_service.py`):**
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

async def send_welcome_email(user: User, temp_password: str):
    message = MessageSchema(
        subject="Welcome to Warehouse Neuron",
        recipients=[user.email],
        body=f"""
        Hello {user.full_name},
        
        Your account has been created:
        Username: {user.username}
        Temporary Password: {temp_password}
        
        Please login and change your password immediately.
        """,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
```

**Configuration:**
```bash
# .env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@warehouse.local
```

---

### 9. Add Session Management UI

**Priority:** LOW  
**Time Estimate:** 2 hours  
**Status:** ⏳ Pending

Allow users to view and revoke active sessions.

**New Endpoint:**
```python
@router.get("/api/v1/auth/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # List all active refresh tokens for user
    tokens = crud_auth.list_user_tokens(db, current_user.id)
    return [
        {
            "id": token.id,
            "created_at": token.created_at,
            "expires_at": token.expires_at,
            "is_current": False,  # Check if current token
        }
        for token in tokens
    ]

@router.delete("/api/v1/auth/sessions/{token_id}")
async def revoke_session(...):
    # Revoke specific refresh token
    pass
```

**UI Features:**
- Show list of active sessions with creation dates
- Show device info (from user agent)
- Allow revoking individual sessions
- Show current session (cannot be revoked)
- Button to revoke all other sessions

---

### 10. Write Unit Tests for Auth System

**Priority:** MEDIUM  
**Time Estimate:** 3 hours  
**Status:** ⏳ Pending

Create comprehensive tests for authentication.

**Test File:** `services/backend/tests/test_auth.py`

```python
import pytest
from app import crud_auth
from app.auth_utils import hash_password, verify_password

def test_create_user(db_session):
    user = crud_auth.create_user(
        db_session,
        username="testuser",
        email="test@example.com",
        password="Test123",
        role="STAFF"
    )
    assert user.id is not None
    assert user.username == "testuser"
    assert user.role == "STAFF"

def test_authenticate_user(db_session, sample_user):
    user = crud_auth.authenticate_user(
        db_session,
        sample_user.username,
        "Test123"
    )
    assert user is not None
    assert user.id == sample_user.id

def test_authenticate_invalid_password(db_session, sample_user):
    user = crud_auth.authenticate_user(
        db_session,
        sample_user.username,
        "WrongPassword"
    )
    assert user is None

def test_change_password(db_session, sample_user):
    success = crud_auth.change_password(
        db_session,
        sample_user.id,
        "Test123",
        "NewPass123"
    )
    assert success is True
    
    # Verify old password no longer works
    user = crud_auth.authenticate_user(
        db_session,
        sample_user.username,
        "Test123"
    )
    assert user is None

def test_permission_check():
    from app.permissions import has_permission
    
    assert has_permission("DEV", "stock.intake") is True
    assert has_permission("STAFF", "user.create") is False
    assert has_permission("MANAGER", "stock.intake") is True

def test_hierarchy():
    from app.permissions import can_manage_user
    
    assert can_manage_user("MANAGER", "STAFF") is True
    assert can_manage_user("STAFF", "MANAGER") is False
    assert can_manage_user("DEV", "MANAGER") is True
```

**Run Tests:**
```bash
docker exec warehouse-neuron_backend_1 python -m pytest tests/test_auth.py -v
```

---

## 📊 Progress Tracking

### Immediate Steps Checklist

- [ ] 1. Rebuild backend container (5-10 min)
- [ ] 2. Test authentication system (10 min)
- [ ] 3. Change default admin password (2 min)
- [ ] 4. Create initial user accounts (20 min)

**Total Time:** ~45 minutes  
**Blocking Issues:** None

### Short Term Checklist

- [ ] 5. Protect existing API endpoints (2 hours)
- [ ] 6. Add rate limiting middleware (1 hour)
- [ ] 7. Build login UI in Flutter web (4 hours)
- [ ] 8. Implement email notifications (3 hours)
- [ ] 9. Add session management UI (2 hours)
- [ ] 10. Write unit tests for auth (3 hours)

**Total Time:** ~15 hours  
**Blocking Issues:** Must complete immediate steps first

---

## 🎯 Success Criteria

### Immediate Goals (End of Day 1)
- ✅ Backend container rebuilt and running
- ✅ Authentication endpoints working
- ✅ Admin password changed
- ✅ Test users created
- ✅ System documented

### Short Term Goals (End of Week 1)
- ✅ All endpoints protected with auth
- ✅ Rate limiting active
- ✅ Login UI functional
- ✅ Email notifications working
- ✅ 80%+ test coverage
- ✅ Production-ready security

---

## 📝 Notes

**Security Reminders:**
- ⚠️ Change default admin password immediately
- ⚠️ Use environment variables for secrets
- ⚠️ Enable HTTPS in production
- ⚠️ Regular security audits
- ⚠️ Monitor failed login attempts

**Documentation:**
- Update API_GUIDE.md with auth endpoints
- Create user management guide
- Document permission system
- Create troubleshooting guide

---

**Last Updated:** November 8, 2025  
**Status:** Ready to begin immediate steps  
**Next Action:** Rebuild backend container
