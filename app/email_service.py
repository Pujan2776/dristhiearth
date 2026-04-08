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
