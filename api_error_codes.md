# API Error Codes Reference

## Format

All API errors return a JSON body in this shape:

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Ticket with id 8821 does not exist",
    "request_id": "req_3f9a2b"
  }
}
```

## Common Error Codes

| Code | HTTP Status | Description |
|---|---|---|
| `invalid_token` | 401 | Authentication token is invalid, expired, or revoked |
| `insufficient_scope` | 403 | The token does not have permission for this action |
| `resource_not_found` | 404 | The requested object does not exist |
| `validation_error` | 422 | One or more request fields failed validation |
| `rate_limit_exceeded` | 429 | Too many requests; see Rate Limits article |
| `internal_server_error` | 500 | Unexpected failure on our end; retry with backoff |
| `service_unavailable` | 503 | Temporary outage; check status.clouddesk.io |

## 500 and 503 Errors

If you see `internal_server_error` or `service_unavailable`:

1. Check `status.clouddesk.io` for an active incident.
2. Retry the request after a short delay using exponential backoff.
3. If the error persists for more than 10 minutes and there is no listed
   incident, open a support ticket with the `request_id` from the error
   body — this allows engineering to trace the exact failed call in logs.

## 422 Validation Errors

Validation errors include a `fields` array describing exactly which inputs
failed and why:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "fields": [
      {"field": "email", "issue": "must be a valid email address"},
      {"field": "priority", "issue": "must be one of: low, medium, high, urgent"}
    ]
  }
}
```

## Idempotency

For `POST` requests that create resources (e.g., creating a ticket),
include an `Idempotency-Key` header with a unique UUID. If the same key is
sent twice (e.g., due to a network retry), CloudDesk returns the original
response instead of creating a duplicate resource.
