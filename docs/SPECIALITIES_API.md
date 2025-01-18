# Specialties API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require authentication. The API uses token-based authentication.

## Endpoints

### 1. Get All Specialties
```http
GET /specialties/
```

#### Query Parameters
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page (default: 10)
- `status` (optional): Filter by status (true/false)
- `search` (optional): Search by title or title_ar

#### Response
```json
{
  "status": "success",
  "data": {
    "specialties": [
      {
        "id": "uuid",
        "title": "string",
        "title_ar": "string",
        "icon": "string",
        "background_color": "string",
        "color_class": "string",
        "description": "string",
        "description_ar": "string",
        "total_time_call": "number",
        "warning_time_call": "number",
        "alert_time_call": "number",
        "status": "boolean",
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

### 2. Get Single Specialty
```http
GET /specialties/{id}/
```

#### Response
```json
{
  "status": "success",
  "data": {
    "specialty": {
      "id": "uuid",
      "title": "string",
      "title_ar": "string",
      "icon": "string",
      "background_color": "string",
      "color_class": "string",
      "description": "string",
      "description_ar": "string",
      "total_time_call": "number",
      "warning_time_call": "number",
      "alert_time_call": "number",
      "status": "boolean",
      "updated_at": "datetime"
    }
  }
}
```

### 3. Create Specialty
```http
POST /specialties/
```

#### Request Body
```json
{
  "title": "string",
  "title_ar": "string",
  "icon": "string",
  "background_color": "string",
  "color_class": "string",
  "description": "string",
  "description_ar": "string",
  "total_time_call": "number",
  "warning_time_call": "number",
  "alert_time_call": "number",
  "status": "boolean"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "specialty": {
      "id": "uuid",
      "title": "string",
      "title_ar": "string",
      "icon": "string",
      "background_color": "string",
      "color_class": "string",
      "description": "string",
      "description_ar": "string",
      "total_time_call": "number",
      "warning_time_call": "number",
      "alert_time_call": "number",
      "status": "boolean",
      "updated_at": "datetime"
    }
  }
}
```

### 4. Update Specialty
```http
PUT /specialties/{id}/
```

#### Request Body
```json
{
  "title": "string",
  "title_ar": "string",
  "icon": "string",
  "background_color": "string",
  "color_class": "string",
  "description": "string",
  "description_ar": "string",
  "total_time_call": "number",
  "warning_time_call": "number",
  "alert_time_call": "number",
  "status": "boolean"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "specialty": {
      "id": "uuid",
      "title": "string",
      "title_ar": "string",
      "icon": "string",
      "background_color": "string",
      "color_class": "string",
      "description": "string",
      "description_ar": "string",
      "total_time_call": "number",
      "warning_time_call": "number",
      "alert_time_call": "number",
      "status": "boolean",
      "updated_at": "datetime"
    }
  }
}
```

### 5. Delete Specialty
```http
DELETE /specialties/{id}/
```

#### Response
```json
{
  "status": "success",
  "message": "Specialty deleted successfully"
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
  "message": "Specialty not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## API Documentation
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI Schema: `/swagger.json` 