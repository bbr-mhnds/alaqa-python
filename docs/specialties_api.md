# Specialties API Documentation

## Base URL
```
http://localhost:8001/api/v1/specialties
```

## Endpoints

### 1. List Specialties
Get a list of all active specialties.

**Endpoint:** `GET /specialties/`  
**Authentication:** Not required  
**Query Parameters:**
- `search`: Search in title and title_ar fields
- `status`: Filter by status (true/false)
- `page`: Page number for pagination
- `page_size`: Number of items per page (default: 10)

**Example Request:**
```bash
curl -X GET "http://localhost:8001/api/v1/specialties/specialties/?search=cardio&page=1"
```

**Success Response (200 OK):**
```json
{
    "status": "success",
    "data": {
        "specialties": [
            {
                "id": "85f84ccd-1f59-4f31-980b-dfc7db74c129",
                "title": "Specialty Title",
                "title_ar": "العنوان بالعربي",
                "icon": "ambulance",
                "background_color": "1",
                "color_class": "1",
                "description": "Description",
                "description_ar": "الوصف بالعربي",
                "total_time_call": 30,
                "warning_time_call": 5,
                "alert_time_call": 4,
                "status": true,
                "updated_at": "2025-01-03T10:17:39.116602Z"
            }
        ],
        "pagination": {
            "count": 1,
            "total_pages": 1,
            "current_page": 1,
            "page_size": 10,
            "next": null,
            "previous": null
        }
    }
}
```

### 2. Get Single Specialty
Get details of a specific specialty.

**Endpoint:** `GET /specialties/{id}/`  
**Authentication:** Not required  
**URL Parameters:**
- `id`: UUID of the specialty

**Example Request:**
```bash
curl -X GET "http://localhost:8001/api/v1/specialties/specialties/85f84ccd-1f59-4f31-980b-dfc7db74c129/"
```

**Success Response (200 OK):**
```json
{
    "status": "success",
    "data": {
        "specialty": {
            "id": "85f84ccd-1f59-4f31-980b-dfc7db74c129",
            "title": "Specialty Title",
            "title_ar": "العنوان بالعربي",
            "icon": "ambulance",
            "background_color": "1",
            "color_class": "1",
            "description": "Description",
            "description_ar": "الوصف بالعربي",
            "total_time_call": 30,
            "warning_time_call": 5,
            "alert_time_call": 4,
            "status": true,
            "updated_at": "2025-01-03T10:17:39.116602Z"
        }
    }
}
```

### 3. Create Specialty (Protected)
Create a new specialty.

**Endpoint:** `POST /specialties/`  
**Authentication:** Required (Bearer Token)  
**Request Body:**
```json
{
    "title": "New Specialty",
    "title_ar": "تخصص جديد",
    "icon": "icon-name",
    "background_color": "color-code",
    "color_class": "class-name",
    "description": "English description",
    "description_ar": "الوصف بالعربي",
    "total_time_call": 30,
    "warning_time_call": 5,
    "alert_time_call": 4,
    "status": true
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8001/api/v1/specialties/specialties/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Specialty",
    "title_ar": "تخصص جديد"
  }'
```

### 4. Update Specialty (Protected)
Update an existing specialty.

**Endpoint:** `PUT /specialties/{id}/`  
**Authentication:** Required (Bearer Token)  
**URL Parameters:**
- `id`: UUID of the specialty

**Example Request:**
```bash
curl -X PUT "http://localhost:8001/api/v1/specialties/specialties/{id}/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Specialty",
    "title_ar": "تخصص محدث"
  }'
```

### 5. Delete Specialty (Protected)
Delete a specialty.

**Endpoint:** `DELETE /specialties/{id}/`  
**Authentication:** Required (Bearer Token)  
**URL Parameters:**
- `id`: UUID of the specialty

**Example Request:**
```bash
curl -X DELETE "http://localhost:8001/api/v1/specialties/specialties/{id}/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "status": "error",
    "message": "Specialty not found"
}
```

### 400 Bad Request
```json
{
    "status": "error",
    "message": "Validation error",
    "errors": {
        "field_name": ["Error message"]
    }
}
```

## Angular Service Example
```typescript
// specialty.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpecialtyService {
  private apiUrl = 'http://localhost:8001/api/v1/specialties/specialties';

  constructor(private http: HttpClient) {}

  // Get all specialties (public)
  getSpecialties(page: number = 1, search?: string): Observable<any> {
    let url = `${this.apiUrl}/?page=${page}`;
    if (search) {
      url += `&search=${search}`;
    }
    return this.http.get(url);
  }

  // Get single specialty (public)
  getSpecialty(id: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}/`);
  }

  // Create specialty (protected)
  createSpecialty(data: any): Observable<any> {
    return this.http.post(this.apiUrl + '/', data);
  }

  // Update specialty (protected)
  updateSpecialty(id: string, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}/`, data);
  }

  // Delete specialty (protected)
  deleteSpecialty(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}/`);
  }
}
``` 