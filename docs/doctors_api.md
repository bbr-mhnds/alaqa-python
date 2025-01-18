# Doctors API Documentation

## Base URL
```
https://api.example.com/v1/doctors
```

## Endpoints

### 1. Get All Doctors
```http
GET /doctors
```

#### Query Parameters
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page
- `status` (optional): Filter by status (pending/approved/rejected)
- `search` (optional): Search by name or email
- `specialty` (optional): Filter by specialty ID

#### Response
```json
{
  "status": "success",
  "data": {
    "doctors": [
      {
        "id": "string",
        "nameArabic": "string",
        "name": "string",
        "sex": "string",
        "email": "string",
        "phone": "string",
        "experience": "string",
        "category": "string",
        "languageInSessions": "string",
        "licenseNumber": "string",
        "specialities": ["string"],
        "profileArabic": "string",
        "profileEnglish": "string",
        "status": "string",
        "photo": "string",
        "bankDetails": {
          "accountHolderName": "string",
          "accountNumber": "string",
          "ibanNumber": "string"
        },
        "createdAt": "string",
        "updatedAt": "string"
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

### 2. Get Single Doctor
```http
GET /doctors/{id}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "doctor": {
      "id": "string",
      "nameArabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "experience": "string",
      "category": "string",
      "languageInSessions": "string",
      "licenseNumber": "string",
      "specialities": ["string"],
      "profileArabic": "string",
      "profileEnglish": "string",
      "status": "string",
      "photo": "string",
      "bankDetails": {
        "accountHolderName": "string",
        "accountNumber": "string",
        "ibanNumber": "string"
      },
      "createdAt": "string",
      "updatedAt": "string"
    }
  }
}
```

### 3. Create Doctor
```http
POST /doctors
```

#### Request Body
```json
{
  "nameArabic": "string",
  "name": "string",
  "sex": "string",
  "email": "string",
  "phone": "string",
  "experience": "string",
  "category": "string",
  "languageInSessions": "string",
  "licenseNumber": "string",
  "specialities": ["string"],
  "profileArabic": "string",
  "profileEnglish": "string",
  "photo": "file",
  "bankDetails": {
    "accountHolderName": "string",
    "accountNumber": "string",
    "ibanNumber": "string"
  }
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "doctor": {
      "id": "string",
      "nameArabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "experience": "string",
      "category": "string",
      "languageInSessions": "string",
      "licenseNumber": "string",
      "specialities": ["string"],
      "profileArabic": "string",
      "profileEnglish": "string",
      "status": "string",
      "photo": "string",
      "bankDetails": {
        "accountHolderName": "string",
        "accountNumber": "string",
        "ibanNumber": "string"
      },
      "createdAt": "string",
      "updatedAt": "string"
    }
  }
}
```

### 4. Update Doctor
```http
PUT /doctors/{id}
```

#### Request Body
```json
{
  "nameArabic": "string",
  "name": "string",
  "sex": "string",
  "email": "string",
  "phone": "string",
  "experience": "string",
  "category": "string",
  "languageInSessions": "string",
  "licenseNumber": "string",
  "specialities": ["string"],
  "profileArabic": "string",
  "profileEnglish": "string",
  "photo": "file",
  "status": "string",
  "bankDetails": {
    "accountHolderName": "string",
    "accountNumber": "string",
    "ibanNumber": "string"
  }
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "doctor": {
      "id": "string",
      "nameArabic": "string",
      "name": "string",
      "sex": "string",
      "email": "string",
      "phone": "string",
      "experience": "string",
      "category": "string",
      "languageInSessions": "string",
      "licenseNumber": "string",
      "specialities": ["string"],
      "profileArabic": "string",
      "profileEnglish": "string",
      "status": "string",
      "photo": "string",
      "bankDetails": {
        "accountHolderName": "string",
        "accountNumber": "string",
        "ibanNumber": "string"
      },
      "createdAt": "string",
      "updatedAt": "string"
    }
  }
}
```

### 5. Delete Doctor
```http
DELETE /doctors/{id}
```

#### Response
```json
{
  "status": "success",
  "message": "Doctor deleted successfully"
}
```

### 6. Update Doctor Status
```http
PATCH /doctors/{id}/status
```

#### Request Body
```json
{
  "status": "string" // pending, approved, rejected
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "doctor": {
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
  "message": "Doctor not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
``` 