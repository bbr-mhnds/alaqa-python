# Video Calls API Documentation

## Overview
The Video Calls API provides endpoints for managing real-time video consultations between doctors and patients using Agora's video calling platform.

## Base URL
```
/api/v1/video/
```

## Authentication
All endpoints require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List Video Calls
Get a list of video calls for the authenticated user (doctor or patient).

**Request**
```http
GET /api/v1/video/video-calls/
```

**Response**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "channel_name": "call_1704436789_5678",
            "doctor": 1,
            "patient": 1,
            "doctor_details": {
                "id": 1,
                "user": {
                    "email": "doctor@example.com",
                    "full_name": "Dr. John Doe"
                },
                // ... other doctor details
            },
            "patient_details": {
                "id": 1,
                "user": {
                    "email": "patient@example.com",
                    "full_name": "Jane Smith"
                },
                // ... other patient details
            },
            "status": "scheduled",
            "scheduled_time": "2024-01-05T10:00:00Z",
            "started_at": null,
            "ended_at": null,
            "created_at": "2024-01-05T08:00:00Z",
            "updated_at": "2024-01-05T08:00:00Z"
        }
    ]
}
```

### 2. Create Video Call
Schedule a new video call between a doctor and patient.

**Request**
```http
POST /api/v1/video/video-calls/
Content-Type: application/json

