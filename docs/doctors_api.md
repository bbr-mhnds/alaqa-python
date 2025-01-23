# Doctors API Documentation

## Overview
The Doctors API provides endpoints to manage doctor profiles, registration, and verification in the healthcare system.

## Base URL
```
https://api.alaqa.net/api/v1/doctors/
```

## Authentication
- Public endpoints (list, retrieve) are accessible without authentication
- Other endpoints require JWT authentication
- Admin endpoints require superuser privileges

## Endpoints

### 1. List Doctors
Get a paginated list of doctors. If no filters are applied, returns all doctors regardless of status.

```http
GET /api/v1/doctors/
```

#### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (pending, approved, rejected). Optional - if not provided, returns all statuses |
| specialty | UUID | Filter by specialty ID. Optional - if not provided, returns all specialties |
| search | string | Search in name, name_arabic, or email. Optional - if not provided, no search filter is applied |
| page | integer | Page number for pagination. Default: 1 |
| ordering | string | Sort field (prefix with - for descending). Default: -created_at |

#### Example Requests

1. Get all doctors (no filters):
```http
GET /api/v1/doctors/
```

2. Filter by status:
```http
GET /api/v1/doctors/?status=approved
```

3. Filter by specialty:
```http
GET /api/v1/doctors/?specialty=d59390ae-a401-417c-ba0f-71305dc0cf6e
```

4. Search with multiple filters:
```http
GET /api/v1/doctors/?status=approved&specialty=d59390ae-a401-417c-ba0f-71305dc0cf6e&search=john
```

#### Response
```json
{
    "status": "success",
    "data": {
        "doctors": [
            {
                "id": "uuid",
                "name_arabic": "د. جون دو",
                "name": "Dr. John Doe",
                "sex": "male",
                "email": "doctor@example.com",
                "phone": "+1234567890",
                "experience": "5",
                "category": "consultant",
                "language_in_sessions": "english",
                "license_number": "LIC123456",
                "specialities": [
                    {
                        "id": "uuid",
                        "title": "Specialty Name",
                        "title_arabic": "التخصص",
                        "description": "Specialty description",
                        "description_arabic": "وصف التخصص",
                        "icon": "url/to/icon.png"
                    }
                ],
                "profile_arabic": "نبذة عن الطبيب",
                "profile_english": "Doctor profile",
                "status": "approved",
                "photo": "url/to/photo.jpg",
                "created_at": "2024-01-22T12:00:00Z",
                "updated_at": "2024-01-22T12:00:00Z"
            }
        ],
        "pagination": {
            "total": 100,
            "pages": 10,
            "page": 1,
            "limit": 10
        }
    }
}
```

### 2. Get Single Doctor
Get detailed information about a specific doctor.

```http
GET /api/v1/doctors/{doctor_id}/
```

#### Response
```json
{
    "status": "success",
    "data": {
        "doctor": {
            "id": "uuid",
            "name_arabic": "د. جون دو",
            "name": "Dr. John Doe",
            "sex": "male",
            "email": "doctor@example.com",
            "phone": "+1234567890",
            "experience": "5",
            "category": "consultant",
            "language_in_sessions": "english",
            "license_number": "LIC123456",
            "specialities": [...],
            "profile_arabic": "نبذة عن الطبيب",
            "profile_english": "Doctor profile",
            "status": "approved",
            "photo": "url/to/photo.jpg",
            "created_at": "2024-01-22T12:00:00Z",
            "updated_at": "2024-01-22T12:00:00Z"
        }
    }
}
```

### 3. Doctor Registration
Two-step registration process for doctors.

#### Step 1: Initiate Registration
```http
POST /api/v1/doctors/register/initiate/
```

##### Request Body (multipart/form-data)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name_arabic | string | Yes | Doctor's name in Arabic |
| name | string | Yes | Doctor's name in English |
| sex | string | Yes | Gender (male/female) |
| email | string | Yes | Email address |
| phone | string | Yes | Phone number (+1234567890) |
| experience | string | Yes | Years of experience |
| category | string | Yes | Doctor category (consultant/specialist/general) |
| language_in_sessions | string | Yes | Preferred language (arabic/english/both) |
| license_number | string | Yes | Medical license number |
| specialities | array | Yes | Array of specialty UUIDs |
| profile_arabic | string | Yes | Profile description in Arabic |
| profile_english | string | Yes | Profile description in English |
| password | string | Yes | Account password |
| confirm_password | string | Yes | Password confirmation |
| license_document | file | Yes | Medical license document |
| qualification_document | file | Yes | Qualification certificates |
| additional_documents | file | No | Additional supporting documents |

##### Response
```json
{
    "status": "success",
    "message": "Verification codes sent successfully",
    "data": {
        "verification_id": "uuid",
        "sms": {
            "success": true,
            "message": "SMS sent successfully"
        }
    }
}
```

#### Step 2: Verify Registration
```http
POST /api/v1/doctors/register/verify/
```

##### Request Body
```json
{
    "email": "doctor@example.com",
    "sms_code": "123456"
}
```

##### Response
```json
{
    "status": "success",
    "message": "Registration successful. Your account is pending approval.",
    "data": {
        "doctor": {
            // Doctor details as above
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

### 4. Update Doctor Status (Admin Only)
Update the approval status of a doctor.

```http
PATCH /api/v1/doctors/{doctor_id}/status/
```

#### Request Body
```json
{
    "status": "approved",
    "rejection_reason": "Optional reason if rejected"
}
```

#### Response
```json
{
    "status": "success",
    "message": "Doctor status updated successfully",
    "data": {
        "doctor": {
            // Updated doctor details
        }
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "status": "error",
    "message": "Validation error",
    "errors": {
        "field": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "status": "error",
    "message": "Authentication credentials were not provided"
}
```

### 403 Forbidden
```json
{
    "status": "error",
    "message": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "status": "error",
    "message": "Doctor not found"
}
```

### 500 Server Error
```json
{
    "status": "error",
    "message": "Internal server error"
}
```

## Constants

### Sex Choices
- male: Male
- female: Female

### Status Choices
- pending: Pending
- approved: Approved
- rejected: Rejected

### Category Choices
- consultant: Consultant
- specialist: Specialist
- general: General Practitioner

### Language Choices
- arabic: Arabic
- english: English
- both: Both

## Notes
1. All timestamps are in UTC
2. File uploads should be in PDF format
3. Phone numbers must include country code
4. Passwords must meet minimum security requirements
5. Registration requires both SMS verification
6. Doctor accounts are inactive until approved by admin 