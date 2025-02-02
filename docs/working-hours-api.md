# Working Hours API Documentation

## Base URL
`/api/v1`

## Endpoints

### 1. Get Doctor's Working Hours
Retrieves the working hours schedule for a specific doctor.

**Endpoint:** `GET /doctors/{email}/schedules/`

**Parameters:**
- `email` (string, required): The doctor's email address

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "schedules": [
      {
        "day": "monday",
        "is_available": true,
        "time_slots": [
          {
            "id": "1",
            "start_time": "09:00",
            "end_time": "12:00"
          },
          {
            "id": "2",
            "start_time": "14:00",
            "end_time": "17:00"
          }
        ]
      },
      {
        "day": "tuesday",
        "is_available": true,
        "time_slots": [
          {
            "id": "3",
            "start_time": "10:00",
            "end_time": "15:00"
          }
        ]
      }
      // ... other days
    ]
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "status": "error",
  "message": "Doctor not found"
}
```

### 2. Update Doctor's Working Hours
Updates the working hours schedule for a specific doctor.

**Endpoint:** `POST /doctors/{email}/schedules/`

**Parameters:**
- `email` (string, required): The doctor's email address

**Request Body:**
```json
{
  "schedules": [
    {
      "day": "monday",
      "is_available": true,
      "time_slots": [
        {
          "start_time": "09:00",
          "end_time": "12:00"
        },
        {
          "start_time": "14:00",
          "end_time": "17:00"
        }
      ]
    },
    {
      "day": "tuesday",
      "is_available": false,
      "time_slots": []
    }
    // ... other days
  ]
}
```

**Validation Rules:**
1. `day` must be one of: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
2. `is_available` must be boolean
3. `time_slots` array is required when `is_available` is true
4. `start_time` and `end_time` must be in 24-hour format "HH:mm"
5. `end_time` must be after `start_time`
6. Time slots must not overlap for the same day
7. Time format must match pattern: ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Working hours updated successfully",
  "data": {
    "schedules": [
      // ... updated schedules (same format as request)
    ]
  }
}
```

**Error Responses:**

1. Invalid Time Format (400 Bad Request):
```json
{
  "status": "error",
  "message": "Invalid time format",
  "errors": {
    "time_slots": ["Time must be in 24-hour format (HH:mm)"]
  }
}
```

2. Overlapping Slots (400 Bad Request):
```json
{
  "status": "error",
  "message": "Invalid time slots",
  "errors": {
    "time_slots": ["Time slots cannot overlap"]
  }
}
```

3. Invalid Time Range (400 Bad Request):
```json
{
  "status": "error",
  "message": "Invalid time range",
  "errors": {
    "time_slots": ["End time must be after start time"]
  }
}
```

4. Doctor Not Found (404 Not Found):
```json
{
  "status": "error",
  "message": "Doctor not found"
}
```

## Data Models

### Schedule
```typescript
interface Schedule {
  day: "monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday" | "sunday";
  is_available: boolean;
  time_slots: TimeSlot[];
}
```

### TimeSlot
```typescript
interface TimeSlot {
  id?: string;          // Required for existing slots, optional for new ones
  start_time: string;   // Format: "HH:mm"
  end_time: string;     // Format: "HH:mm"
}
```

## Notes

1. **Authentication:**
   - All endpoints require authentication
   - Must include valid JWT token in Authorization header
   - Token must belong to the doctor being modified or an admin

2. **Time Slots:**
   - All times are in 24-hour format
   - Times are stored and returned in UTC
   - Frontend should handle timezone conversions
   - Minimum slot duration: 30 minutes
   - Maximum slots per day: 10

3. **Validation:**
   - Server performs all time slot validation
   - Overlapping slots are not allowed
   - End time must be after start time
   - Time slots must be within same day (00:00 - 23:59)

4. **Performance:**
   - Responses are cached for 5 minutes
   - Rate limit: 100 requests per minute
   - Bulk updates should be done in a single request

5. **Security:**
   - Input sanitization is performed
   - CORS is enabled for approved domains
   - Rate limiting is applied per IP and per user 