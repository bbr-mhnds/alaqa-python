# Instant Appointment Prices API Documentation

## Base URL
```
https://api.example.com/v1/instant-appointment-prices
```

## Endpoints

### 1. Get All Instant Appointment Prices
```http
GET /instant-appointment-prices
```

#### Query Parameters
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page
- `status` (optional): Filter by status (active/inactive)
- `specialtyId` (optional): Filter by specialty ID

#### Response
```json
{
  "status": "success",
  "data": {
    "prices": [
      {
        "id": "string",
        "specialtyId": "string",
        "price": "number",
        "status": "string",
        "createdAt": "string",
        "updatedAt": "string",
        "specialty": {
          "id": "string",
          "name": "string",
          "nameArabic": "string"
        }
      }
    ],
    "pagination": {
      "total": "number",
      "pages": "number",
      "page": "number",
      "limit": "number"
    }
  }
}
```

### 2. Get Single Instant Appointment Price
```http
GET /instant-appointment-prices/{id}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "price": {
      "id": "string",
      "specialtyId": "string",
      "price": "number",
      "status": "string",
      "createdAt": "string",
      "updatedAt": "string",
      "specialty": {
        "id": "string",
        "name": "string",
        "nameArabic": "string"
      }
    }
  }
}
```

### 3. Create Instant Appointment Price
```http
POST /instant-appointment-prices
```

#### Request Body
```json
{
  "specialtyId": "string",
  "price": "number"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "price": {
      "id": "string",
      "specialtyId": "string",
      "price": "number",
      "status": "string",
      "createdAt": "string",
      "updatedAt": "string",
      "specialty": {
        "id": "string",
        "name": "string",
        "nameArabic": "string"
      }
    }
  }
}
```

### 4. Update Instant Appointment Price
```http
PUT /instant-appointment-prices/{id}
```

#### Request Body
```json
{
  "specialtyId": "string",
  "price": "number",
  "status": "string"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "price": {
      "id": "string",
      "specialtyId": "string",
      "price": "number",
      "status": "string",
      "createdAt": "string",
      "updatedAt": "string",
      "specialty": {
        "id": "string",
        "name": "string",
        "nameArabic": "string"
      }
    }
  }
}
```

### 5. Delete Instant Appointment Price
```http
DELETE /instant-appointment-prices/{id}
```

#### Response
```json
{
  "status": "success",
  "message": "Instant appointment price deleted successfully"
}
```

### 6. Update Instant Appointment Price Status
```http
PATCH /instant-appointment-prices/{id}/status
```

#### Request Body
```json
{
  "status": "string" // active, inactive
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "price": {
      "id": "string",
      "status": "string",
      "updatedAt": "string"
    }
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid request parameters",
  "errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Unauthorized access"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Instant appointment price not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
``` 