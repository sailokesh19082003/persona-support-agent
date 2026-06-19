# API Authentication Guide

## Overview

CloudDesk's REST API uses Bearer Token authentication. Every request to an
authenticated endpoint must include a valid token in the `Authorization`
header.

## Generating an API Key

1. Log in to the CloudDesk dashboard.
2. Navigate to **Settings → Developer → API Keys**.
3. Click **Generate New Key**. Keys are shown only once, so copy and store
   them securely (e.g., in a secrets manager or `.env` file).
4. Each account can have up to 5 active API keys at a time.

## Making an Authenticated Request

Include the token in the `Authorization` header using the `Bearer` scheme:

```
GET /v1/tickets HTTP/1.1
Host: api.clouddesk.io
Authorization: Bearer cd_live_8f3a1c9d2e7b4f1a
Content-Type: application/json
```

## Common Authentication Errors

| HTTP Status | Error Code | Meaning | Fix |
|---|---|---|---|
| 401 | `invalid_token` | Token is malformed, expired, or revoked | Generate a new key from the dashboard |
| 401 | `missing_authorization_header` | The `Authorization` header was not sent | Add the header to every request |
| 403 | `insufficient_scope` | The key does not have permission for this endpoint | Regenerate a key with the correct scope (read/write/admin) |
| 429 | `rate_limit_exceeded` | Too many requests in a short window | Implement exponential backoff (see Rate Limits article) |

## Token Expiration and Rotation

- Live API keys (`cd_live_*`) do not expire automatically but can be
  manually revoked at any time from the dashboard.
- Sandbox keys (`cd_test_*`) expire after 90 days of inactivity.
- We recommend rotating production keys every 6 months as a security
  best practice.

## OAuth 2.0 (For Partner Integrations)

For integrations that act on behalf of multiple customers, use the OAuth
2.0 Authorization Code flow instead of static API keys:

1. Redirect the user to `https://auth.clouddesk.io/oauth/authorize`.
2. After consent, CloudDesk redirects back with a `code` parameter.
3. Exchange the code for an `access_token` and `refresh_token` at
   `https://auth.clouddesk.io/oauth/token`.
4. Access tokens expire after 1 hour; use the refresh token to obtain a
   new one without requiring the user to log in again.

## Troubleshooting Checklist

- Confirm the header is exactly `Authorization: Bearer <token>` (note the
  space after "Bearer").
- Confirm the key has not been revoked in the dashboard's API Keys list.
- Confirm you are using the correct base URL for your environment
  (`api.clouddesk.io` for production, `sandbox-api.clouddesk.io` for
  testing).
- Check the `X-Request-Id` returned in the response headers and provide it
  to support if you need to escalate the issue.
