# Doctor Registration API Documentation

## Overview
The doctor registration process consists of 3 steps:
1. Initiate Registration (Email & Phone only)
2. Verify Phone Number (OTP Verification)
3. Complete Registration (Full Profile Details)

## Base URL
```
/api/v1/doctors/register/
```

## 1. Initiate Registration
Start the registration process by providing email and phone number.

### Endpoint
```
POST /api/v1/doctors/register/initiate/
```

### Request Body
```json
{
    "email": "doctor@example.com",
    "phone": "+966500000000"
}
```

### Validation Rules
- Email must be unique (not used by any existing user/doctor)
- Phone must start with '+'
- Both fields are required

### Success Response (200 OK)
```json
{
    "status": "success",
    "message": "Registration initiated successfully. Please verify your phone number.",
    "data": {
        "verification_id": "550e8400-e29b-41d4-a716-446655440000",
        "next_steps": [
            "Check your phone for the verification code.",
            "Use the code to verify your phone number.",
            "After verification, you can complete your profile."
        ]
    }
}
```

### Error Response (400 Bad Request)
```json
{
    "status": "error",
    "message": "Validation error",
    "errors": {
        "email": ["A user with this email already exists."],
        "phone": ["Phone number must start with '+'"]
    }
}
```

## 2. Verify Phone Number
Verify the phone number using the OTP code received.

### Endpoint
```
POST /api/v1/doctors/register/verify/
```

### Request Body
```json
{
    "verification_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "doctor@example.com",
    "sms_code": "123456"
}
```

### Notes
- In development mode, using `"sms_code": "000000"` will always succeed
- Maximum 3 verification attempts allowed

### Success Response (200 OK)
```json
{
    "status": "success",
    "message": "Phone number verified successfully.",
    "data": {
        "verification_id": "550e8400-e29b-41d4-a716-446655440000",
        "next_steps": [
            "Your phone number has been verified.",
            "Please complete your profile with additional details."
        ]
    }
}
```

### Error Response (400 Bad Request)
```json
{
    "status": "error",
    "message": "Invalid verification code",
    "data": {
        "attempts_remaining": 2
    }
}
```

## 3. Complete Registration
Complete the registration by providing all required doctor details.

### Endpoint
```
POST /api/v1/doctors/register/complete/
```

### Request Body
```json
{
    "verification_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "doctor@example.com",
    "name": "Dr. John Doe",
    "name_arabic": "د. جون دو",
    "sex": "male",
    "experience": 5,
    "category": "specialist",
    "language_in_sessions": "english",
    "license_number": "12345",
    "specialities": ["550e8400-e29b-41d4-a716-446655440000"],
    "profile_arabic": "نبذة عن الطبيب",
    "profile_english": "Doctor's profile",
    "password": "securepassword123",
    "confirm_password": "securepassword123",
    "terms_and_privacy_accepted": true,
    "account_holder_name": "John Doe",
    "account_number": "1234567890",
    "iban_number": "SA0380000000608010167519",
    "bank_name": "Sample Bank",
    "swift_code": "SAMPGB2L",
    "photo": "[binary file]",
    "license_document": "[binary file]",
    "qualification_document": "[binary file]",
    "additional_documents": "[binary file]"
}
```

### Required Files
- `photo`: Doctor's profile photo
- `license_document`: Medical license document
- `qualification_document`: Medical qualification document
- `additional_documents`: Optional additional documents

### Validation Rules
- All fields marked as required must be provided
- Passwords must match
- Terms and privacy must be accepted
- Bank details must follow format rules:
  - IBAN: 16-34 characters
  - SWIFT code: 8 or 11 characters
  - Account number: minimum 8 characters
- Specialties must be valid UUIDs of existing specialties

### Success Response (200 OK)
```json
{
    "status": "success",
    "message": "Registration completed successfully. Your profile is pending approval.",
    "data": {
        "doctor": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Dr. John Doe",
            "email": "doctor@example.com",
            // ... other doctor details
        },
        "next_steps": [
            "Your profile is being reviewed by our team.",
            "You will receive a notification once your account is approved.",
            "After approval, you can sign in using your email and password.",
            "For any questions, please contact our support team."
        ]
    }
}
```

### Error Response (400 Bad Request)
```json
{
    "status": "error",
    "message": "Validation error",
    "errors": {
        "specialities": ["One or more specialities do not exist."],
        "swift_code": ["SWIFT code must be either 8 or 11 characters"],
        "iban_number": ["IBAN must be between 16 and 34 characters"]
    }
}
```

## Rate Limiting
- Registration initiation: 100 requests per hour
- Verification attempts: 100 requests per hour

## Notes
1. All endpoints are unauthenticated (no token required)
2. Files should be sent as multipart/form-data
3. The registration process is sequential - each step must be completed before proceeding to the next
4. After successful registration, the doctor's account will be pending admin approval
5. The doctor can only log in after admin approval

## Field Requirements and Formats

### Doctor Information
| Field | Type | Required | Format/Rules |
|-------|------|----------|--------------|
| name | string | Yes | Full name in English |
| name_arabic | string | Yes | Full name in Arabic |
| sex | string | Yes | "male" or "female" |
| email | string | Yes | Valid email format |
| phone | string | Yes | Starts with '+' |
| experience | integer | Yes | Years of experience |
| category | string | Yes | "specialist", "consultant", etc. |
| language_in_sessions | string | Yes | "english", "arabic", "both" |
| license_number | string | Yes | Unique license number |
| specialities | array | Yes | Array of valid specialty UUIDs |
| profile_arabic | string | Yes | Profile description in Arabic |
| profile_english | string | Yes | Profile description in English |

### Bank Details
| Field | Type | Required | Format/Rules |
|-------|------|----------|--------------|
| account_holder_name | string | Yes | Full name as per bank account |
| account_number | string | Yes | Min 8 characters |
| iban_number | string | Yes | 16-34 characters, starts with country code |
| bank_name | string | Yes | Name of the bank |
| swift_code | string | Yes | 8 or 11 characters |

### Documents
| Field | Type | Required | Format/Rules |
|-------|------|----------|--------------|
| photo | file | Yes | Profile photo |
| license_document | file | Yes | Medical license |
| qualification_document | file | Yes | Medical qualification |
| additional_documents | file | No | Additional supporting documents |

### Security
| Field | Type | Required | Format/Rules |
|-------|------|----------|--------------|
| password | string | Yes | Strong password |
| confirm_password | string | Yes | Must match password |
| terms_and_privacy_accepted | boolean | Yes | Must be true | 