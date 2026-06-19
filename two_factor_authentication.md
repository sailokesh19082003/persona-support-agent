# Two-Factor Authentication (2FA)

## Enabling 2FA

1. Go to **Settings → Security → Two-Factor Authentication**.
2. Choose a method: Authenticator App (TOTP) or SMS.
3. For Authenticator App: scan the displayed QR code with an app like
   Google Authenticator, Authy, or 1Password, then enter the 6-digit
   code to confirm.
4. For SMS: enter your phone number and confirm the code sent via text.
5. Save your **backup codes** somewhere safe — these let you log in if
   you lose access to your authenticator device or phone number.

## Logging In With 2FA

After entering your email and password, you'll be prompted for your
6-digit code. Codes refresh every 30 seconds for TOTP apps. If your code
is rejected, check that your device's clock is synced correctly, since
TOTP codes are time-based.

## Lost Access to 2FA Device

If you lose your phone or authenticator app and don't have backup codes
saved:

1. Click "Can't access your authenticator?" on the 2FA prompt screen.
2. Choose "Recover via email" — this sends a verification link to your
   account email, but only if email-based recovery was enabled in your
   security settings.
3. If email recovery is disabled or unavailable, this requires manual
   identity verification by our security team, since disabling 2FA
   without proper verification could allow account takeover.

## Disabling 2FA

Go to Settings → Security → Two-Factor Authentication → Disable. You
will be asked to re-enter your current 2FA code to confirm. We recommend
keeping 2FA enabled at all times, especially for admin accounts.

## Enforcing 2FA for a Team (Admin Feature)

Admins on Pro and Enterprise plans can require all team members to enable
2FA under Settings → Security → Team Policies → Require 2FA. Team members
who haven't set up 2FA within 7 days of this being enabled will be
prompted on their next login and blocked from continuing until they do.
