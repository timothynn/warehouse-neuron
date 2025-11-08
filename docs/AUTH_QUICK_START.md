# Authentication & Authorization - Quick Start Guide

## Overview
Complete auth system with role-based access control (RBAC) implemented for Warehouse Neuron.

---

## 🔐 Default Administrator Account

After running the migration, a default admin account is created:

```
Username: admin
Password: Admin123
Role: DEV (full system access)
Email: admin@warehouse.local
```

**⚠️ IMPORTANT:** Change this password immediately after first login!

---

## 🎯 User Roles & Hierarchy

```
1. DEV (Developer)        - System admin, full access
2. DB_MANAGER             - Database administration
3. MANAGER (Boss)         - Operational management
4. SUPERVISOR             - Team lead, approvals
5. STAFF (Worker)         - Basic warehouse operations
6. VIEWER (Guest/Auditor) - Read-only access
```

### Role Capabilities

| Role | Create SKUs | Stock Intake | Approve | Manage Users | View Reports |
|------|-------------|--------------|---------|--------------|--------------|
| DEV | ✅ | ✅ | ✅ | ✅ All | ✅ All |
| DB_MANAGER | ✅ | ✅ | ✅ | ❌ | ✅ All |
| MANAGER | ✅ | ✅ | ✅ | ✅ Lower roles | ✅ All |
| SUPERVISOR | ❌ | ✅ | ✅ Staff only | ❌ | ✅ Some |
| STAFF | ❌ | ✅ | ❌ | ❌ | ❌ |
| VIEWER | ❌ | ❌ | ❌ | ❌ | ✅ Some |

---

## 🚀 Quick Start

### 1. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "AbC123...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@warehouse.local",
    "role": "DEV",
    "full_name": "System Administrator",
    "is_active": true,
    "must_change_password": true
  }
}
```

### 2. Change Password (Required on First Login)

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_password": "Admin123",
    "new_password": "NewSecurePass123"
  }'
```

### 3. Get Current User Info

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create a New User

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "username": "john.doe",
    "email": "john@warehouse.com",
    "password": "SecurePass123",
    "role": "STAFF",
    "full_name": "John Doe"
  }'
```

---

## 📖 API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login
Login with username and password.

**Request:**
```json
{
  "username": "admin",
  "password": "Admin123"
}
```

#### POST /api/v1/auth/logout
Logout and revoke refresh token.

**Request:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

#### POST /api/v1/auth/refresh
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### POST /api/v1/auth/change-password
Change current user's password.

**Request:**
```json
{
  "old_password": "OldPass123",
  "new_password": "NewPass123"
}
```

#### GET /api/v1/auth/permissions
Get current user's permissions list.

#### POST /api/v1/auth/check-permission
Check if current user has a specific permission.

**Request:**
```json
{
  "permission": "stock.intake"
}
```

---

### User Management Endpoints

#### POST /api/v1/users
Create a new user (requires `user.create` permission).

**Request:**
```json
{
  "username": "jane.smith",
  "email": "jane@warehouse.com",
  "password": "TempPass123",
  "role": "SUPERVISOR",
  "full_name": "Jane Smith",
  "manager_id": "manager_uuid",
  "team_id": "team_uuid"
}
```

#### GET /api/v1/users
List all users (filtered by hierarchy).

**Query Parameters:**
- `skip`: Offset for pagination (default: 0)
- `limit`: Limit results (default: 100)
- `role`: Filter by role
- `is_active`: Filter by active status

#### GET /api/v1/users/{user_id}
Get user details by ID.

#### PUT /api/v1/users/{user_id}
Update user information.

**Request:**
```json
{
  "email": "newemail@warehouse.com",
  "full_name": "Jane Smith Updated",
  "role": "MANAGER",
  "is_active": true
}
```

#### POST /api/v1/users/{user_id}/deactivate
Deactivate a user account.

#### POST /api/v1/users/{user_id}/activate
Activate a user account.

#### POST /api/v1/users/{user_id}/reset-password
Reset user password (admin action).

**Response:**
```json
{
  "message": "Password reset successfully",
  "temporary_password": "Abc123def",
  "note": "User must change password on next login"
}
```

#### GET /api/v1/users/{user_id}/audit-logs
Get audit logs for a specific user.

---

## 🔑 Using Authentication in Requests

### Include Access Token in Headers

```bash
curl http://localhost:8000/api/v1/stock/intake \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Token Expiration

- **Access Token**: 15 minutes
- **Refresh Token**: 7 days

When access token expires, use refresh token to get a new one:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 🛡️ Permission System

### Permission Format

Permissions follow the pattern: `resource.action`

Examples:
- `stock.intake` - Create stock intake
- `stock.view` - View stock levels
- `inventory.sku.create` - Create new SKU
- `user.create` - Create new user
- `system.logs.view` - View audit logs

### Wildcard Permissions

- `*` - All permissions (DEV only)
- `stock.*` - All stock permissions
- `inventory.*` - All inventory permissions

### Check Your Permissions

```bash
curl http://localhost:8000/api/v1/auth/permissions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "has_permission": true,
  "user_role": "STAFF",
  "permissions": [
    "stock.intake",
    "stock.transfer",
    "stock.view",
    "location.view",
    "inventory.sku.view"
  ]
}
```

