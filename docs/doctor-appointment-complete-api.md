# Doctor Appointment Completion API Documentation

This document describes the API endpoint for marking a doctor's appointment as completed.

## Base URL
```
/api/v1/appointments/{appointment_id}/complete/
```

## Authentication
All endpoints require authentication using JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Complete Appointment
Marks a specific appointment as completed.

**Request**
```http
POST /api/v1/appointments/{appointment_id}/complete/
```

**URL Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| appointment_id | integer | The unique identifier of the appointment |

**Request Body**
```json
{
    "completion_notes": "string?", // Optional completion notes
    "duration_minutes": "integer?", // Optional actual duration in minutes
    "completion_time": "string?"    // Optional completion timestamp (ISO format)
}
```

**Response**
```json
{
    "status": "success",
    "data": {
        "id": "integer",
        "status": "COMPLETED",
        "completion_notes": "string",
        "scheduled_time": "string",
        "completion_time": "string",
        "duration_minutes": "integer",
        "specialist_category": "string",
        "patient_id": "string",
        "updated_at": "string"
    }
}
```

**Status Codes**
| Status Code | Description |
|-------------|-------------|
| 200 | Appointment marked as completed successfully |
| 400 | Invalid request or appointment cannot be completed |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Not authorized to complete this appointment |
| 404 | Appointment not found |
| 409 | Appointment already completed or cancelled |
| 500 | Internal server error |

**Error Response**
```json
{
    "status": "error",
    "message": "string",
    "errors": {
        "field_name": ["error_message"]
    }
}
```

## Validation Rules

1. Only scheduled appointments can be marked as completed
2. Only the assigned doctor can complete their appointments
3. Completion time cannot be in the future
4. Completion time must be after the scheduled time
5. Duration minutes must be greater than 0 if provided

## State Transitions
```
SCHEDULED -> COMPLETED
```

Other states (CANCELLED, IN_PROGRESS) cannot transition to COMPLETED.

## Example Usage

### Request
```bash
curl -X POST \
  "https://api.example.com/api/v1/appointments/123/complete/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "completion_notes": "Session completed successfully",
    "duration_minutes": 45,
    "completion_time": "2024-02-20T15:30:00Z"
}'
```

### Success Response
```json
{
    "status": "success",
    "data": {
        "id": 123,
        "status": "COMPLETED",
        "completion_notes": "Session completed successfully",
        "scheduled_time": "2024-02-20T15:00:00Z",
        "completion_time": "2024-02-20T15:30:00Z",
        "duration_minutes": 45,
        "specialist_category": "psychiatrist",
        "patient_id": "PAT123",
        "updated_at": "2024-02-20T15:30:00Z"
    }
}
```

### Error Response Example
```json
{
    "status": "error",
    "message": "Invalid appointment completion request",
    "errors": {
        "completion_time": ["Completion time cannot be in the future"],
        "duration_minutes": ["Duration must be greater than 0"]
    }
}
```

## Implementation Notes

1. The endpoint should validate:
   - Appointment exists and belongs to the authenticated doctor
   - Current appointment status allows completion
   - All provided data is valid
   - No conflicting appointments exist

2. The endpoint should:
   - Update appointment status
   - Record completion time and duration
   - Store completion notes if provided
   - Update any related records (e.g., patient history)
   - Send notifications if required

3. Security considerations:
   - Validate JWT token
   - Check doctor's permissions
   - Sanitize and validate all inputs
   - Rate limit requests
   - Log all completion attempts

4. Database updates:
   - Use transactions for data consistency
   - Update appointment status atomically
   - Maintain audit trail of changes

5. Notifications:
   - Notify patient of completion
   - Update any scheduling systems
   - Trigger any follow-up workflows

## Rate Limiting
- Maximum 10 requests per minute per doctor
- 429 Too Many Requests response when limit exceeded

## Caching
- Response should include appropriate cache headers
- GET requests may be cached
- POST requests should not be cached 
