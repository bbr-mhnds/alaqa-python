#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Base URL - change this according to your environment
BASE_URL="http://localhost:8000/api/v1"

# Test authentication token - replace with a valid token
AUTH_TOKEN="your_auth_token_here"

# Function to print response
print_response() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
    echo "Response:"
    echo "$3" | json_pp
    echo "----------------------------------------"
}

echo "🏥 Testing Doctors API Endpoints"
echo "========================================"

# 1. List Doctors (Public)
echo "1. Testing GET /api/v1/doctors/ (List Doctors)"
response=$(curl -s "${BASE_URL}/doctors/?page=1&page_size=2")
print_response $? "List Doctors" "$response"

# 2. Get Doctor Details (Public)
echo "2. Testing GET /api/v1/doctors/{id}/ (Get Doctor Details)"
DOCTOR_ID="fdb62949-ce34-4bac-ba7b-0aeee5a3ec1e"
response=$(curl -s "${BASE_URL}/doctors/${DOCTOR_ID}/")
print_response $? "Get Doctor Details" "$response"

# 3. Create Doctor (Protected)
echo "3. Testing POST /api/v1/doctors/ (Create Doctor)"
response=$(curl -s -X POST \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Dr. Test Doctor",
        "name_arabic": "د. طبيب اختبار",
        "sex": "male",
        "email": "test.doctor@example.com",
        "phone": "+966500000007",
        "experience": "Test experience",
        "category": "consultant",
        "language_in_sessions": "both",
        "license_number": "TEST001",
        "profile_english": "Test profile in English",
        "profile_arabic": "ملف تعريفي تجريبي",
        "status": "pending",
        "account_holder_name": "Test Doctor",
        "account_number": "9876543210",
        "iban_number": "SA0380000000608010167525",
        "specialities": ["a3cb17d3-d8f5-4547-a5da-733b6596eac1"]
    }' \
    "${BASE_URL}/doctors/")
print_response $? "Create Doctor" "$response"

# 4. Update Doctor (Protected)
echo "4. Testing PATCH /api/v1/doctors/{id}/ (Update Doctor)"
response=$(curl -s -X PATCH \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "experience": "Updated test experience"
    }' \
    "${BASE_URL}/doctors/${DOCTOR_ID}/")
print_response $? "Update Doctor" "$response"

# 5. Update Doctor Status (Protected)
echo "5. Testing PATCH /api/v1/doctors/{id}/status/ (Update Status)"
response=$(curl -s -X PATCH \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "status": "approved"
    }' \
    "${BASE_URL}/doctors/${DOCTOR_ID}/status/")
print_response $? "Update Doctor Status" "$response"

# 6. Filter and Search Doctors (Public)
echo "6. Testing GET /api/v1/doctors/ with filters"
response=$(curl -s "${BASE_URL}/doctors/?status=approved&search=doctor&ordering=-created_at")
print_response $? "Filter and Search Doctors" "$response"

# 7. Filter by Specialty (Public)
echo "7. Testing GET /api/v1/doctors/ with specialty filter"
SPECIALTY_ID="a3cb17d3-d8f5-4547-a5da-733b6596eac1"
response=$(curl -s "${BASE_URL}/doctors/?specialty=${SPECIALTY_ID}")
print_response $? "Filter by Specialty" "$response"

# Optional: Delete Doctor (Protected)
# Uncomment to test deletion
# echo "8. Testing DELETE /api/v1/doctors/{id}/ (Delete Doctor)"
# response=$(curl -s -X DELETE \
#     -H "Authorization: Bearer ${AUTH_TOKEN}" \
#     "${BASE_URL}/doctors/${DOCTOR_ID}/")
# print_response $? "Delete Doctor" "$response"

echo "========================================"
echo "API Testing Complete" 