# API Rate Limits

## Default Limits

| Plan | Requests / Minute | Burst Allowance |
|---|---|---|
| Free | 60 | 10 |
| Pro | 600 | 100 |
| Enterprise | 6,000 | 1,000 |

Limits are applied per API key, not per account. If you use multiple keys,
each key has its own quota.

## Reading Rate Limit Headers

Every API response includes the following headers so you can track your
usage in real time:

```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 542
X-RateLimit-Reset: 1718700000
```

`X-RateLimit-Reset` is a Unix timestamp indicating when the limit window
resets.

## Handling 429 Responses

When you exceed your limit, the API returns `429 Too Many Requests` with a
`Retry-After` header (in seconds). Clients should implement exponential
backoff with jitter:

```python
import time, random

def call_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        response = func()
        if response.status_code != 429:
            return response
        wait = (2 ** attempt) + random.uniform(0, 1)
        time.sleep(wait)
    raise Exception("Max retries exceeded")
```

## Requesting a Limit Increase

Enterprise customers experiencing sustained high-volume traffic can request
a custom rate limit by contacting their account manager or opening a
ticket under the "API & Integrations" category. Increases typically take
1-2 business days to take effect and require justification (expected
requests/minute, use case, and integration architecture).

## Best Practices to Avoid Hitting Limits

- Batch requests where the API supports it (e.g., bulk ticket fetch
  instead of one-by-one).
- Cache responses that don't change frequently (e.g., team member lists).
- Use webhooks instead of polling endpoints for real-time updates.
- Stagger scheduled jobs so they don't all fire at the same minute.
