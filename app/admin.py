from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from flask_bcrypt import Bcrypt
from app import db, limiter
from app.models import Contact, NewsletterSubscriber, ResearchDownload

admin = Blueprint("admin", __name__, url_prefix="/admin")
bcrypt = Bcrypt()

# ── Hard-coded credentials ─────────────────────────────────────────────────────
ADMIN_EMAIL = "pujanadhikari301@gmail.com"
# bcrypt hash of "DrishtiEarth2026!"
ADMIN_PASSWORD_HASH = "$2b$12$0Unk03Qc5yUvqft1bbVa3.mJzoYcmb.KCZwXDzV7Vg1o2bshZZto6"


# ── Auth decorator ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


# ── Login / Logout ─────────────────────────────────────────────────────────────
@admin.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes")
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and bcrypt.check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["admin_logged_in"] = True
            session.permanent = False
            return redirect(url_for("admin.dashboard"))
        else:
            error = "Invalid credentials."

    return render_template("admin/login.html", error=error)


@admin.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@admin.route("/")
@login_required
def dashboard():
    stats = {
        "total_contacts": Contact.query.count(),
        "unresponded_contacts": Contact.query.filter_by(responded=False).count(),
        "total_subscribers": NewsletterSubscriber.query.filter_by(active=True).count(),
        "total_downloads": ResearchDownload.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


# ── Contacts ───────────────────────────────────────────────────────────────────
@admin.route("/contacts")
@login_required
def contacts():
    rows = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template("admin/contacts.html", contacts=rows)


@admin.route("/contacts/<int:contact_id>/respond", methods=["POST"])
@login_required
def toggle_responded(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    contact.responded = not contact.responded
    db.session.commit()
    return redirect(url_for("admin.contacts"))


# ── Subscribers ────────────────────────────────────────────────────────────────
@admin.route("/subscribers")
@login_required
def subscribers():
    rows = NewsletterSubscriber.query.order_by(NewsletterSubscriber.created_at.desc()).all()
    return render_template("admin/subscribers.html", subscribers=rows)


# ── Downloads ──────────────────────────────────────────────────────────────────
@admin.route("/downloads")
@login_required
def downloads():
    rows = ResearchDownload.query.order_by(ResearchDownload.created_at.desc()).all()
    return render_template("admin/downloads.html", downloads=rows)
