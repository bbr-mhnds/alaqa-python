# Prescriptions API Documentation

## Base URL
```
https://api.example.com/api/v1/prescriptions
```

## Authentication
All endpoints require authentication using JWT (JSON Web Token). Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Prescriptions

#### 1.1 List Prescriptions
```http
GET /api/v1/prescriptions/
```

Query Parameters:
- `appointment_id` (optional): Filter by appointment ID
- `doctor_id` (optional): Filter by doctor ID
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 10)

Response:
```json
{
    "count": "number",
    "next": "string | null",
    "previous": "string | null",
    "results": [
        {
            "id": "uuid",
            "appointment": {
                "id": "uuid",
                "doctor": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string"
                },
                "slot_time": "datetime",
                "status": "string"
            },
            "diagnosis": "string",
            "notes": "string",
            "follow_up_date": "date",
            "prescribed_drugs": [
                {
                    "id": "uuid",
                    "drug": {
                        "id": "uuid",
                        "name": "string",
                        "name_arabic": "string",
                        "category": {
                            "id": "uuid",
                            "name": "string",
                            "name_arabic": "string"
                        },
                        "dosage_form": {
                            "id": "uuid",
                            "name": "string",
                            "name_arabic": "string"
                        }
                    },
                    "dosage": "string",
                    "frequency": "string",
                    "duration": "number",
                    "duration_unit": "string",
                    "route": "string",
                    "instructions": "string"
                }
            ],
            "test_recommendations": [
                {
                    "id": "uuid",
                    "test_name": "string",
                    "description": "string",
                    "urgency": "string",
                    "notes": "string"
                }
            ],
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### 1.2 Create Prescription
```http
POST /api/v1/prescriptions/
```

Request Body:
```json
{
    "appointment_id": "uuid",
    "diagnosis": "string",
    "notes": "string",
    "follow_up_date": "date",
    "prescribed_drugs": [
        {
            "drug_id": "uuid",
            "dosage": "string",
            "frequency": "string",
            "duration": "number",
            "duration_unit": "string",
            "route": "string",
            "instructions": "string"
        }
    ],
    "test_recommendations": [
        {
            "test_name": "string",
            "description": "string",
            "urgency": "string",
            "notes": "string"
        }
    ]
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "prescription": {
            "id": "uuid",
            "appointment": {
                "id": "uuid",
                "doctor": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string"
                },
                "slot_time": "datetime",
                "status": "string"
            },
            "diagnosis": "string",
            "notes": "string",
            "follow_up_date": "date",
            "prescribed_drugs": [
                {
                    "id": "uuid",
                    "drug": {
                        "id": "uuid",
                        "name": "string",
                        "name_arabic": "string",
                        "category": {
                            "id": "uuid",
                            "name": "string",
                            "name_arabic": "string"
                        },
                        "dosage_form": {
                            "id": "uuid",
                            "name": "string",
                            "name_arabic": "string"
                        }
                    },
                    "dosage": "string",
                    "frequency": "string",
                    "duration": "number",
                    "duration_unit": "string",
                    "route": "string",
                    "instructions": "string"
                }
            ],
            "test_recommendations": [
                {
                    "id": "uuid",
                    "test_name": "string",
                    "description": "string",
                    "urgency": "string",
                    "notes": "string"
                }
            ],
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    }
}
```

#### 1.3 Get Prescription Details
```http
GET /api/v1/prescriptions/{id}/
```

Response: Same as create prescription response

#### 1.4 Update Prescription
```http
PUT /api/v1/prescriptions/{id}/
```

Request Body: Same as create prescription request
Response: Same as create prescription response

#### 1.5 Delete Prescription
```http
DELETE /api/v1/prescriptions/{id}/
```

Response:
```json
{
    "status": "success",
    "message": "Prescription deleted successfully"
}
```

#### 1.6 Download Prescription PDF
```http
GET /api/v1/prescriptions/{id}/download/
```

Response: Binary PDF file

### 2. Prescribed Drugs

#### 2.1 List Prescribed Drugs
```http
GET /api/v1/prescriptions/{prescription_id}/drugs/
```

Response:
```json
{
    "count": "number",
    "next": "string | null",
    "previous": "string | null",
    "results": [
        {
            "id": "uuid",
            "drug": {
                "id": "uuid",
                "name": "string",
                "name_arabic": "string",
                "category": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string"
                },
                "dosage_form": {
                    "id": "uuid",
                    "name": "string",
                    "name_arabic": "string"
                }
            },
            "dosage": "string",
            "frequency": "string",
            "duration": "number",
            "duration_unit": "string",
            "route": "string",
            "instructions": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### 2.2 Add Prescribed Drug
```http
POST /api/v1/prescriptions/{prescription_id}/drugs/
```

Request Body:
```json
{
    "drug_id": "uuid",
    "dosage": "string",
    "frequency": "string",
    "duration": "number",
    "duration_unit": "string",
    "route": "string",
    "instructions": "string"
}
```

Response: Single prescribed drug object

#### 2.3 Update Prescribed Drug
```http
PUT /api/v1/prescriptions/{prescription_id}/drugs/{id}/
```

Request Body: Same as add prescribed drug
Response: Single prescribed drug object

#### 2.4 Delete Prescribed Drug
```http
DELETE /api/v1/prescriptions/{prescription_id}/drugs/{id}/
```

Response:
```json
{
    "status": "success",
    "message": "Prescribed drug deleted successfully"
}
```

### 3. Test Recommendations

#### 3.1 List Test Recommendations
```http
GET /api/v1/prescriptions/{prescription_id}/tests/
```

Response:
```json
{
    "count": "number",
    "next": "string | null",
    "previous": "string | null",
    "results": [
        {
            "id": "uuid",
            "test_name": "string",
            "description": "string",
            "urgency": "string",
            "notes": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    ]
}
```

#### 3.2 Add Test Recommendation
```http
POST /api/v1/prescriptions/{prescription_id}/tests/
```

Request Body:
```json
{
    "test_name": "string",
    "description": "string",
    "urgency": "string",
    "notes": "string"
}
```

Response: Single test recommendation object

#### 3.3 Update Test Recommendation
```http
PUT /api/v1/prescriptions/{prescription_id}/tests/{id}/
```

Request Body: Same as add test recommendation
Response: Single test recommendation object

#### 3.4 Delete Test Recommendation
```http
DELETE /api/v1/prescriptions/{prescription_id}/tests/{id}/
```

Response:
```json
{
    "status": "success",
    "message": "Test recommendation deleted successfully"
}
```

## Enumerations

### Frequency Options
- `OD`: Once daily
- `BD`: Twice daily
- `TDS`: Three times a day
- `QDS`: Four times a day
- `PRN`: As needed
- `STAT`: Immediately
- `OTHER`: Other (see notes)

### Duration Units
- `days`: Days
- `weeks`: Weeks
- `months`: Months

### Route Options
- `oral`: Oral
- `topical`: Topical
- `injection`: Injection
- `inhaler`: Inhaler
- `drops`: Drops
- `other`: Other

### Test Urgency Levels
- `routine`: Routine
- `urgent`: Urgent
- `emergency`: Emergency

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

## Notes

1. All timestamps are in ISO 8601 format with timezone (UTC)
2. All IDs are UUIDs
3. Pagination is enabled by default with 10 items per page
4. The prescription can only be created for appointments that:
   - Have status "COMPLETED"
   - Don't already have a prescription
   - Belong to the authenticated doctor
5. Only the doctor who created the prescription can modify or delete it
6. The PDF download endpoint generates a formatted prescription document with all details
7. When creating a prescription, at least one prescribed drug is required
8. Test recommendations are optional 