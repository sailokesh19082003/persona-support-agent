# Third-Party Integrations

## Available Integrations

CloudDesk natively integrates with: Slack, Microsoft Teams, Jira,
Salesforce, HubSpot, Zapier, and Shopify. All integrations are managed
under **Settings → Integrations**.

## Slack Integration

Connect a workspace to receive ticket notifications in a chosen channel
and reply to tickets directly from Slack using `/clouddesk reply`. Setup
requires a workspace Admin to authorize the OAuth connection once;
individual members don't need separate authorization.

## Jira Integration

Link CloudDesk tickets to Jira issues bidirectionally — status changes in
either system sync to the other within about 1 minute. Useful for
escalating customer-reported bugs to engineering without manual
re-entry. Requires a Jira Cloud (not Server/Data Center) instance and an
API token generated from your Atlassian account.

## Zapier Integration

For integrations not natively supported, use our Zapier app to connect
CloudDesk to over 5,000 other tools. Common "Zaps" include creating a
CloudDesk ticket from a new Typeform response, or posting to a Discord
channel on ticket escalation.

## Salesforce Integration

Syncs contact and account data between Salesforce and CloudDesk so
support agents can see a customer's deal stage and account value
directly inside a ticket. Initial sync of historical data can take
several hours for large Salesforce instances (100,000+ records).

## Troubleshooting Integration Sync Issues

| Symptom | Likely Cause |
|---|---|
| Integration shows "Connected" but no data syncs | OAuth token expired; disconnect and reconnect the integration |
| Duplicate records created | Matching field (usually email) differs in formatting between systems (e.g., casing, whitespace) |
| Sync delay longer than expected | Large data volume queued; check Integration Logs for queue depth |
| "Permission denied" error from third-party | The connected account lacks admin rights in the third-party tool |

## Custom Integrations via API

If a native integration doesn't exist for your tool, you can build a
custom one using the CloudDesk REST API combined with webhooks — see the
API Authentication Guide and Webhook Integration Guide for the building
blocks.
