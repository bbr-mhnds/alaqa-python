# Doctor Registration API Tests

## Prerequisites
- Install curl
- Have test files ready for document upload:
  - `license.pdf`
  - `qualification.pdf`

## Test Cases

### 1. Initiate Registration

#### a. Success Case
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.doctor@alaqa.net",
    "phone": "555552022"
  }'
```

#### b. Invalid Email
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "phone": "555552022"
  }'
```

#### c. Invalid Phone
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.doctor@alaqa.net",
    "phone": "123"
  }'
```

### 2. Complete Registration

#### a. Success Case
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "123",
    "email": "test.doctor@alaqa.net",
    "sms_code": "000000",
    "name_arabic": "طبيب تجريبي",
    "name": "Test Doctor",
    "sex": "male",
    "phone": "555552022",
    "experience": "10 years",
    "category": "specialist",
    "language_in_sessions": "both",
    "license_number": "LIC20250106123456",
    "specialities": ["188da049-4265-4ddb-9df7-5b9dc8cb2056"],
    "profile_arabic": "نبذة عن الطبيب باللغة العربية",
    "profile_english": "Doctor profile in English",
    "password": "TestPass@123",
    "confirm_password": "TestPass@123",
    "terms_and_privacy_accepted": true,
    "bank_name": "Test Bank",
    "account_holder_name": "Test Doctor",
    "account_number": "12345678",
    "iban_number": "SA0380000000608010167519",
    "swift_code": "TESTBICX"
  }'
```

#### b. Invalid SMS Code
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "123",
    "email": "test.doctor@alaqa.net",
    "sms_code": "111111"
  }'
```

#### c. Expired Verification
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "expired_id",
    "email": "test.doctor@alaqa.net",
    "sms_code": "000000"
  }'
```

#### d. Invalid Verification ID
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "invalid_id",
    "email": "test.doctor@alaqa.net",
    "sms_code": "000000"
  }'
```

## Test Execution Steps

1. Start with a clean database state
2. Run the success case for initiation
3. Note down the verification_id from the response
4. Check SMS for verification code
5. Use these in the complete registration test
6. Verify the response contains doctor details
7. Try to login (should fail until approved)
8. Run error cases to verify proper error handling

## Expected Results

1. Success cases should:
   - Return 200/201 status codes
   - Provide verification ID for initiation
   - Show pending status after completion
   - Send actual SMS code

2. Error cases should:
   - Return appropriate 4xx status codes
   - Provide clear error messages
   - Not create partial records
   - Not send verification codes for invalid requests

## Monitoring

Monitor the following during tests:
1. SMS delivery logs
2. Server logs for errors
3. Database records
4. File storage for uploaded documents 