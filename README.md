# Drishti Earth

Environmental Intelligence for the Hindu Kush Himalayan Region.

**Website:** dristhiearth.com  
**Stack:** Python Flask · SQLAlchemy · SendGrid · Vanilla JS · Gunicorn

---

## Local Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd dristhiearth

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set SECRET_KEY and (optionally) SENDGRID_API_KEY

# 5. Run the development server
python run.py
```

The site will be available at **http://localhost:5000**

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `FLASK_ENV` | No | `development` (default) or `production` |
| `SECRET_KEY` | Yes | Long random string for session signing |
| `SENDGRID_API_KEY` | No | SendGrid API key for email notifications — omit to disable email |
| `CONTACT_EMAIL` | No | Destination for contact form notifications (default: `pujanadhikari301@gmail.com`) |
| `FROM_EMAIL` | No | Sender address for outbound emails (default: `info@dristhiearth.com`) |
| `DATABASE_URL` | Production | PostgreSQL connection string. SQLite is used automatically in development. |

---

## Deploying to Render

1. Push this repository to GitHub.
2. In the [Render dashboard](https://dashboard.render.com), select **New → Blueprint**.
3. Connect your GitHub repository. Render will detect `render.yaml` automatically.
4. Set `SENDGRID_API_KEY` manually in the Render environment variables panel (marked `sync: false` in `render.yaml`).
5. Deploy. Render will provision a PostgreSQL database, build the app, and start Gunicorn.

The `DATABASE_URL` is injected automatically from the linked database. The `postgres://` → `postgresql://` prefix replacement in `config.py` handles the legacy Render URL format.

---

## Adding Research PDFs

1. Create the directory if it does not exist:
   ```bash
   mkdir -p static/research
   ```
2. Place the PDF in `static/research/` with the exact filename defined in `app/routes.py`:
   ```python
   allowed_slugs = {
       "hkh-intelligence-gap-2026": "HKH_Intelligence_Gap_Market_Analysis_2026.pdf",
   }
   ```
3. To add a new document, add an entry to the `allowed_slugs` dict and place the matching PDF in `static/research/`.

The download endpoint logs every download to the `research_downloads` table (slug, email if provided, IP hash, timestamp).

---

## Querying the Database (SQLite, development)

```bash
# Open the database
sqlite3 drishti.db

# List all contact enquiries
SELECT id, name, organisation, country, email, created_at FROM contacts;

# List newsletter subscribers
SELECT email, source_page, created_at, active FROM newsletter_subscribers;

# List research downloads
SELECT document_slug, downloader_email, organisation, created_at FROM research_downloads;

# Mark a contact as responded
UPDATE contacts SET responded = 1 WHERE id = 1;

# Exit
.quit
```

---

## Project Structure

```
dristhiearth/
├── app/
│   ├── __init__.py        # Flask app factory, db init, blueprints
│   ├── models.py          # SQLAlchemy models: Contact, NewsletterSubscriber, ResearchDownload
│   ├── routes.py          # Page routes + /api/* endpoints
│   ├── email_service.py   # SendGrid integration
│   └── validators.py      # Email validation and field checking
├── static/
│   ├── css/styles.css     # Complete stylesheet
│   └── js/main.js         # Nav, AJAX forms, scroll animations
├── templates/
│   ├── base.html          # Base layout: nav, footer, head
│   ├── index.html         # Homepage
│   ├── about.html         # About / founder
│   ├── services.html      # Four service lines
│   ├── research.html      # Research and publications
│   ├── partners.html      # Nine partner categories
│   ├── contact.html       # AJAX contact form
│   └── 404.html           # Error page
├── run.py                 # Entry point
├── config.py              # DevelopmentConfig / ProductionConfig
├── requirements.txt
├── Procfile               # Gunicorn for Render / Heroku
├── render.yaml            # Render Blueprint configuration
├── .env.example
└── .gitignore
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/api/contact` | Submit contact form. Body: `name`, `organisation`, `country`, `email`, `message`, `service_interest` |
| `POST` | `/api/newsletter` | Subscribe to research updates. Body: `email`, `source_page` |
| `GET` | `/api/research/download/<slug>` | Log and serve a research PDF |

---

## Licence

Copyright 2026 Drishti Earth Limited. All rights reserved.
