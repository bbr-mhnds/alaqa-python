# OTP API Documentation

## Base URL
```
http://localhost:8000/api/v1/otp
```

## Endpoints

### 1. Send OTP
Send a one-time password to a phone number.

**Endpoint:** `POST /send/`

**Request Body:**
```json
{
    "phone_number": "555552022"  // Required, string, min length 9
}
```

**Success Response:**
```json
{
    "status": "success",
    "message": "OTP sent successfully",
    "data": {
        "otp_id": "2b1e6925-5dc4-4823-bd79-67c85119dd9a"
    }
}
```

**Error Responses:**

1. Missing Phone Number:
```json
{
    "status": "error",
    "message": "Phone number is required"
}
```

2. Invalid Phone Number Format:
```json
{
    "status": "error",
    "message": "Invalid phone number format"
}
```

3. SMS Service Error:
```json
{
    "status": "error",
    "message": "Failed to send SMS: [error details]"
}
```

### 2. Verify OTP
Verify a received OTP code.

**Endpoint:** `POST /verify/`

**Request Body:**
```json
{
    "phone_number": "555552022",  // Required, string, min length 9
    "otp_code": "123456"         // Required, string, exactly 6 digits
}
```

**Success Response:**
```json
{
    "status": "success",
    "message": "OTP verified successfully"
}
```

**Error Responses:**

1. Invalid OTP:
```json
{
    "status": "error",
    "message": "Invalid OTP"
}
```

2. Expired OTP:
```json
{
    "status": "error",
    "message": "OTP has expired"
}
```

3. Maximum Attempts Exceeded:
```json
{
    "status": "error",
    "message": "Maximum verification attempts exceeded"
}
```

4. Missing Fields:
```json
{
    "status": "error",
    "message": "Both phone number and OTP code are required"
}
```

## Implementation Notes

1. OTP Lifecycle:
   - OTPs are valid for 10 minutes after creation
   - Maximum 3 verification attempts allowed
   - OTP becomes invalid after successful verification

2. Phone Number Format:
   - Minimum 9 digits
   - Only numeric characters allowed
   - No special characters except '+' prefix

3. OTP Code Format:
   - Exactly 6 digits
   - Numeric only

## TypeScript Interface

```typescript
interface OTPSendRequest {
    phone_number: string;
}

interface OTPVerifyRequest {
    phone_number: string;
    otp_code: string;
}

interface OTPResponse {
    status: 'success' | 'error';
    message: string;
    data?: {
        otp_id: string;
    };
}

// Example Angular Service
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class OTPService {
    private baseUrl = 'http://localhost:8000/api/v1/otp';

    constructor(private http: HttpClient) {}

    sendOTP(phoneNumber: string): Observable<OTPResponse> {
        return this.http.post<OTPResponse>(`${this.baseUrl}/send/`, {
            phone_number: phoneNumber
        });
    }

    verifyOTP(phoneNumber: string, otpCode: string): Observable<OTPResponse> {
        return this.http.post<OTPResponse>(`${this.baseUrl}/verify/`, {
            phone_number: phoneNumber,
            otp_code: otpCode
        });
    }
}
```

## Error Handling Best Practices

1. Always check the `status` field in the response to determine success/failure
2. Display appropriate user messages based on the `message` field
3. Implement exponential backoff for retries on network errors
4. Store the `otp_id` from successful send responses for tracking/debugging

## Security Considerations

1. Use HTTPS in production
2. Implement rate limiting on the client side
3. Don't store OTP codes locally
4. Clear OTP input fields after failed attempts
5. Implement proper error handling for network timeouts 