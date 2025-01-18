# Integrations Module Documentation

## Overview
The Integrations module provides a flexible system for managing third-party service integrations, with a specific implementation for Agora video services. It handles configuration management, credential storage, and integration status tracking.

## Base URLs
- API Base URL: `/api/v1/integrations/`
- Agora Callback URL: `/api/v1/integrations/agora/callback/`

## Models

### Integration (Base Model)
Base model for all integrations with common fields:
```python
{
    "id": "uuid",
    "name": "string",
    "description": "string",
    "is_enabled": "boolean",
    "status": "string (active/error/inactive)",
    "last_error": "string",
    "last_error_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime",
    "created_by": "user_id"
}
```

### AgoraIntegration
Extends Integration with Agora-specific fields:
```python
{
    ...Integration fields,
    "app_id": "string",
    "app_certificate": "string",
    "token_expiration_time": "integer (seconds)",
    "max_users_per_channel": "integer",
    "recording_enabled": "boolean",
    "recording_bucket": "string"
}
```

### IntegrationCredential
Stores sensitive credentials:
```python
{
    "id": "uuid",
    "integration": "integration_id",
    "key": "string",
    "value": "string (encrypted)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### IntegrationLog
Tracks integration activities and errors:
```python
{
    "id": "uuid",
    "integration": "integration_id",
    "level": "string (info/error/warning)",
    "message": "string",
    "metadata": "json",
    "user": "user_id",
    "created_at": "datetime"
}
```

## API Endpoints

### General Integration Endpoints

#### List Integrations
```
GET /api/v1/integrations/
```
Returns a list of all integrations. Requires admin permissions.

#### Create Integration
```
POST /api/v1/integrations/
```
Create a new integration. Requires admin permissions.

#### Get Integration Details
```
GET /api/v1/integrations/{integration_id}/
```
Get details of a specific integration.

#### Update Integration
```
PUT/PATCH /api/v1/integrations/{integration_id}/
```
Update an existing integration.

#### Delete Integration
```
DELETE /api/v1/integrations/{integration_id}/
```
Delete an integration.

#### Toggle Integration Status
```
POST /api/v1/integrations/{integration_id}/toggle/
```
Toggle the enabled status of an integration.

#### Get Integration Logs
```
GET /api/v1/integrations/{integration_id}/logs/
```
Get logs for a specific integration. Supports filtering by:
- level (info/error/warning)
- start_date
- end_date

### Agora-Specific Endpoints

#### Test Connection
```
POST /api/v1/integrations/agora/{integration_id}/test_connection/
```
Test the Agora integration connection by generating a test token.

#### Update Settings
```
POST /api/v1/integrations/agora/{integration_id}/update_settings/
```
Update Agora integration settings.

#### Agora Callback
```
POST /api/v1/integrations/agora/callback/
```
Webhook endpoint for receiving Agora configuration updates.

Request Headers:
- Content-Type: application/json
- X-Agora-Signature: HMAC SHA-256 signature

Example Request Body:
```json
{
    "app_id": "your_app_id",
    "app_certificate": "your_app_certificate",
    "credentials": {
        "api_key": "your_api_key",
        "api_secret": "your_api_secret"
    },
    "config": {
        "token_expiration_time": 3600,
        "max_users_per_channel": 4,
        "recording_enabled": true,
        "recording_bucket": "your-bucket-name"
    }
}
```

## Security

### Authentication
- Admin endpoints require admin user authentication
- Callback endpoint uses HMAC signature verification

### Signature Verification
The Agora callback endpoint verifies requests using HMAC SHA-256:
1. Request must include X-Agora-Signature header
2. Signature is verified against request body using AGORA_WEBHOOK_SECRET
3. Uses constant-time comparison to prevent timing attacks

### Credential Storage
- Sensitive credentials are stored encrypted
- Access is restricted to admin users only
- Credentials are never exposed in logs or API responses

## Error Handling

### HTTP Status Codes
- 200: Success
- 400: Bad Request (invalid data)
- 401: Unauthorized (invalid signature)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

### Error Response Format
```json
{
    "error": "Error message description"
}
```

## Logging
The module maintains detailed logs for all integration activities:
- Info level: Configuration updates, status changes
- Error level: Failed operations, validation errors
- Warning level: Potential issues or concerns

Logs include:
- Timestamp
- Integration reference
- User (if applicable)
- Message
- Additional metadata

## Testing
Run integration tests:
```bash
python manage.py test integrations.tests
```

Test coverage includes:
- Model operations
- API endpoints
- Callback functionality
- Security features
- Error handling

## Environment Variables
Required environment variables:
```
AGORA_WEBHOOK_SECRET=your_webhook_secret
```

## Best Practices
1. Always verify integration status before use
2. Monitor integration logs for errors
3. Regularly test connections
4. Keep credentials secure and updated
5. Handle rate limits appropriately
6. Implement proper error handling
7. Maintain audit logs

## Troubleshooting
Common issues and solutions:

1. Invalid Signature
   - Verify webhook secret is correctly configured
   - Check signature generation process
   - Ensure request body hasn't been modified

2. Connection Failures
   - Verify credentials are correct
   - Check integration status
   - Review error logs for details

3. Configuration Issues
   - Validate all required settings
   - Check for proper format
   - Ensure values are within allowed ranges 