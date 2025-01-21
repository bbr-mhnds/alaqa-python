# Doctor Registration API Documentation

## Overview
The doctor registration process is a two-step verification system that requires both email and SMS verification before completing the registration. After successful registration, the doctor's account will be pending admin approval.

## Base URL
```
/api/v1/doctors
```

## Endpoints

### 1. Initiate Registration
Start the registration process by submitting doctor details and receiving verification codes.

**Endpoint:** `POST /register/initiate/`

**Request Body:**
```json
{
    "name_arabic": "الطبيب محمد",
    "name": "Dr. Mohammed",
    "sex": "male",              // Options: male, female
    "email": "doctor@example.com",
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
    "confirm_password": "secure_password"
}
```

**Success Response (200 OK):**
```json
{
    "status": "success",
    "message": "Verification codes sent successfully",
    "data": {
        "verification_id": "123",
        "email_sent": true,
        "sms_sent": true,
        "expires_at": "2025-01-20T22:45:00Z"
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
        "license_number": ["A doctor with this license number already exists."]
    }
}
```

2. Failed to Send Verification (400 Bad Request):
```json
{
    "status": "error",
    "message": "Failed to send verification codes",
    "email_error": "Failed to send email",
    "sms_error": "Failed to send SMS"
}
```

### 2. Complete Registration with Verification
Verify email and SMS codes to complete the registration process.

**Endpoint:** `POST /register/verify/`

**Request Body:**
```json
{
    "verification_id": "123",
    "email_code": "123456",  // 6-digit code received in email
    "sms_code": "789012"     // 6-digit code received in SMS
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
    "message": "Invalid verification codes",
    "email_verified": false,
    "phone_verified": false
}
```

3. Expired Codes (400 Bad Request):
```json
{
    "status": "error",
    "message": "Verification codes have expired"
}
```

4. Invalid Verification ID (404 Not Found):
```json
{
    "status": "error",
    "message": "Invalid verification ID"
}
```

## Important Notes

1. **File Upload Requirements:**
   - `license_document`: Required, max size 5MB, formats: PDF, JPG, PNG
   - `qualification_document`: Required, max size 5MB, formats: PDF, JPG, PNG
   - `additional_documents`: Optional, max size 5MB, formats: PDF, JPG, PNG

2. **Verification Process:**
   - Both email and SMS codes must be verified
   - Verification codes expire after 10 minutes
   - Different codes are sent for email and SMS
   - Maximum 3 verification attempts allowed

3. **Password Requirements:**
   - Minimum 8 characters
   - Must contain at least one uppercase letter
   - Must contain at least one number
   - Must contain at least one special character

4. **Phone Number Format:**
   - Must start with country code (+966)
   - Must be between 9-15 digits
   - No spaces or special characters except '+'

5. **Account Status:**
   - Initial status is 'pending'
   - Admin must approve account before doctor can sign in
   - Doctor will be notified via email upon approval/rejection

## Security Considerations

1. All endpoints use HTTPS
2. Files are scanned for viruses
3. Rate limiting applied: 5 requests per minute
4. Verification codes are hashed before storage
5. Registration data is encrypted at rest

## Testing

Test credentials are available for development:
- Email: test.doctor@zuwara.net
- Phone: +966555555555

## Support

For any issues or questions:
- Email: support@zuwara.net
- Phone: +966xxxxxxxxx
- Hours: 24/7 