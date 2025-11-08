#!/bin/bash
# Test Authentication - Login and basic operations

API_URL="http://localhost:8000"

echo "========================================="
echo "Test 1: Login with default admin account"
echo "========================================="
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123"
  }')

echo "$LOGIN_RESPONSE" | jq '.'

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.id')

if [ "$ACCESS_TOKEN" == "null" ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo "✅ Login successful!"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo ""

echo "========================================="
echo "Test 2: Get current user info"
echo "========================================="
curl -s "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo ""

echo "========================================="
echo "Test 3: Get user permissions"
echo "========================================="
curl -s "$API_URL/api/v1/auth/permissions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo ""

echo "========================================="
echo "Test 4: Check specific permission"
echo "========================================="
curl -s -X POST "$API_URL/api/v1/auth/check-permission" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"permission": "stock.intake"}' | jq '.'
echo ""

echo "========================================="
echo "Test 5: Create a STAFF user"
echo "========================================="
NEW_USER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/users" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test.staff",
    "email": "test.staff@warehouse.local",
    "password": "Staff123",
    "role": "STAFF",
    "full_name": "Test Staff Member"
  }')

echo "$NEW_USER_RESPONSE" | jq '.'

NEW_USER_ID=$(echo "$NEW_USER_RESPONSE" | jq -r '.id')
echo ""

if [ "$NEW_USER_ID" != "null" ]; then
    echo "✅ User created successfully!"
    
    echo "========================================="
    echo "Test 6: Login with new staff account"
    echo "========================================="
    STAFF_LOGIN=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
      -H "Content-Type: application/json" \
      -d '{
        "username": "test.staff",
        "password": "Staff123"
      }')
    
    echo "$STAFF_LOGIN" | jq '.'
    
    STAFF_TOKEN=$(echo "$STAFF_LOGIN" | jq -r '.access_token')
    
    if [ "$STAFF_TOKEN" != "null" ]; then
        echo "✅ Staff login successful!"
        
        echo "========================================="
        echo "Test 7: Staff permissions check"
        echo "========================================="
        curl -s "$API_URL/api/v1/auth/permissions" \
          -H "Authorization: Bearer $STAFF_TOKEN" | jq '.'
        echo ""
    else
        echo "❌ Staff login failed!"
    fi
fi

echo "========================================="
echo "Test 8: List all users"
echo "========================================="
curl -s "$API_URL/api/v1/users?limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
echo ""

echo "========================================="
echo "✅ All tests completed!"
echo "========================================="
