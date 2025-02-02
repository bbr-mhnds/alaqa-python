# Duration & Prices API Documentation

## Base URL
`/api/v1`

## Endpoints

### Get Doctor's Duration Prices
Retrieves the duration and price settings for a doctor.

- **Method**: `GET`
- **URL**: `/doctors/{email}/duration-prices/`
- **Parameters**:
  - `email` (string, required): The doctor's email address

#### Success Response
```json
{
  "status": "success",
  "data": {
    "categories": [
      {
        "type": "initial_consultation",
        "is_enabled": true,
        "entries": [
          {
            "duration": 30,
            "price": 100
          },
          {
            "duration": 45,
            "price": 150
          }
        ]
      },
      {
        "type": "follow_up",
        "is_enabled": true,
        "entries": [
          {
            "duration": 15,
            "price": 50
          },
          {
            "duration": 30,
            "price": 80
          }
        ]
      },
      {
        "type": "emergency",
        "is_enabled": true,
        "entries": [
          {
            "duration": 45,
            "price": 150
          }
        ]
      },
      {
        "type": "specialist",
        "is_enabled": true,
        "entries": [
          {
            "duration": 60,
            "price": 200
          }
        ]
      }
    ]
  }
}
```

#### Error Response
```json
{
  "status": "error",
  "message": "Doctor not found"
}
```

- **Status Code**: 404 Not Found

### Update Doctor's Duration Prices
Updates the duration and price settings for a doctor.

- **Method**: `POST`
- **URL**: `/doctors/{email}/duration-prices/`
- **Parameters**:
  - `email` (string, required): The doctor's email address

#### Request Body
```json
{
  "categories": [
    {
      "type": "initial_consultation",
      "is_enabled": true,
      "entries": [
        {
          "duration": 30,
          "price": 100
        }
      ]
    },
    {
      "type": "follow_up",
      "is_enabled": true,
      "entries": [
        {
          "duration": 15,
          "price": 50
        }
      ]
    },
    {
      "type": "emergency",
      "is_enabled": true,
      "entries": [
        {
          "duration": 45,
          "price": 150
        }
      ]
    },
    {
      "type": "specialist",
      "is_enabled": true,
      "entries": [
        {
          "duration": 60,
          "price": 200
        }
      ]
    }
  ]
}
```

#### Success Response
```json
{
  "status": "success",
  "data": {
    "categories": [/* Updated categories data */]
  }
}
```

#### Error Responses
1. Doctor Not Found
```json
{
  "status": "error",
  "message": "Doctor not found"
}
```
- **Status Code**: 404 Not Found

2. Invalid Input
```json
{
  "status": "error",
  "message": "Invalid input",
  "errors": [
    {
      "field": "categories[0].entries[0].duration",
      "message": "Duration must be at least 5 minutes"
    }
  ]
}
```
- **Status Code**: 400 Bad Request

## Data Models

### Category
```typescript
{
  type: 'initial_consultation' | 'follow_up' | 'emergency' | 'specialist';
  is_enabled: boolean;
  entries: DurationPrice[];
}
```

### DurationPrice
```typescript
{
  duration: number; // in minutes, minimum 5
  price: number;    // in USD, non-negative
}
```

## Validation Rules

1. **Category Type**
   - Must be one of: `initial_consultation`, `follow_up`, `emergency`, `specialist`
   - Each type must appear exactly once in the categories array

2. **Duration**
   - Minimum: 5 minutes
   - Must be a positive integer
   - Must be unique within each category
   - Recommended step: 5 minutes

3. **Price**
   - Must be non-negative
   - Must be a number with up to 2 decimal places
   - Currency: USD

4. **Entries Array**
   - Can be empty if category is disabled
   - Must have at least one entry if category is enabled
   - Maximum 10 entries per category

## Notes

### Authentication
- All endpoints require JWT authentication
- Token must be included in the Authorization header
- Doctor can only access and modify their own duration prices

### Performance
- Response is cached for 5 minutes
- Cache is invalidated when prices are updated

### Security
- Input sanitization is required
- Price values should be validated server-side
- Rate limiting is applied (100 requests per hour)

### Best Practices
1. **Updating Prices**
   - Changes take effect immediately
   - Existing appointments are not affected by price changes
   - Consider adding a notification system for price changes

2. **Duration Management**
   - Duration affects calendar slot availability
   - Ensure duration aligns with working hours slots
   - Consider buffer time between appointments

3. **Error Handling**
   - Validate all inputs server-side
   - Return specific error messages
   - Log all validation failures

4. **Data Consistency**
   - Maintain price history for accounting
   - Ensure atomic updates
   - Validate against business rules 