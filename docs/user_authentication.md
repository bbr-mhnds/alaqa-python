# User Authentication API Documentation

## Base URL
```
https://api.example.com/v1/auth
```

## Authentication Endpoints

### 1. User Registration
```http
POST /auth/register
```

#### Request Body
```json
{
  "email": "string",
  "password": "string",
  "password_confirmation": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string",
      "created_at": "string"
    },
    "tokens": {
      "access": "string",
      "refresh": "string"
    }
  }
}
```

### 2. User Login
```http
POST /auth/login
```

#### Request Body
```json
{
  "email": "string",
  "password": "string"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string",
      "created_at": "string"
    },
    "tokens": {
      "access": "string",
      "refresh": "string"
    }
  }
}
```

### 3. Refresh Token
```http
POST /auth/token/refresh
```

#### Request Body
```json
{
  "refresh": "string"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "tokens": {
      "access": "string",
      "refresh": "string"
    }
  }
}
```

### 4. Logout
```http
POST /auth/logout
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response
```json
{
  "status": "success",
  "message": "Successfully logged out"
}
```

### 5. Request Password Reset
```http
POST /auth/password/reset
```

#### Request Body
```json
{
  "email": "string"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Password reset email sent successfully"
}
```

### 6. Reset Password
```http
POST /auth/password/reset/confirm
```

#### Request Body
```json
{
  "token": "string",
  "password": "string",
  "password_confirmation": "string"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Password reset successfully"
}
```

### 7. Change Password
```http
POST /auth/password/change
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body
```json
{
  "current_password": "string",
  "new_password": "string",
  "new_password_confirmation": "string"
}
```

#### Response
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

### 8. Get User Profile
```http
GET /auth/profile
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Response
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string",
      "created_at": "string"
    }
  }
}
```

### 9. Update User Profile
```http
PUT /auth/profile
```

#### Headers
```
Authorization: Bearer <access_token>
```

#### Request Body
```json
{
  "first_name": "string",
  "last_name": "string",
  "phone": "string"
}
```

#### Response
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string",
      "created_at": "string"
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
  "message": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "Access denied"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "status": "error",
  "message": "Too many requests",
  "retry_after": "number"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## Authentication Flow

1. **Registration**:
   - User submits registration details
   - System validates and creates account
   - Returns user data and authentication tokens

2. **Login**:
   - User provides email and password
   - System validates credentials
   - Returns user data and authentication tokens

3. **Using Protected Endpoints**:
   - Include access token in Authorization header
   - Format: `Authorization: Bearer <access_token>`

4. **Token Refresh**:
   - When access token expires
   - Use refresh token to get new tokens
   - Implement automatic refresh in your client

5. **Password Reset**:
   - Request reset via email
   - Receive reset token
   - Submit new password with token

## Security Guidelines

1. **Password Requirements**:
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character

2. **Token Security**:
   - Store tokens securely
   - Never expose in URLs
   - Clear on logout
   - Implement automatic refresh

3. **Rate Limiting**:
   - Login attempts: 5 per minute
   - Password reset requests: 3 per hour
   - API calls: 100 per minute

4. **Session Management**:
   - Access tokens expire in 15 minutes
   - Refresh tokens expire in 7 days
   - One active session per user

## Implementation Notes

1. **Environment Variables**:
   ```env
   JWT_SECRET_KEY=your-secret-key
   JWT_ACCESS_TOKEN_EXPIRES=900
   JWT_REFRESH_TOKEN_EXPIRES=604800
   ```

2. **Required Headers**:
   ```
   Content-Type: application/json
   Accept: application/json
   ```

3. **CORS Configuration**:
   - Allowed origins must be configured
   - Credentials must be included
   - Proper headers must be set 