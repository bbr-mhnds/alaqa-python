# Appointment API Documentation

## Overview
This API provides endpoints for managing appointments. Both creation and listing of appointments are public endpoints that don't require authentication.

## Endpoints

### 1. Create Appointment
- **URL**: `/api/v1/appointments/`
- **Method**: `POST`
- **Authentication**: Not required (Public endpoint)

#### Request Body

```json
{
    "doctor": 1,                    // Required: Doctor ID (integer)
    "specialties": [1, 2],          // Required: Array of Specialty IDs
    "specialist_category": "string", // Required: Category name
    "gender": "M",                  // Required: "M" or "F"
    "duration": "30",               // Required: Duration in minutes
    "language": "English",          // Required: Session language
    "phone_number": "1234567890",   // Required: At least 10 digits
    "slot_time": "2024-01-20T14:30:00Z"  // Required: ISO format datetime
}
```

#### Field Descriptions

| Field | Type | Description | Validation Rules |
|-------|------|-------------|-----------------|
| doctor | integer | ID of the doctor | Must exist in the system |
| specialties | array | List of specialty IDs | Doctor must be associated with at least one selected specialty |
| specialist_category | string | Category of the specialist | Required |
| gender | string | Gender preference | Must be "M" or "F" |
| duration | string | Duration of appointment | Required |
| language | string | Preferred language | Required |
| phone_number | string | Contact number | Must have at least 10 digits |
| slot_time | string | Appointment time | Must be in ISO format and in the future |

### 2. List Appointments
- **URL**: `/api/v1/appointments/`
- **Method**: `GET`
- **Authentication**: Not required (Public endpoint)

#### Query Parameters
- `doctor_id` (optional): Filter appointments by doctor ID
- `status` (optional): Filter appointments by status (`SCHEDULED`, `COMPLETED`, `CANCELLED`)
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

#### Response
```json
{
    "count": 10,
    "next": "http://api.example.com/api/v1/appointments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "doctor": 1,
            "specialties": [1, 2],
            "specialist_category": "string",
            "gender": "M",
            "duration": "30",
            "language": "English",
            "phone_number": "1234567890",
            "slot_time": "2024-01-20T14:30:00Z",
            "video_token": "generated_token_string",
            "status": "SCHEDULED",
            "created_at": "2024-01-19T10:00:00Z"
        }
        // ... more appointments
    ]
}
```

## Success Responses

### Create Appointment Success
**Status Code**: `201 Created`

```json
{
    "id": 1,
    "doctor": 1,
    "specialties": [1, 2],
    "specialist_category": "string",
    "gender": "M",
    "duration": "30",
    "language": "English",
    "phone_number": "1234567890",
    "slot_time": "2024-01-20T14:30:00Z",
    "video_token": "generated_token_string",
    "status": "SCHEDULED",
    "created_at": "2024-01-19T10:00:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique appointment identifier |
| video_token | string | Generated video call token |
| status | string | Always "SCHEDULED" for new appointments |
| created_at | string | Timestamp of creation |
| *other fields* | various | Same as request body |

## Error Responses

### Validation Error
**Status Code**: `400 Bad Request`

```json
{
    "field_name": [
        "Error message"
    ]
}
```

Common validation errors:
- Invalid doctor ID
- Invalid specialty IDs
- Doctor not associated with specialties
- Invalid phone number format
- Invalid datetime format

### Video Token Generation Error
**Status Code**: `500 Internal Server Error`

```json
{
    "error": "Failed to generate video token"
}
```

## Example Requests

### Create Appointment
```bash
curl -X POST \
  'http://localhost:8000/api/v1/appointments/' \
  -H 'Content-Type: application/json' \
  -d '{
    "doctor": 1,
    "specialties": [1, 2],
    "specialist_category": "Cardiologist",
    "gender": "M",
    "duration": "30",
    "language": "English",
    "phone_number": "1234567890",
    "slot_time": "2024-01-20T14:30:00Z"
}'
```

### List Appointments
```bash
# List all appointments
curl 'http://localhost:8000/api/v1/appointments/'

# Filter by doctor
curl 'http://localhost:8000/api/v1/appointments/?doctor_id=1'

# Filter by status
curl 'http://localhost:8000/api/v1/appointments/?status=SCHEDULED'

# Paginated results
curl 'http://localhost:8000/api/v1/appointments/?page=1&limit=10'
```

## Notes

1. The video token is automatically generated during appointment creation using a public token generation service
2. All datetime values should be in ISO 8601 format
3. Phone numbers are automatically cleaned to remove non-digit characters
4. The appointment status is automatically set to "SCHEDULED"
5. No authentication is required for creating or listing appointments
6. Other operations (update, delete, cancel) still require authentication 