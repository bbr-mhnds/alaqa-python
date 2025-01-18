/**
 * OTP-related interfaces for frontend integration
 */

// Request Types
export interface OTPSendRequest {
    phone_number: string;
}

export interface OTPVerifyRequest {
    phone_number: string;
    otp_code: string;
}

// Response Types
export interface OTPResponse {
    status: 'success' | 'error';
    message: string;
    data?: {
        otp_id: string;
    };
}

// OTP Status Types
export type OTPStatus = 'Verified' | 'Expired' | 'Max Attempts' | 'Active';

// OTP Service Configuration
export interface OTPConfig {
    baseUrl: string;
    maxAttempts: number;
    expiryMinutes: number;
    minPhoneLength: number;
    otpLength: number;
}

// Default configuration
export const DEFAULT_OTP_CONFIG: OTPConfig = {
    baseUrl: 'http://localhost:8000/api/v1/otp',
    maxAttempts: 3,
    expiryMinutes: 10,
    minPhoneLength: 9,
    otpLength: 6
}; 