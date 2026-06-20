# Mobile App Troubleshooting

## App Won't Load / Stuck on Splash Screen

1. Force-close the app completely and reopen it.
2. Confirm you're on app version 4.2 or later (Settings → About in the
   app) — versions before 4.0 are no longer supported and may fail to
   connect.
3. Check your internet connection; the app requires a stable connection
   for the initial sync even if you plan to work offline afterward.
4. If the issue persists, uninstall and reinstall the app. Your data is
   stored server-side, so reinstalling does not cause data loss.

## Push Notifications Not Working

- Confirm notifications are enabled for the app in your phone's system
  settings (Settings → Apps → CloudDesk → Notifications on Android;
  Settings → Notifications → CloudDesk on iOS).
- Inside the app, check Settings → Notifications → Push Notifications is
  toggled on.
- If you recently changed phones, push tokens can take up to 30 minutes
  to re-register after first login on the new device.

## App Crashes on Specific Screens

Crashes tied to a specific screen (e.g., opening a ticket with many
attachments) are usually caused by an outdated app version or a
corrupted local cache. Try: update the app → clear app cache (Android:
Settings → Apps → CloudDesk → Storage → Clear Cache) → restart the app.
On iOS, clearing cache requires reinstalling the app since iOS doesn't
expose a cache-clear option per app.

## Offline Mode

The mobile app caches your most recent 200 tickets for offline viewing.
Changes made offline (replies, status updates) sync automatically once
connectivity is restored. If a sync conflict occurs (e.g., someone else
updated the same ticket while you were offline), the app will prompt you
to choose which version to keep.

## Biometric Login Not Appearing

Biometric login (Face ID / fingerprint) requires that you've logged in
with email/password at least once on that device and enabled it under
Settings → Security → Biometric Login. It is not available immediately
after a fresh install before the first standard login.
