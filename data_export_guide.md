# Data Export Guide

## What Can Be Exported

- All tickets and their full conversation history (CSV or JSON)
- Knowledge base articles (Markdown ZIP)
- Team member list and roles (CSV)
- Billing and invoice history (CSV or PDF bundle)

## Requesting an Export

1. Go to **Settings → Data → Export Data**.
2. Choose the data type and date range.
3. Click "Request Export." Exports are generated asynchronously — you'll
   receive an email with a secure download link once ready.
4. Large exports (full ticket history for accounts with 100,000+
   tickets) can take up to 24 hours to generate.

## Download Link Expiration

Export download links expire after 7 days for security reasons. If your
link expires before you download it, simply request a new export — no
need to contact support for this.

## Scheduled Recurring Exports (Enterprise)

Enterprise accounts can configure a recurring export (daily, weekly, or
monthly) that automatically delivers a file to a connected S3 bucket or
SFTP server, configured under Settings → Data → Scheduled Exports.

## GDPR / Data Subject Requests

If you need to export or delete a specific individual's personal data
(e.g., an end-user who submitted a support ticket) to comply with a GDPR
or CCPA data subject request, use the "Personal Data Request" tool under
Settings → Data → Privacy Tools rather than a standard export, since
this requires different handling to ensure complete and verifiable
removal. Requests involving full erasure must be reviewed by our privacy
team before execution and cannot be reversed once completed.

## API-Based Export

For programmatic access, use the `GET /v1/exports` endpoint to list
completed export jobs and download them directly, useful for automating
nightly backups into your own data warehouse.
