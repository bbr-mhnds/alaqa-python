# Services API Documentation

This document outlines the API endpoints for managing services in the healthcare system.

## Base URL
`/api/v1/services/`

## Authentication
- List and Retrieve operations are public and don't require authentication
- Create, Update, and Delete operations require a valid JWT token in the Authorization header:
  ```
  Authorization: Bearer <your_jwt_token>
  ```

## Endpoints

### 1. List Services
Retrieve a list of all services.

**Request**
```http
GET /api/v1/services/
```

**Query Parameters**
- `is_active` (boolean): Filter by active status
- `search` (string): Search in names and descriptions (both Arabic and English)
- `ordering` (string): Order results by field
  - Available fields: `created_at`, `name_en`, `name_ar`
  - Prefix with `-` for descending order (e.g., `-created_at`)
- `page` (integer): Page number for pagination
- `page_size` (integer): Number of items per page (default: 10)

**Response**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name_en": "General Consultation",
            "name_ar": "استشارة عامة",
            "description_en": "General medical consultation service",
            "description_ar": "خدمة استشارة طبية عامة",
            "icon": "/media/services/icons/general.png",
            "is_active": true,
            "created_at": "2024-01-26T12:00:00Z",
            "updated_at": "2024-01-26T12:00:00Z"
        }
    ]
}
```

### 2. Create Service
Create a new service.

**Request**
```http
POST /api/v1/services/
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

**Request Body**
```json
{
    "name_en": "General Consultation",
    "name_ar": "استشارة عامة",
    "description_en": "General medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة",
    "icon": <file>,
    "is_active": true
}
```

**Response**
```json
{
    "id": 1,
    "name_en": "General Consultation",
    "name_ar": "استشارة عامة",
    "description_en": "General medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة",
    "icon": "/media/services/icons/general.png",
    "is_active": true,
    "created_at": "2024-01-26T12:00:00Z",
    "updated_at": "2024-01-26T12:00:00Z"
}
```

### 3. Retrieve Service
Get details of a specific service.

**Request**
```http
GET /api/v1/services/{id}/
```

**Response**
```json
{
    "id": 1,
    "name_en": "General Consultation",
    "name_ar": "استشارة عامة",
    "description_en": "General medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة",
    "icon": "/media/services/icons/general.png",
    "is_active": true,
    "created_at": "2024-01-26T12:00:00Z",
    "updated_at": "2024-01-26T12:00:00Z"
}
```

### 4. Update Service
Update an existing service.

**Request**
```http
PUT /api/v1/services/{id}/
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

**Request Body**
```json
{
    "name_en": "Updated General Consultation",
    "name_ar": "استشارة عامة محدثة",
    "description_en": "Updated general medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة محدثة",
    "icon": <file>,
    "is_active": true
}
```

**Response**
```json
{
    "id": 1,
    "name_en": "Updated General Consultation",
    "name_ar": "استشارة عامة محدثة",
    "description_en": "Updated general medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة محدثة",
    "icon": "/media/services/icons/updated_general.png",
    "is_active": true,
    "created_at": "2024-01-26T12:00:00Z",
    "updated_at": "2024-01-26T12:30:00Z"
}
```

### 5. Partial Update Service
Update specific fields of an existing service.

**Request**
```http
PATCH /api/v1/services/{id}/
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

**Request Body**
```json
{
    "is_active": false
}
```

**Response**
```json
{
    "id": 1,
    "name_en": "General Consultation",
    "name_ar": "استشارة عامة",
    "description_en": "General medical consultation service",
    "description_ar": "خدمة استشارة طبية عامة",
    "icon": "/media/services/icons/general.png",
    "is_active": false,
    "created_at": "2024-01-26T12:00:00Z",
    "updated_at": "2024-01-26T12:45:00Z"
}
```

### 6. Delete Service
Delete a service.

**Request**
```http
DELETE /api/v1/services/{id}/
Authorization: Bearer <your_jwt_token>
```

**Response**
```http
Status: 204 No Content
```

## Error Responses

### 400 Bad Request
```json
{
    "icon": ["Icon file size cannot exceed 2MB"],
    "name_en": ["This field is required."]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

## File Upload Requirements

### Icon
- Supported formats: PNG, JPG, JPEG, SVG
- Maximum file size: 2MB
- Upload path: `/media/services/icons/` 