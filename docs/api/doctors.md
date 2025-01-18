# Doctors API Documentation

> **Important**: All API endpoints must include a trailing slash (/) to prevent 301 redirects.

## Endpoints Overview

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/doctors/` | List all doctors | No (Public) |
| GET | `/api/v1/doctors/{id}/` | Get doctor details | No (Public) |
| POST | `/api/v1/doctors/` | Create new doctor | Yes |
| PUT | `/api/v1/doctors/{id}/` | Update doctor (full) | Yes |
| PATCH | `/api/v1/doctors/{id}/` | Update doctor (partial) | Yes |
| DELETE | `/api/v1/doctors/{id}/` | Delete doctor | Yes |
| PATCH | `/api/v1/doctors/{id}/status/` | Update doctor status | Yes |

## Examples

✅ Correct URLs:
```
/api/v1/doctors/
/api/v1/doctors/?status=approved
/api/v1/doctors/123/
/api/v1/doctors/123/status/
```

❌ Incorrect URLs (will cause 301 redirects):
```
/api/v1/doctors
/api/v1/doctors?status=approved
/api/v1/doctors/123
/api/v1/doctors/123/status
```

## List Doctors

Get a paginated list of doctors.

**Endpoint:** `GET /api/v1/doctors/`  
**Authentication:** Not required (Public endpoint)

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by doctor status |
| specialty | UUID | Filter by specialty ID |
| search | string | Search in name, name_arabic, or email |
| ordering | string | Order by field (e.g., 'created_at', '-created_at', 'name', '-name') |
| page | integer | Page number for pagination |
| page_size | integer | Number of items per page |

### Success Response

```json
{
    "status": "success",
    "data": {
        "doctors": [
            {
                "id": "uuid",
                "name": "Dr. John Doe",
                "name_arabic": "د. جون دو",
                "sex": "male",
                "email": "john.doe@example.com",
                "phone": "+966500000001",
                "experience": "20 years of experience...",
                "category": "consultant",
                "language_in_sessions": "both",
                "license_number": "PSY001",
                "profile_english": "Detailed profile in English...",
                "profile_arabic": "الملف الشخصي باللغة العربية...",
                "status": "approved",
                "specialities": [
                    {
                        "id": "uuid",
                        "title": "Psychiatry",
                        "title_ar": "الطب النفسي"
                        // ... other specialty fields
                    }
                ],
                "created_at": "2024-03-15T12:00:00Z",
                "updated_at": "2024-03-15T12:00:00Z"
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

### Error Response

```json
{
    "status": "error",
    "message": "Error message details"
}
```

## Get Doctor Details

Get detailed information about a specific doctor.

**Endpoint:** `GET /api/v1/doctors/{id}/`  
**Authentication:** Not required (Public endpoint)

### Success Response

```json
{
    "status": "success",
    "data": {
        "doctor": {
            "id": "uuid",
            "name": "Dr. John Doe",
            "name_arabic": "د. جون دو",
            "sex": "male",
            "email": "john.doe@example.com",
            "phone": "+966500000001",
            "experience": "20 years of experience...",
            "category": "consultant",
            "language_in_sessions": "both",
            "license_number": "PSY001",
            "profile_english": "Detailed profile in English...",
            "profile_arabic": "الملف الشخصي باللغة العربية...",
            "status": "approved",
            "specialities": [
                {
                    "id": "uuid",
                    "title": "Psychiatry",
                    "title_ar": "الطب النفسي"
                    // ... other specialty fields
                }
            ],
            "created_at": "2024-03-15T12:00:00Z",
            "updated_at": "2024-03-15T12:00:00Z"
        }
    }
}
```

### Error Response

```json
{
    "status": "error",
    "message": "Doctor not found"
}
```

## Create Doctor

Create a new doctor profile.

**Endpoint:** `POST /api/v1/doctors/`  
**Authentication:** Required

### Request Body

```json
{
    "name": "Dr. John Doe",
    "name_arabic": "د. جون دو",
    "sex": "male",
    "email": "john.doe@example.com",
    "phone": "+966500000001",
    "experience": "20 years of experience...",
    "category": "consultant",
    "language_in_sessions": "both",
    "license_number": "PSY001",
    "profile_english": "Detailed profile in English...",
    "profile_arabic": "الملف الشخصي باللغة العربية...",
    "status": "pending",
    "account_holder_name": "John Doe",
    "account_number": "1234567890",
    "iban_number": "SA0380000000608010167519",
    "specialities": ["uuid1", "uuid2"]
}
```

### Success Response

```json
{
    "status": "success",
    "message": "Doctor created successfully",
    "data": {
        "doctor": {
            // ... doctor object (same as GET response)
        }
    }
}
```

### Error Response

```json
{
    "status": "error",
    "message": "Validation error details"
}
```

## Update Doctor

Update an existing doctor's information.

**Endpoint:** `PUT /api/v1/doctors/{id}/` or `PATCH /api/v1/doctors/{id}/`  
**Authentication:** Required

### Request Body

For PUT (full update), include all fields. For PATCH (partial update), include only fields to be updated.

```json
{
    "name": "Dr. John Doe",
    "name_arabic": "د. جون دو",
    // ... other fields to update
}
```

### Success Response

```json
{
    "status": "success",
    "message": "Doctor updated successfully",
    "data": {
        "doctor": {
            // ... updated doctor object
        }
    }
}
```

### Error Response

```json
{
    "status": "error",
    "message": "Error details"
}
```

## Delete Doctor

Delete a doctor profile.

**Endpoint:** `DELETE /api/v1/doctors/{id}/`  
**Authentication:** Required

### Success Response

```json
{
    "status": "success",
    "message": "Doctor deleted successfully"
}
```

### Error Response

```json
{
    "status": "error",
    "message": "Doctor not found"
}
```

## Update Doctor Status

Update a doctor's status.

**Endpoint:** `PATCH /api/v1/doctors/{id}/status/`  
**Authentication:** Required

### Request Body

```json
{
    "status": "approved"
}
```

### Success Response

```json
{
    "status": "success",
    "message": "Doctor status updated successfully",
    "data": {
        "doctor": {
            // ... updated doctor object
        }
    }
}
```

### Error Response

```json
{
    "status": "error",
    "message": "Error details"
}
```

## Status Values

Available status values for doctors:
- `pending`: Initial status when doctor is created
- `approved`: Doctor is approved and visible to public
- `rejected`: Doctor application is rejected
- `suspended`: Doctor account is temporarily suspended

## Field Descriptions

| Field | Type | Description | Required |
|-------|------|-------------|-----------|
| name | string | Doctor's name in English | Yes |
| name_arabic | string | Doctor's name in Arabic | Yes |
| sex | string | Gender (male/female) | Yes |
| email | string | Contact email | Yes |
| phone | string | Contact phone number | Yes |
| experience | text | Professional experience description | Yes |
| category | string | Doctor's category (consultant/specialist) | Yes |
| language_in_sessions | string | Session language preference (english/arabic/both) | Yes |
| license_number | string | Professional license number | Yes |
| profile_english | text | Detailed profile in English | Yes |
| profile_arabic | text | Detailed profile in Arabic | Yes |
| status | string | Account status | Yes |
| account_holder_name | string | Bank account holder name | Yes |
| account_number | string | Bank account number | Yes |
| iban_number | string | IBAN number | Yes |
| specialities | array | List of specialty UUIDs | Yes | 