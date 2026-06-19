# Account Lockout Troubleshooting

## Why Accounts Get Locked

CloudDesk automatically locks an account after **5 consecutive failed
login attempts** within a 15-minute window, as a brute-force protection
measure. A lock can also occur if our fraud-detection system flags
unusual login activity (e.g., login attempts from many different
countries within a short time).

## How Long Does a Lockout Last?

- Standard failed-attempt lockout: 30 minutes, after which it unlocks
  automatically.
- Fraud-detection lockout: requires identity verification via email
  before it unlocks (it does not auto-expire).

## Unlocking Your Account

1. Wait for the 30-minute automatic unlock if it was a standard lockout
   (check the lockout email for the exact unlock time).
2. If you need immediate access, click "Unlock via Email" on the login
   page. This sends a one-time unlock link to your registered email,
   valid for 15 minutes.
3. If you don't receive the email within a few minutes, check your spam
   folder and confirm the email address on file is correct (you may need
   a teammate with admin access to verify this for you if you can't log
   in).

## Repeated Lockouts

If your account keeps getting locked even with correct credentials, this
is often caused by:
- An old saved password being auto-filled by your browser or password
  manager.
- A cached session in a mobile app that is silently retrying with an
  outdated token.
- Multiple team members sharing one login (not recommended — each user
  should have a separate seat).

## Lockouts Tied to Suspicious Activity

If the lockout reason shown is "suspicious activity detected," this
indicates our fraud system flagged the login pattern. These cases
require manual review by the security team before access is restored,
since automated unlocking is intentionally disabled for this category to
protect the account.
