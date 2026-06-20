# SSO / SAML Setup (Enterprise)

## Overview

CloudDesk supports SAML 2.0 single sign-on for Enterprise plans, allowing
your team to log in using your existing identity provider (IdP) such as
Okta, Azure AD, Google Workspace, or OneLogin.

## Setup Steps

1. Go to **Settings → Security → SSO Configuration** (visible only on
   Enterprise plans).
2. Download the CloudDesk SAML metadata file, or copy the **Entity ID**
   and **Assertion Consumer Service (ACS) URL** shown on this page.
3. In your IdP's admin console, create a new SAML application using
   those values.
4. Map the following attributes in your IdP: `email`, `first_name`,
   `last_name`. These are required for CloudDesk to provision accounts
   correctly.
5. Copy the **IdP SSO URL**, **IdP Entity ID**, and **X.509 Certificate**
   from your IdP and paste them into the CloudDesk SSO Configuration
   page.
6. Click "Test Connection" to verify the handshake before enabling
   enforced SSO.

## Just-In-Time (JIT) Provisioning

When enabled, new users who log in via SSO for the first time
automatically get a CloudDesk account created with the default role
("Member"). Without JIT provisioning, an admin must manually invite each
user first.

## Enforcing SSO Org-Wide

Once tested successfully, toggle "Require SSO for all members" to
disable email/password login entirely for your organization. Admins
retain a break-glass password login option for emergency access, which
should be stored securely and used only if the IdP is unreachable.

## Troubleshooting SSO Failures

| Symptom | Likely Cause |
|---|---|
| "Invalid SAML response" error | Certificate mismatch or expired cert in IdP config |
| User redirected back to login repeatedly | Missing required attribute mapping (email/first_name/last_name) |
| "No matching account" error | JIT provisioning disabled and user wasn't pre-invited |
| Works for some users, not others | Group/role assignment rules in IdP excluding certain users |

Issues involving certificate rotation, IdP-side configuration changes, or
suspected SSO security misconfiguration should be escalated to a
technical specialist, as incorrect changes can lock out an entire
organization.
