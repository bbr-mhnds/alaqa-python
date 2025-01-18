# Drug Management API Documentation

## Base URL
```
/api/v1/drugs
```

## Authentication
All endpoints require authentication using JWT (JSON Web Token). Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Drug Management

#### 1.1 List Drugs
```http
GET /api/v1/drugs/
```

Query Parameters:
- `search` (optional): Search in name, name_arabic, description, and description_arabic
- `status` (optional): Filter by status (true/false)
- `category` (optional): Filter by category ID
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 10)

Response:
```json
{
    "count": "number",
    "next": "string | null",
    "previous": "string | null",
    "status": "success",
    "data": {
        "drugs": [
            {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "description": "string",
                "description_arabic": "string",
                "category": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string",
                    "status": "boolean"
                },
                "dosage_form": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string",
                    "status": "boolean"
                },
                "strength": "string",
                "manufacturer": "string",
                "status": "boolean",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        ]
    }
}
```

#### 1.2 Create Drug
```http
POST /api/v1/drugs/
```

Request Body:
```json
{
    "name": "string",
    "name_arabic": "string",
    "description": "string",
    "description_arabic": "string",
    "category": "uuid",
    "dosage_form": "uuid",
    "strength": "string",
    "manufacturer": "string",
    "status": "boolean"
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "drug": {
            "id": "uuid",
            "name": "string",
            "name_arabic": "string",
            "description": "string",
            "description_arabic": "string",
            "category": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "dosage_form": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "strength": "string",
            "manufacturer": "string",
            "status": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

#### 1.3 Get Drug Details
```http
GET /api/v1/drugs/{id}/
```

Response:
```json
{
    "status": "success",
    "data": {
        "drug": {
            "id": "uuid",
            "name": "string",
            "name_arabic": "string",
            "description": "string",
            "description_arabic": "string",
            "category": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "dosage_form": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "strength": "string",
            "manufacturer": "string",
            "status": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

#### 1.4 Update Drug
```http
PUT /api/v1/drugs/{id}/
```

Request Body:
```json
{
    "name": "string",
    "name_arabic": "string",
    "description": "string",
    "description_arabic": "string",
    "category": "uuid",
    "dosage_form": "uuid",
    "strength": "string",
    "manufacturer": "string",
    "status": "boolean"
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "drug": {
            "id": "uuid",
            "name": "string",
            "name_arabic": "string",
            "description": "string",
            "description_arabic": "string",
            "category": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "dosage_form": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            },
            "strength": "string",
            "manufacturer": "string",
            "status": "boolean",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

#### 1.5 Delete Drug
```http
DELETE /api/v1/drugs/{id}/
```

Response:
```json
{
    "status": "success",
    "message": "Drug deleted successfully"
}
```

#### 1.6 Update Drug Status
```http
PATCH /api/v1/drugs/{id}/status/
```

Request Body:
```json
{
    "status": "boolean"
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "drug": {
            "id": "uuid",
            "status": "boolean",
            "updated_at": "datetime"
        }
    }
}
```

### 2. Drug Categories

#### 2.1 List Categories
```http
GET /api/v1/drugs/categories/
```

Response:
```json
{
    "status": "success",
    "data": {
        "categories": [
            {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            }
        ]
    }
}
```

### 3. Drug Dosage Forms

#### 3.1 List Dosage Forms
```http
GET /api/v1/drugs/dosage-forms/
```

Response:
```json
{
    "status": "success",
    "data": {
        "dosageForms": [
            {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "status": "boolean"
            }
        ]
    }
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": [
        "Error message"
    ]
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

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Notes

1. All timestamps are in ISO 8601 format with timezone (UTC)
2. All IDs are UUIDs
3. Pagination is enabled by default with 10 items per page
4. Search is case-insensitive and matches partial text
5. Category and dosage form endpoints are read-only (no create/update/delete operations)
6. Status updates only affect the status field
7. Drug categories and dosage forms are protected - cannot be deleted if referenced by drugs
8. Arabic translations are supported for names and descriptions
9. Only active categories and dosage forms are returned in their respective list endpoints 