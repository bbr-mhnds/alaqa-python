# Doctor Working Hours API Documentation

## Overview
This API allows management of doctor working hours and schedules. It supports setting availability for each day of the week and defining specific time slots within available days.

## Base URL
`/api/v1`

## Authentication
All endpoints require authentication using JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. Get Doctor's Working Hours
Retrieves the working schedule for a specific doctor.

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
            "id": "uuid-here",
            "start_time": "09:00",
            "end_time": "12:00"
          },
          {
            "id": "uuid-here",
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
Updates the working schedule for a specific doctor.

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

**Success Response (200 OK):**
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
  "message": "Validation error",
  "errors": {
    "time_slots": ["Time must be in 24-hour format (HH:mm)"]
  }
}
```

2. Overlapping Slots (400 Bad Request):
```json
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "time_slots": ["Time slots cannot overlap"]
  }
}
```

3. Invalid Time Range (400 Bad Request):
```json
{
  "status": "error",
  "message": "Validation error",
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

## Implementation Notes

1. **Schedule Creation:**
   - When retrieving schedules, entries are automatically created for all days if they don't exist
   - Default value for `is_available` is `false` for newly created days
   - Existing time slots are automatically removed when updating a schedule

2. **Time Slots:**
   - All times must be in 24-hour format (HH:mm)
   - Times are stored in UTC
   - Frontend should handle timezone conversions
   - Time slots are automatically cleared when setting `is_available` to false

3. **Validation:**
   - Server performs comprehensive validation of time slots
   - Overlapping time slots are not allowed within the same day
   - End time must be after start time
   - Time format must be valid 24-hour format

4. **Security:**
   - All endpoints require authentication
   - Only authenticated users can view or modify schedules
   - Input validation and sanitization is performed on all inputs

## Example Usage

### Get Doctor's Schedule
```bash
curl -X GET \
  'http://your-api/api/v1/doctors/doctor@example.com/schedules/' \
  -H 'Authorization: Bearer your_token'
```

### Update Doctor's Schedule
```bash
curl -X POST \
  'http://your-api/api/v1/doctors/doctor@example.com/schedules/' \
  -H 'Authorization: Bearer your_token' \
  -H 'Content-Type: application/json' \
  -d '{
    "schedules": [
      {
        "day": "monday",
        "is_available": true,
        "time_slots": [
          {
            "start_time": "09:00",
            "end_time": "12:00"
          }
        ]
      }
    ]
  }'
``` 