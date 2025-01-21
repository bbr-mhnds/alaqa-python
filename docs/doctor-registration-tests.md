# Doctor Registration API Tests

## Prerequisites
- Install curl
- Have test files ready for document upload:
  - `license.pdf`
  - `qualification.pdf`

## Test Cases

### 1. Initiate Registration - Success Case
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: multipart/form-data" \
  -F "name_arabic=الطبيب محمد" \
  -F "name=Dr. Mohammed" \
  -F "sex=male" \
  -F "email=test.doctor@zuwara.net" \
  -F "phone=+966555555555" \
  -F "experience=10 years" \
  -F "category=specialist" \
  -F "language_in_sessions=both" \
  -F "license_number=12345" \
  -F "specialities=[1,2]" \
  -F "profile_arabic=نبذة عن الطبيب" \
  -F "profile_english=Doctor profile" \
  -F "license_document=@license.pdf" \
  -F "qualification_document=@qualification.pdf" \
  -F "password=Test@123" \
  -F "confirm_password=Test@123"
```

### 2. Initiate Registration - Validation Error Cases

#### a. Existing Email
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: multipart/form-data" \
  -F "email=existing.doctor@zuwara.net" \
  # ... (other fields)
```

#### b. Invalid Phone Format
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: multipart/form-data" \
  -F "phone=123456789" \
  # ... (other fields)
```

#### c. Missing Required Documents
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/initiate/ \
  -H "Content-Type: multipart/form-data" \
  # ... (without license_document)
```

### 3. Complete Registration - Success Case
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "123",
    "email_code": "123456",
    "sms_code": "789012"
  }'
```

### 4. Complete Registration - Error Cases

#### a. Invalid Verification Codes
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "123",
    "email_code": "000000",
    "sms_code": "000000"
  }'
```

#### b. Expired Verification
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "expired_id",
    "email_code": "123456",
    "sms_code": "789012"
  }'
```

#### c. Invalid Verification ID
```bash
curl -X POST http://localhost:8000/api/v1/doctors/register/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "verification_id": "invalid_id",
    "email_code": "123456",
    "sms_code": "789012"
  }'
```

## Test Execution Steps

1. Start with a clean database state
2. Run the success case for initiation
3. Note down the verification_id from the response
4. Check email and SMS for verification codes
5. Use these in the complete registration test
6. Verify the response contains doctor details
7. Try to login (should fail until approved)
8. Run error cases to verify proper error handling

## Expected Results

1. Success cases should:
   - Return 200/201 status codes
   - Provide verification ID for initiation
   - Show pending status after completion
   - Send actual email and SMS codes

2. Error cases should:
   - Return appropriate 4xx status codes
   - Provide clear error messages
   - Not create partial records
   - Not send verification codes for invalid requests

## Monitoring

Monitor the following during tests:
1. Email delivery logs
2. SMS delivery logs
3. Server logs for errors
4. Database records
5. File storage for uploaded documents 