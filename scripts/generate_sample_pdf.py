"""
One-time script used to generate password_reset_guide.pdf.
Not part of the runtime application - kept here only for transparency/reproducibility.
Run with: python _generate_pdf.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

doc = SimpleDocTemplate("password_reset_guide.pdf", pagesize=letter,
                         topMargin=0.8*inch, bottomMargin=0.8*inch,
                         leftMargin=0.9*inch, rightMargin=0.9*inch)

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=18, spaceAfter=14)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=8,
                     textColor=colors.HexColor("#1a3a5c"))
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10.5, leading=15, spaceAfter=8)

story = []

story.append(Paragraph("CloudDesk Password Reset Guide", h1))
story.append(Paragraph(
    "This guide covers self-service password resets, troubleshooting reset "
    "emails, and what to do if you've lost access to your account entirely.",
    body))

story.append(Paragraph("1. Resetting Your Password (Self-Service)", h2))
story.append(ListFlowable([
    ListItem(Paragraph("Go to the CloudDesk login page and click \"Forgot password?\" below the login form.", body)),
    ListItem(Paragraph("Enter the email address associated with your account and submit.", body)),
    ListItem(Paragraph("Check your inbox for an email titled \"Reset your CloudDesk password.\" It arrives within 2 minutes.", body)),
    ListItem(Paragraph("Click the reset link inside the email. It is valid for 30 minutes from when it was sent.", body)),
    ListItem(Paragraph("Enter a new password that meets the requirements below, then confirm it to complete the reset.", body)),
], bulletType="1"))

story.append(Paragraph("2. Password Requirements", h2))
story.append(Paragraph(
    "New passwords must be at least 10 characters long and include at least one number "
    "and one special character. Passwords cannot match any of your last 5 previously used "
    "passwords on this account.",
    body))

story.append(Paragraph("3. Not Receiving the Reset Email", h2))
story.append(Paragraph("If the reset email doesn't arrive within a few minutes, check the following in order:", body))
story.append(ListFlowable([
    ListItem(Paragraph("Spam or Promotions folder - search for \"CloudDesk\" directly rather than scrolling.", body)),
    ListItem(Paragraph("Confirm you typed the correct email address - a typo will silently fail without showing an error, for security reasons (we don't reveal whether an email exists in our system).", body)),
    ListItem(Paragraph("Corporate email filters - some company mail servers block automated emails from new senders. Ask your IT team to allowlist no-reply@clouddesk.io.", body)),
    ListItem(Paragraph("Wait at least 10 minutes before requesting a second email, since requesting too many in a row triggers a temporary rate limit of 1 email per 10 minutes.", body)),
], bulletType="1"))

story.append(Paragraph("4. Reset Link Expired or Already Used", h2))
story.append(Paragraph(
    "Reset links are single-use and expire after 30 minutes. If you see \"This link has expired "
    "or already been used,\" simply return to the login page and request a new one - this is "
    "expected behavior and not an error with your account.",
    body))

story.append(Paragraph("5. Locked Out With No Access to Your Email", h2))
story.append(Paragraph(
    "If you no longer have access to the email address on file (for example, it was a former "
    "work email), self-service reset is not possible since the reset link can only be sent to "
    "the registered address. In this situation:",
    body))
story.append(ListFlowable([
    ListItem(Paragraph("If you are part of a team, ask an Owner or Admin on your account to update your email address from Settings -> Team, then attempt the reset again with the new address.", body)),
    ListItem(Paragraph("If you are the sole Owner of the account with no other admins, this requires manual identity verification by a human support specialist, since changing the primary recovery email for an unattended account is a sensitive, irreversible action that cannot be automated.", body)),
], bulletType="1"))

story.append(Paragraph("6. Two-Factor Authentication and Password Resets", h2))
story.append(Paragraph(
    "Resetting your password does not disable two-factor authentication (2FA). After setting a "
    "new password, you will still be prompted for your 2FA code on login. If you have also lost "
    "access to your 2FA device, see the separate Two-Factor Authentication article for recovery "
    "options.",
    body))

story.append(Paragraph("7. Security Best Practices", h2))
story.append(ListFlowable([
    ListItem(Paragraph("Use a unique password for CloudDesk rather than reusing one from another service.", body)),
    ListItem(Paragraph("Enable two-factor authentication for an additional layer of protection.", body)),
    ListItem(Paragraph("If you receive a password reset email you did not request, you can safely ignore it - no action is taken on your account unless the link is clicked and completed. If this happens repeatedly, enable 2FA and consider reporting it to support.", body)),
], bulletType="1"))

doc.build(story)
print("Generated password_reset_guide.pdf")
