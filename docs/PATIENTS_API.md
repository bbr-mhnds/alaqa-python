# Patients API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication. The API uses token-based authentication.

## Endpoints

### 1. Get All Patients
```http
GET /patients/
```

#### Query Parameters
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page (default: 10)
- `status` (optional): Filter by status (active/inactive)
- `search` (optional): Search by name, Arabic name, or email

#### Response
```json
{
  "status": "success",
  "data": {
    "patients": [
      {
        "id": "uuid",
        "name_arabic": "string",
        "name": "string",
        "sex": "string",
        "email": "string",
        "phone": "string",
        "date_of_birth": "date",
        "status": "string",
        "photo": "url",
        "created_at": "datetime",
        "updated_at": "datetime"
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

### 2. Get Single Patient
```http
GET /patients/{id}/
```

#### Response
```json
{
  "status": "success",
  "data": {
    "patient": {
      "id": "uuid",
      "name_arabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "date_of_birth": "date",
      "status": "string",
      "photo": "url",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
}
```

### 3. Create Patient
```http
POST /patients/
```

#### Request Body
```json
{
  "name_arabic": "string",
  "name": "string",
  "sex": "string",
  "email": "string",
  "phone": "string",
  "date_of_birth": "date",
  "photo": "file"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "patient": {
      "id": "uuid",
      "name_arabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "date_of_birth": "date",
      "status": "string",
      "photo": "url",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
}
```

### 4. Update Patient
```http
PUT /patients/{id}/
```

#### Request Body
```json
{
  "name_arabic": "string",
  "name": "string",
  "sex": "string",
  "email": "string",
  "phone": "string",
  "date_of_birth": "date",
  "status": "string",
  "photo": "file"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "patient": {
      "id": "uuid",
      "name_arabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "date_of_birth": "date",
      "status": "string",
      "photo": "url",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
}
```

### 5. Delete Patient
```http
DELETE /patients/{id}/
```

#### Response
```json
{
  "status": "success",
  "message": "Patient deleted successfully"
}
```

### 6. Update Patient Status
```http
PATCH /patients/{id}/status/
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
    "patient": {
      "id": "uuid",
      "status": "string",
      "updated_at": "datetime"
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
  "message": "Patient not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## Field Validations

1. Name and Arabic Name:
   - Minimum length: 3 characters
   - Required fields

2. Sex:
   - Valid values: "male", "female"
   - Required field

3. Email:
   - Must be a valid email format
   - Must be unique
   - Required field

4. Phone:
   - Must contain only digits
   - Required field

5. Date of Birth:
   - Must be a valid date format (YYYY-MM-DD)
   - Required field

6. Status:
   - Valid values: "active", "inactive"
   - Default: "active"

7. Photo:
   - Optional field
   - Supported formats: JPEG, PNG
   - Maximum size: 5MB

## API Documentation
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI Schema: `/swagger.json` 