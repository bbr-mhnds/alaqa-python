# Doctor Registration API Documentation

## Overview
The doctor registration process is a two-step verification system that uses SMS verification before completing the registration. After successful registration, the doctor's account will be pending admin approval.

## Base URL
```
/api/v1/doctors
```

## Endpoints

### 1. Initiate Registration
Start the registration process by submitting doctor details and receiving verification code.

**Endpoint:** `POST /register/initiate/`

**Request Body:**
```json
{
    "email": "doctor@example.com",
    "phone": "+966555555555"   // Format: +966XXXXXXXXX
}
```

**Success Response (200 OK):**
```json
{
    "status": "success",
    "message": "Verification code sent successfully",
    "data": {
        "verification_id": "123",
        "otp_id": "uuid"
    }
}
```

**Error Responses:**

1. Validation Error (400 Bad Request):
```json
{
    "status": "error",
    "message": "Validation error",
    "errors": {
        "email": ["A user with this email already exists."],
        "phone": ["Invalid phone number format"]
    }
}
```

2. Failed to Send Verification (400 Bad Request):
```json
{
    "status": "error",
    "message": "Failed to send verification code",
    "sms_error": "Failed to send SMS"
}
```

### 2. Complete Registration with Verification
Verify SMS code to complete the registration process.

**Endpoint:** `POST /register/verify/`

**Request Body:**
```json
{
    "verification_id": "123",
    "email": "doctor@example.com",
    "sms_code": "000000",     // 6-digit code received in SMS
    "name_arabic": "الطبيب محمد",
    "name": "Dr. Mohammed",
    "sex": "male",              // Options: male, female
    "phone": "+966555555555",   // Format: +966XXXXXXXXX
    "experience": "10 years",
    "category": "specialist",    // Options: consultant, specialist, general
    "language_in_sessions": "both",  // Options: arabic, english, both
    "license_number": "12345",
    "specialities": [1, 2],     // Array of specialty IDs
    "profile_arabic": "نبذة عن الطبيب",
    "profile_english": "Doctor profile",
    "license_document": [file],  // Required
    "qualification_document": [file],  // Required
    "additional_documents": [file],    // Optional
    "password": "secure_password",
    "confirm_password": "secure_password",
    "terms_and_privacy_accepted": true,
    "bank_name": "Bank Name",
    "account_holder_name": "Account Holder",
    "account_number": "12345678",
    "iban_number": "SA0380000000608010167519",
    "swift_code": "TESTBICX"
}
```

**Success Response (201 Created):**
```json
{
    "status": "success",
    "message": "Registration successful. Your account is pending approval.",
    "data": {
        "doctor": {
            "id": "uuid",
            "name": "Dr. Mohammed",
            "name_arabic": "الطبيب محمد",
            "email": "doctor@example.com",
            "phone": "+966555555555",
            "status": "pending",
            "specialities": [
                {
                    "id": 1,
                    "name": "Cardiology"
                }
            ],
            "created_at": "2025-01-20T22:45:00Z"
        },
        "next_steps": [
            "Your registration is being reviewed by our team.",
            "You will receive a notification once your account is approved.",
            "After approval, you can sign in using your email and password.",
            "For any questions, please contact our support team."
        ]
    }
}
```

**Error Responses:**

1. Missing Fields (400 Bad Request):
```json
{
    "status": "error",
    "message": "Missing required fields"
}
```

2. Invalid Verification (400 Bad Request):
```json
{
    "status": "error",
    "message": "Invalid verification code",
    "data": {
        "attempts_remaining": 2
    }
}
```

3. Expired Code (400 Bad Request):
```json
{
    "status": "error",
    "message": "Verification code has expired"
}
```

4. Invalid Verification ID (404 Not Found):
```json
{
    "status": "error",
    "message": "Invalid or expired verification ID"
}
```

## Implementation Notes

1. Phone Number Format:
   - Must start with country code (e.g., +966)
   - Must be at least 9 digits after country code
   - No special characters except leading '+'

2. SMS Verification:
   - Code is 6 digits
   - Valid for 10 minutes
   - Maximum 3 verification attempts
   - Code becomes invalid after successful verification

3. File Requirements:
   - License document: Required, PDF format
   - Qualification document: Required, PDF format
   - Additional documents: Optional, PDF format
   - Maximum file size: 5MB per file

4. Password Requirements:
   - Minimum 8 characters
   - Must contain at least one uppercase letter
   - Must contain at least one lowercase letter
   - Must contain at least one number
   - Must contain at least one special character

5. Bank Details:
   - IBAN: Must follow Saudi IBAN format (24 characters)
   - SWIFT code: Must be 8 or 11 characters
   - Account number: Minimum 8 digits

## Security Considerations

1. Use HTTPS for all API calls
2. Implement rate limiting for verification attempts
3. Validate file types and sizes before upload
4. Sanitize all user inputs
5. Implement proper session management
6. Use secure password hashing
7. Implement proper error handling
8. Log all registration attempts

## Testing

Test credentials are available for development:
- Email: test.doctor@zuwara.net
- Phone: +966555555555

## Support

For any issues or questions:
- Email: support@zuwara.net
- Phone: +966xxxxxxxxx
- Hours: 24/7 