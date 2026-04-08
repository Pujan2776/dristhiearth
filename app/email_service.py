import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)


def send_contact_notification(contact) -> bool:
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    if not api_key:
        logger.warning("SENDGRID_API_KEY not set — skipping email notification")
        return False

    to_email = os.environ.get("CONTACT_EMAIL", "pujanadhikari301@gmail.com")
    from_email = os.environ.get("FROM_EMAIL", "info@dristhiearth.com")

    subject = f"New Enquiry — Dristhi Earth: {contact.name} from {contact.organisation}"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A1A0C; color: #F4F0E8; padding: 32px;">
        <h2 style="color: #C8943A; border-bottom: 1px solid #1E3322; padding-bottom: 16px;">
            New Enquiry — Dristhi Earth
        </h2>

        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px 0; color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; width: 160px;">Name</td>
                <td style="padding: 8px 0; color: #F4F0E8;">{contact.name}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Organisation</td>
                <td style="padding: 8px 0; color: #F4F0E8;">{contact.organisation}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Country</td>
                <td style="padding: 8px 0; color: #F4F0E8;">{contact.country}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Email</td>
                <td style="padding: 8px 0; color: #F4F0E8;"><a href="mailto:{contact.email}" style="color: #4A9E5C;">{contact.email}</a></td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Service Interest</td>
                <td style="padding: 8px 0; color: #F4F0E8;">{contact.service_interest or 'Not specified'}</td>
            </tr>
        </table>

        <div style="margin-top: 24px; padding: 16px; background: #132015; border-left: 3px solid #C8943A;">
            <p style="color: #7A9B7E; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 8px 0;">Message</p>
            <p style="color: #F4F0E8; margin: 0; line-height: 1.6;">{contact.message}</p>
        </div>

        <p style="color: #7A9B7E; font-size: 12px; margin-top: 24px;">
            Received: {contact.created_at.strftime('%Y-%m-%d %H:%M UTC') if contact.created_at else 'Unknown'}<br>
            IP: {contact.ip_address or 'Unknown'}
        </p>
    </div>
    """

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info("Contact notification sent, status: %s", response.status_code)
        return True
    except Exception as exc:
        logger.error("Failed to send contact notification: %s", exc)
        return False


def send_enquiry_confirmation(contact) -> bool:
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    if not api_key:
        logger.warning("SENDGRID_API_KEY not set — skipping enquiry confirmation")
        return False

    from_email = os.environ.get("FROM_EMAIL", "info@dristhiearth.com")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f5f5f0;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f0;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#0A1A0C;padding:32px 40px 28px;">
              <p style="margin:0;font-family:'Helvetica Neue',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#7A9B7E;">Environmental Intelligence</p>
              <h1 style="margin:8px 0 0;font-family:Georgia,'Times New Roman',serif;font-size:24px;font-weight:400;color:#F4F0E8;">Dristhi Earth</h1>
              <div style="margin-top:20px;height:2px;background:#C8943A;width:48px;"></div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:40px 40px 32px;">
              <p style="margin:0 0 20px;font-size:16px;color:#1a1a1a;line-height:1.6;">Dear {contact.name},</p>
              <p style="margin:0 0 16px;font-size:15px;color:#333333;line-height:1.7;">Thank you for reaching out to Dristhi Earth.</p>
              <p style="margin:0 0 16px;font-size:15px;color:#333333;line-height:1.7;">We have received your enquiry and will respond within <strong>48 hours</strong>.</p>
              <p style="margin:0 0 28px;font-size:15px;color:#555555;line-height:1.7;">Dristhi Earth provides environmental intelligence for the Hindu Kush Himalayan region — working with governments, development organisations, and research institutions across South Asia.</p>

              <div style="border-left:3px solid #C8943A;padding:16px 20px;background:#fafaf8;margin-bottom:28px;">
                <p style="margin:0;font-size:14px;color:#555555;line-height:1.7;">In the meantime, you can learn more about our work at <a href="https://dristhiearth.com" style="color:#4A9E5C;text-decoration:none;">dristhiearth.com</a></p>
              </div>

              <p style="margin:0 0 4px;font-size:15px;color:#333333;">With regards,</p>
              <p style="margin:0 0 2px;font-size:15px;color:#1a1a1a;font-weight:600;">Pujan Adhikari</p>
              <p style="margin:0 0 2px;font-size:13px;color:#777777;">Founder, Dristhi Earth</p>
              <p style="margin:0 0 2px;font-size:13px;color:#777777;"><a href="mailto:info@dristhiearth.com" style="color:#4A9E5C;text-decoration:none;">info@dristhiearth.com</a></p>
              <p style="margin:0;font-size:13px;color:#777777;"><a href="https://dristhiearth.com" style="color:#4A9E5C;text-decoration:none;">dristhiearth.com</a></p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0a1208;padding:20px 40px;border-top:1px solid #1E3322;">
              <p style="margin:0;font-size:11px;color:#7A9B7E;line-height:1.6;">This is an automated confirmation. Please do not reply to this email.</p>
              <p style="margin:6px 0 0;font-size:11px;color:#4a6a4e;">Dristhi Earth Limited &mdash; Preston, Lancashire, UK</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    message = Mail(
        from_email=from_email,
        to_emails=contact.email,
        subject="Thank you for your enquiry — Dristhi Earth",
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info("Enquiry confirmation sent to %s, status: %s", contact.email, response.status_code)
        return True
    except Exception as exc:
        logger.error("Failed to send enquiry confirmation to %s: %s", contact.email, exc)
        return False


def send_newsletter_confirmation(email: str) -> bool:
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    if not api_key:
        return False

    from_email = os.environ.get("FROM_EMAIL", "info@dristhiearth.com")

    html_content = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0A1A0C; color: #F4F0E8; padding: 32px;">
        <h2 style="color: #C8943A;">Dristhi Earth — Research Updates</h2>
        <p style="color: #F4F0E8; line-height: 1.7;">
            You are now subscribed to Dristhi Earth research updates. We publish
            analysis on environmental intelligence, climate finance flows, and
            data infrastructure across the Hindu Kush Himalayan region.
        </p>
        <p style="color: #7A9B7E; font-size: 13px;">
            Expect infrequent, substantive communications — not newsletters in the
            conventional sense.
        </p>
        <hr style="border: none; border-top: 1px solid #1E3322; margin: 24px 0;">
        <p style="color: #7A9B7E; font-size: 12px;">
            Dristhi Earth Limited &mdash; Preston, Lancashire, UK
        </p>
    </div>
    """

    message = Mail(
        from_email=from_email,
        to_emails=email,
        subject="Dristhi Earth — Research Updates Confirmed",
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True
    except Exception as exc:
        logger.error("Failed to send newsletter confirmation: %s", exc)
        return False