{
    "doctor": 1,
    "patient": 1,
    "scheduled_time": "2024-01-05T10:00:00Z"
}
```

**Validation Rules**
- Scheduled time must be in the future
- Doctor and patient cannot be the same user
- No overlapping calls within 30 minutes for either doctor or patient
- Both doctor and patient must be valid and active users

**Response**
```json
{
    "id": 1,
    "channel_name": "call_1704436789_5678",
    "doctor": 1,
    "patient": 1,
    "doctor_details": { ... },
    "patient_details": { ... },
    "status": "scheduled",
    "scheduled_time": "2024-01-05T10:00:00Z",
    "started_at": null,
    "ended_at": null,
    "created_at": "2024-01-05T08:00:00Z",
    "updated_at": "2024-01-05T08:00:00Z"
}
```

### 3. Get Video Call Details
Retrieve details of a specific video call.

**Request**
```http
GET /api/v1/video/video-calls/{id}/
```

**Response**
```json
{
    "id": 1,
    "channel_name": "call_1704436789_5678",
    "doctor": 1,
    "patient": 1,
    "doctor_details": { ... },
    "patient_details": { ... },
    "status": "scheduled",
    "scheduled_time": "2024-01-05T10:00:00Z",
    "started_at": null,
    "ended_at": null,
    "created_at": "2024-01-05T08:00:00Z",
    "updated_at": "2024-01-05T08:00:00Z"
}
```

### 4. Join Video Call
Join a video call and get Agora credentials.

**Request**
```http
POST /api/v1/video/video-calls/{id}/join/
```

**Validation Rules**
- User must be either the doctor or patient of the call
- Call must be scheduled within the next 15 minutes
- Call status must be 'scheduled' or 'ongoing'
- Call must not be cancelled or completed

**Response**
```json
{
    "channel_name": "call_1704436789_5678",
    "token": "006YOUR_AGORA_TOKEN...",
    "uid": 123,
    "expiration_time": "2024-01-05T11:00:00Z"
}
```

### 5. End Video Call
End an ongoing video call.

**Request**
```http
POST /api/v1/video/video-calls/{id}/end/
```

**Validation Rules**
- User must be either the doctor or patient of the call
- Call status must be 'ongoing'

**Response**
```json
{
    "id": 1,
    "channel_name": "call_1704436789_5678",
    "doctor": 1,
    "patient": 1,
    "doctor_details": { ... },
    "patient_details": { ... },
    "status": "completed",
    "scheduled_time": "2024-01-05T10:00:00Z",
    "started_at": "2024-01-05T10:00:00Z",
    "ended_at": "2024-01-05T10:30:00Z",
    "created_at": "2024-01-05T08:00:00Z",
    "updated_at": "2024-01-05T10:30:00Z"
}
```

### 6. Cancel Video Call
Cancel a scheduled video call.

**Request**
```http
POST /api/v1/video/video-calls/{id}/cancel/
```

**Validation Rules**
- User must be either the doctor or patient of the call
- Call status must be 'scheduled'

**Response**
```json
{
    "id": 1,
    "channel_name": "call_1704436789_5678",
    "doctor": 1,
    "patient": 1,
    "doctor_details": { ... },
    "patient_details": { ... },
    "status": "cancelled",
    "scheduled_time": "2024-01-05T10:00:00Z",
    "started_at": null,
    "ended_at": null,
    "created_at": "2024-01-05T08:00:00Z",
    "updated_at": "2024-01-05T10:30:00Z"
}
```

## Models

### VideoCall
| Field | Type | Description |
|-------|------|-------------|
| channel_name | CharField | Unique identifier for the Agora channel |
| doctor | ForeignKey | Reference to the Doctor model |
| patient | ForeignKey | Reference to the Patient model |
| status | CharField | Call status (scheduled/ongoing/completed/cancelled) |
| scheduled_time | DateTimeField | When the call is scheduled to start |
| started_at | DateTimeField | When the call actually started |
| ended_at | DateTimeField | When the call ended |
| created_at | DateTimeField | When the record was created |
| updated_at | DateTimeField | When the record was last updated |

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (no authentication)
- 403: Forbidden (no permission)
- 404: Not Found
- 500: Internal Server Error

## Error Responses
The API returns detailed error messages for validation failures:

```json
{
    "error": "You are not authorized to access this call"
}
```

```json
{
    "error": "This call is not scheduled to start yet"
}
```

```json
{
    "error": "There is already a scheduled call within 30 minutes of this time"
}
```

## Frontend Integration

### Example: Creating a Video Call
```javascript
const createVideoCall = async (doctorId, patientId, scheduledTime) => {
  try {
    const response = await fetch('/api/v1/video/video-calls/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${yourAuthToken}`
      },
      body: JSON.stringify({
        doctor: doctorId,
        patient: patientId,
        scheduled_time: scheduledTime
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create video call');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating video call:', error);
    throw error;
  }
};
```

### Example: Joining a Video Call
```javascript
const joinVideoCall = async (callId) => {
  try {
    const response = await fetch(`/api/v1/video/video-calls/${callId}/join/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${yourAuthToken}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to join video call');
    }
    
    const { channel_name, token, uid } = await response.json();
    
    // Initialize Agora client
    const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
    await client.join(AGORA_APP_ID, channel_name, token, uid);
    
    // ... handle video streaming
    
    return client;
  } catch (error) {
    console.error('Error joining video call:', error);
    throw error;
  }
};
```

### Example: Ending a Video Call
```javascript
const endVideoCall = async (callId) => {
  try {
    const response = await fetch(`/api/v1/video/video-calls/${callId}/end/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${yourAuthToken}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to end video call');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error ending video call:', error);
    throw error;
  }
};
```

### Example: Cancelling a Video Call
```javascript
const cancelVideoCall = async (callId) => {
  try {
    const response = await fetch(`/api/v1/video/video-calls/${callId}/cancel/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${yourAuthToken}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to cancel video call');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error cancelling video call:', error);
    throw error;
  }
};
```

## Environment Setup
Add these variables to your `.env` file:
```
AGORA_APP_ID=your_agora_app_id
AGORA_APP_CERTIFICATE=your_agora_certificate
```

## Security Considerations
1. All endpoints require authentication
2. Users can only access their own video calls
3. Only participants can join their scheduled calls
4. Agora tokens expire after 1 hour
5. Channel names are randomly generated
6. Sensitive data is not exposed in responses
7. Validation prevents scheduling conflicts
8. Time-based restrictions on joining calls

## Rate Limiting
The API uses Django REST framework's default rate limiting settings. Consider implementing custom rate limiting for production use.

## Websocket Events (Future Enhancement)
Consider implementing these WebSocket events for real-time updates:
- `call.started`: When a call begins
- `call.ended`: When a call ends
- `call.cancelled`: When a call is cancelled
- `participant.joined`: When a participant joins
- `participant.left`: When a participant leaves

## Testing
Run the test suite:
```bash
python manage.py test video_calls
```

The test suite includes:
- Creating video calls
- Joining calls as doctor/patient
- Ending calls
- Cancelling calls
- Validation rules
- Authorization checks
- Error handling 