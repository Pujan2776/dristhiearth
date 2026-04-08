from datetime import datetime, timezone
from app import db


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organisation = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    service_interest = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    responded = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organisation": self.organisation,
            "country": self.country,
            "email": self.email,
            "service_interest": self.service_interest,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "responded": self.responded,
        }


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    source_page = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "source_page": self.source_page,
            "created_at": self.created_at.isoformat(),
            "active": self.active,
        }


class ResearchDownload(db.Model):
    __tablename__ = "research_downloads"

    id = db.Column(db.Integer, primary_key=True)
    document_slug = db.Column(db.String(255), nullable=False)
    downloader_email = db.Column(db.String(255), nullable=True)
    organisation = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ip_hash = db.Column(db.String(64), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "document_slug": self.document_slug,
            "downloader_email": self.downloader_email,
            "organisation": self.organisation,
            "created_at": self.created_at.isoformat(),
        }
