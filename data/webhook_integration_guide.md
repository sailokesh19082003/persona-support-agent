# Webhook Integration Guide

## Overview

Webhooks let your application receive real-time notifications when
events happen in CloudDesk (e.g., a ticket is created or its status
changes), instead of polling the API.

## Setting Up a Webhook

1. Go to **Settings → Developer → Webhooks → Add Endpoint**.
2. Enter your publicly reachable HTTPS URL.
3. Select which event types to subscribe to (e.g., `ticket.created`,
   `ticket.updated`, `ticket.escalated`).
4. Save. CloudDesk immediately sends a `ping` event so you can verify
   your endpoint is reachable and returns a `200` status.

## Payload Format

```json
{
  "event": "ticket.created",
  "timestamp": "2026-06-18T10:15:00Z",
  "data": {
    "ticket_id": "tk_9931",
    "persona": "Frustrated User",
    "status": "open"
  }
}
```

## Verifying Webhook Signatures

Every webhook request includes an `X-CloudDesk-Signature` header, an
HMAC-SHA256 hash of the raw request body using your webhook signing
secret (found on the same settings page). Always verify this signature
before processing the payload, to confirm the request genuinely came
from CloudDesk and wasn't spoofed:

```python
import hmac, hashlib

def verify_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

## Retry Behavior

If your endpoint doesn't return a `2xx` status, CloudDesk retries
delivery up to 5 times with exponential backoff (1 min, 5 min, 15 min,
1 hr, 6 hr). After 5 failed attempts, the event is marked as failed and
visible in the Webhook Logs page, where you can manually trigger a
resend.

## Common Issues

| Issue | Likely Cause |
|---|---|
| No events received | Endpoint URL unreachable, or firewall blocking CloudDesk's IP range |
| Duplicate events | Normal — webhooks are "at least once" delivery; use the event `id` field to deduplicate |
| Signature verification fails | Using the wrong signing secret, or modifying the body before verifying (verify on the raw bytes, not a re-serialized JSON object) |
