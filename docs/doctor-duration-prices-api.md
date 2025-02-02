# Doctor Duration Prices API Documentation

This document describes the API endpoints for managing doctor consultation duration prices and appointment settings.

## Base URLs
```
/api/v1/doctors/{doctor_email}/price-categories/
/api/v1/doctors/{doctor_email}/duration-prices/
```

## Authentication
All endpoints require authentication using JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### List Price Categories and Settings
Retrieves all price categories, duration-based prices, and appointment settings for a specific doctor.

**Request**
```http
GET /api/v1/doctors/{doctor_email}/price-categories/
```
or
```http
GET /api/v1/doctors/{doctor_email}/duration-prices/
```

**Response**
```json
{
    "categories": [
        {
            "type": "initial_consultation",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                }
            ]
        }
    ],
    "accept_instant_appointment": true,
    "accept_tamkeen_clinics": true
}
```

### Create/Update Price Categories and Settings
Creates or updates multiple price categories, duration-based prices, and appointment settings for a doctor.

**Request**
```http
POST /api/v1/doctors/{doctor_email}/price-categories/
```
or
```http
POST /api/v1/doctors/{doctor_email}/duration-prices/
```

**Request Body**
```json
{
    "categories": [
        {
            "type": "initial_consultation",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                },
                {
                    "duration": 45,
                    "price": 149.99
                },
                {
                    "duration": 60,
                    "price": 199.99
                },
                {
                    "duration": 120,
                    "price": 300.00
                }
            ]
        },
        {
            "type": "follow_up",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                },
                {
                    "duration": 45,
                    "price": 149.99
                },
                {
                    "duration": 60,
                    "price": 199.99
                },
                {
                    "duration": 120,
                    "price": 300.00
                }
            ]
        }
    ],
    "accept_instant_appointment": true,
    "accept_tamkeen_clinics": true
}
```

**Response**
```json
{
    "categories": [
        {
            "type": "initial_consultation",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                },
                {
                    "duration": 45,
                    "price": 149.99
                },
                {
                    "duration": 60,
                    "price": 199.99
                },
                {
                    "duration": 120,
                    "price": 300.00
                }
            ]
        },
        {
            "type": "follow_up",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                },
                {
                    "duration": 45,
                    "price": 149.99
                },
                {
                    "duration": 60,
                    "price": 199.99
                },
                {
                    "duration": 120,
                    "price": 300.00
                }
            ]
        }
    ],
    "accept_instant_appointment": true,
    "accept_tamkeen_clinics": true
}
```

### Update Single Price Category
Updates an existing price category and its duration-based prices.

**Request**
```http
PUT /api/v1/doctors/{doctor_email}/price-categories/{category_id}/
```
or
```http
PUT /api/v1/doctors/{doctor_email}/duration-prices/{category_id}/
```

**Request Body**
```json
{
    "is_enabled": true,
    "entries": [
        {
            "duration": 30,
            "price": 50.00
        }
    ]
}
```

### Delete Price Category
Deletes a price category and all its duration-based prices.

**Request**
```http
DELETE /api/v1/doctors/{doctor_email}/price-categories/{category_id}/
```
or
```http
DELETE /api/v1/doctors/{doctor_email}/duration-prices/{category_id}/
```

## Data Models

### Price Category Types
```typescript
enum PriceCategoryType {
    INITIAL_CONSULTATION = "initial_consultation",
    FOLLOW_UP = "follow_up",
    EMERGENCY = "emergency",
    SPECIALIST = "specialist"
}
```

### Price Category
```typescript
interface PriceCategory {
    type: PriceCategoryType;
    is_enabled: boolean;
    entries: DurationPrice[];
}
```

### Duration Price
```typescript
interface DurationPrice {
    duration: number;  // in minutes
    price: number;     // decimal
}
```

### Doctor Settings
```typescript
interface DoctorSettings {
    accept_instant_appointment: boolean;  // Whether to accept instant appointments
    accept_tamkeen_clinics: boolean;     // Whether to accept Tamkeen clinic patients
}
```

## Validation Rules

### Duration Price Entries
- Duration must be at least 5 minutes
- Duration must be in increments of 5 minutes
- Price cannot be negative
- Maximum 10 entries allowed per category
- No duplicate durations allowed within a category

### Price Categories
- Each doctor can have only one category of each type
- At least one duration-price entry is required when category is enabled
- When category is disabled, all duration-price entries are removed

### Appointment Settings
- Both `accept_instant_appointment` and `accept_tamkeen_clinics` are optional
- When not provided, existing values are preserved
- Both fields accept boolean values (true/false)

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Price category already exists for this type"
}
```
or
```json
{
    "detail": {
        "entries": [
            "Maximum 10 entries allowed per category",
            "Duplicate durations are not allowed"
        ]
    }
}
```

### 404 Not Found
```json
{
    "detail": "Doctor not found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "An unexpected error occurred"
}
```

## Implementation Notes

1. Both `/price-categories/` and `/duration-prices/` endpoints provide identical functionality
2. Duration values are always in minutes
3. The API supports both single and bulk operations
4. When updating categories:
   - All existing duration prices are replaced with the new ones
   - Disabling a category automatically removes all its entries
5. When updating appointment settings:
   - Settings can be updated independently of categories
   - Omitted settings retain their previous values
6. The API maintains data consistency by:
   - Preventing duplicate categories per doctor
   - Validating all inputs
   - Enforcing business rules for durations and prices
7. Authentication is required for all operations
8. All operations are atomic - they either completely succeed or fail

## Example Usage

### Create/Update Categories and Settings
```bash
curl -X POST \
  "https://api.example.com/api/v1/doctors/doctor@example.com/price-categories/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "categories": [
        {
            "type": "initial_consultation",
            "is_enabled": true,
            "entries": [
                {
                    "duration": 15,
                    "price": 90.00
                },
                {
                    "duration": 30,
                    "price": 100.00
                }
            ]
        }
    ],
    "accept_instant_appointment": true,
    "accept_tamkeen_clinics": true
}'
``` 