import hashlib
import logging
import os

logger = logging.getLogger(__name__)
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_from_directory,
    abort,
    Response,
)
from app import db, limiter
from app.models import Contact, NewsletterSubscriber, ResearchDownload
from app.validators import is_valid_email, are_required_fields_present, sanitise_string
from app.email_service import send_contact_notification, send_enquiry_confirmation, send_newsletter_confirmation

main = Blueprint("main", __name__)


def get_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()


# ── Page routes ────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/services")
def services():
    return render_template("services.html")


@main.route("/research")
def research():
    return render_template("research.html")


@main.route("/partners")
def partners():
    return render_template("partners.html")


@main.route("/contact")
def contact():
    return render_template("contact.html")


# ── API routes ─────────────────────────────────────────────────────────────────

@main.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Sitemap: https://www.dristhiearth.com/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@main.route("/sitemap.xml")
def sitemap():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [
        "/",
        "/about",
        "/services",
        "/research",
        "/partners",
        "/contact",
    ]
    base = "https://www.dristhiearth.com"
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in urls:
        xml_parts.append(
            f"  <url>\n"
            f"    <loc>{base}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>{'1.0' if path == '/' else '0.8'}</priority>\n"
            f"  </url>"
        )
    xml_parts.append("</urlset>")
    return Response("\n".join(xml_parts), mimetype="application/xml")


@main.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@main.route("/api/contact", methods=["POST"])
@limiter.limit("5 per hour")
def api_contact():
    data = request.get_json(silent=True) or {}

    required = ["name", "organisation", "country", "email", "message"]
    ok, missing = are_required_fields_present(data, required)
    if not ok:
        return jsonify({"success": False, "errors": {f: "This field is required." for f in missing}}), 422

    email = sanitise_string(data.get("email", ""))
    if not is_valid_email(email):
        return jsonify({"success": False, "errors": {"email": "Please enter a valid email address."}}), 422

    message_text = sanitise_string(data.get("message", ""), max_length=5000)
    if len(message_text) < 10:
        return jsonify({"success": False, "errors": {"message": "Message must be at least 10 characters."}}), 422

    contact = Contact(
        name=sanitise_string(data.get("name", ""), max_length=255),
        organisation=sanitise_string(data.get("organisation", ""), max_length=255),
        country=sanitise_string(data.get("country", ""), max_length=100),
        email=email,
        service_interest=sanitise_string(data.get("service_interest", ""), max_length=100) or None,
        message=message_text,
        ip_address=get_ip(),
    )

    try:
        db.session.add(contact)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "errors": {"general": "A server error occurred. Please try again."}}), 500

    try:
        send_contact_notification(contact)
    except Exception as exc:
        logger.error("send_contact_notification failed: %s", exc)

    try:
        send_enquiry_confirmation(contact)
    except Exception as exc:
        logger.error("send_enquiry_confirmation failed: %s", exc)

    return jsonify({"success": True, "message": "Your enquiry has been received. We will respond within 48 hours."}), 201


@main.route("/api/newsletter", methods=["POST"])
@limiter.limit("3 per hour")
def api_newsletter():
    data = request.get_json(silent=True) or {}

    email = sanitise_string(data.get("email", ""))
    if not email:
        return jsonify({"success": False, "errors": {"email": "Email address is required."}}), 422
    if not is_valid_email(email):
        return jsonify({"success": False, "errors": {"email": "Please enter a valid email address."}}), 422

    source_page = sanitise_string(data.get("source_page", ""), max_length=100) or "unknown"

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        if not existing.active:
            existing.active = True
            db.session.commit()
            return jsonify({"success": True, "message": "Your subscription has been reactivated."}), 200
        return jsonify({"success": True, "message": "You are already subscribed to research updates."}), 200

    subscriber = NewsletterSubscriber(email=email, source_page=source_page)
    try:
        db.session.add(subscriber)
        db.session.commit()
        send_newsletter_confirmation(email)
        return jsonify({"success": True, "message": "You have been added to our research updates list."}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "errors": {"general": "A server error occurred. Please try again."}}), 500


@main.route("/api/research/download/<slug>")
def api_research_download(slug):
    allowed_slugs = {
        "hkh-intelligence-gap-2026": "HKH_Intelligence_Gap_Market_Analysis_2026.pdf",
    }

    if slug not in allowed_slugs:
        abort(404)

    filename = allowed_slugs[slug]
    pdf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "research")

    ip = get_ip()
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    email = request.args.get("email", "")
    organisation = request.args.get("organisation", "")

    record = ResearchDownload(
        document_slug=slug,
        downloader_email=email if is_valid_email(email) else None,
        organisation=sanitise_string(organisation, max_length=255) or None,
        ip_hash=ip_hash,
    )
    try:
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        return send_from_directory(pdf_dir, filename, as_attachment=True)
    except Exception:
        return jsonify({
            "success": False,
            "message": "This document is not yet available. Please check back after April 2026."
        }), 404