---

## 👥 User Management Hierarchy

### Who Can Manage Whom

- **DEV**: Can manage everyone
- **DB_MANAGER**: Can manage no one (technical role)
- **MANAGER**: Can manage SUPERVISOR, STAFF, VIEWER
- **SUPERVISOR**: Can manage STAFF, VIEWER
- **STAFF**: Can manage self only
- **VIEWER**: Can manage no one

### Example Workflow

1. **DEV** creates **MANAGER**
2. **MANAGER** creates **SUPERVISOR**
3. **SUPERVISOR** creates **STAFF**
4. **STAFF** performs warehouse operations
5. **SUPERVISOR** approves STAFF actions

---

## 📊 Audit Logging

All authentication and user actions are logged automatically:

### Logged Events

- `auth.login.success` - Successful login
- `auth.login.failed` - Failed login attempt
- `auth.logout` - User logout
- `auth.password.changed` - Password changed
- `user.created` - New user created
- `user.updated` - User information updated
- `user.deactivated` - User deactivated
- `user.activated` - User activated
- `user.password.reset` - Password reset by admin

### View Audit Logs

```bash
curl http://localhost:8000/api/v1/users/{user_id}/audit-logs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔒 Security Features

### Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- Cannot be same as username

### Rate Limiting

- Login attempts: 5 per 15 minutes per IP
- API calls: 100 per minute per user
- Password reset: 3 per hour per email

### Token Security

- Access tokens expire in 15 minutes
- Refresh tokens are stored hashed
- Refresh tokens can be revoked
- All tokens revoked on password change

### Audit Trail

- Every action is logged with:
  - User ID
  - Action type
  - Resource affected
  - IP address
  - User agent
  - Timestamp

---

## 🧪 Testing Authentication

### Test Login
```bash
./test_auth_login.sh
```

### Test User Creation
```bash
./test_auth_create_user.sh
```

### Test Permission Check
```bash
./test_auth_permissions.sh
```

---

## 🐛 Troubleshooting

### "Invalid authentication credentials"
- Token expired (get new token via refresh)
- Token malformed (re-login)
- Token revoked (re-login)

### "Permission denied"
- User doesn't have required permission
- Check permissions: `/api/v1/auth/permissions`

### "Cannot create user with role X"
- Current user cannot manage that role level
- Only higher roles can create lower roles

### "User account is inactive"
- Account has been deactivated
- Contact admin to reactivate

---

## 📝 Example Scenarios

### Scenario 1: New Warehouse Staff Member

```bash
# 1. Manager logs in
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "ManagerPass123"}'

# 2. Manager creates staff account
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new.staff",
    "email": "staff@warehouse.com",
    "password": "TempPass123",
    "role": "STAFF",
    "full_name": "New Staff Member"
  }'

# 3. Staff logs in with temp password
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "new.staff", "password": "TempPass123"}'

# 4. Staff changes password (required)
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "TempPass123",
    "new_password": "MyNewPass123"
  }'

# 5. Staff performs stock intake
curl -X POST http://localhost:8000/api/v1/stock/intake \
  -H "Authorization: Bearer STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "PROD-001",
    "qty": 100,
    "location_code": "WH-A-01",
    "movement_type": "INTAKE"
  }'
```

### Scenario 2: Supervisor Approves Stock Movement

```bash
# 1. Supervisor logs in
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "supervisor", "password": "SuperPass123"}'

# 2. View pending approvals
curl http://localhost:8000/api/v1/stock/movements?status=pending \
  -H "Authorization: Bearer SUPERVISOR_TOKEN"

# 3. Approve movement
curl -X POST http://localhost:8000/api/v1/stock/movements/{id}/approve \
  -H "Authorization: Bearer SUPERVISOR_TOKEN"
```

---

## 🎨 Frontend Integration (Flutter)

### Store Tokens Securely

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();

// Save tokens
await storage.write(key: 'access_token', value: accessToken);
await storage.write(key: 'refresh_token', value: refreshToken);

// Retrieve tokens
String? accessToken = await storage.read(key: 'access_token');
```

### Add Authorization Header

```dart
final response = await http.post(
  Uri.parse('http://localhost:8000/api/v1/stock/intake'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode(data),
);
```

### Handle Token Expiration

```dart
if (response.statusCode == 401) {
  // Token expired, refresh it
  final newToken = await refreshAccessToken(refreshToken);
  // Retry request with new token
}
```

---

## 📚 Additional Resources

- API Documentation: http://localhost:8000/docs
- Phase A Checklist: `docs/PHASE_A_CHECKLIST.md`
- Auth Design Doc: *(created earlier in this session)*

---

## ✅ Verification Checklist

- [ ] Default admin account works
- [ ] Can create new users
- [ ] Password change required on first login
- [ ] Permissions enforced on endpoints
- [ ] Audit logs created for actions
- [ ] Tokens expire correctly
- [ ] Refresh token workflow works
- [ ] Hierarchy rules enforced
- [ ] Deactivated users cannot login
- [ ] All endpoints protected with auth

---

**Created:** November 8, 2025
**Version:** 1.0
**Status:** ✅ Fully Implemented
