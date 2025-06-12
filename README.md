# SkaterBater 🛹

**SkaterBater** is a Flask-based web application for tracking skateboarding tricks and practice sessions. Users can add tricks to their personal dashboard, update learning statuses (To Learn, In Progress, Mastered), log practice sessions with tries, lands, and notes, and visualize progress through various charts.

---

## 🚀 Key Features

* **User Authentication:** Secure login via **Auth0** OAuth.
* **Trick Library:** Pre-seeded list of flatground/street tricks (e.g., Ollie, Kickflip).
* **Personal Dashboard:** Organize tricks by status: To Learn, In Progress, Mastered.
* **Session Logging:** Record date, number of tries, landed attempts, and optional notes.
* **Data Visualizations:**

  * **Cumulative Lands Over Time** chart.
  * **Landing % Over Time** chart.
* **Responsive UI:** Modern design using reusable CSS components and cards.
* **Containerized:** Docker & Docker Compose setup for easy local development and production.
* **Database Migrations:** Managed with **Flask-Migrate** (Alembic).
* **Seed Data:** `seed_tricks.py` to populate tricks and optionally sample session logs.

---

## 📁 Project Structure

```
skaterbater/            # Project root
├── app/                # Application package
│   ├── __init__.py     # Factory (`create_app`), extension setup
│   ├── models.py       # SQLAlchemy models: Trick, UserTrick, PracticeLogEntry
│   ├── oauth.py        # Auth0 OAuth client setup
│   ├── routes.py       # Flask blueprints and route handlers
│   ├── static/         # Static assets (CSS, JS, images)
│   └── templates/      # Jinja2 HTML templates
├── migrations/         # Alembic migration scripts
├── Dockerfile          # Production-ready container image build
├── docker-compose.yml  # Local development orchestration
├── run.py              # Dev entrypoint (Flask server)
├── wsgi.py             # Production WSGI entrypoint (Gunicorn)
├── config.py           # Configuration classes (Config, ProductionConfig, DevelopmentConfig)
├── requirements.txt    # Python dependencies
├── seed_tricks.py      # Script to seed the database with tricks (and sessions)
└── .env.example        # Example environment variables file
```

---

## 📦 Prerequisites

* [Docker & Docker Compose](https://docs.docker.com/get-docker/)
* [Python 3.13](https://www.python.org/downloads/) (for non-Docker dev)
* Auth0 account and application

---

## ⚙️ Setup & Local Development

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/skaterbater.git
   cd skaterbater
   ```

2. **Environment Variables**:

   * Copy the example file:

     ```bash
     cp .env.example .env
     ```
   * Fill in your Auth0 credentials and a local DATABASE\_URL (e.g., `postgresql://skateruser:skaterpass@db:5432/skaterdb`).

3. **Docker Compose**:

   * During this step 'flask db upgrade' gets called automatically.
   * As well as seed_tricks.py is run during this step to seed the database with tricks.


   ```bash
   docker compose up -d
   ```

4. **Access the App**:
   Open your browser at `http://localhost:8000`.

---

## 🛠️ Manual (Non-Docker) Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables in your shell or via `.env`.

3. Initialize and upgrade the database:

   ```bash
   flask db init       # only first time
   flask db migrate
   flask db upgrade
   python seed_tricks.py
   ```

4. Run the development server:

   ```bash
   flask run
   ```
---
## 🎯 Environment Variables (`.env`)

```ini
# Flask core
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret
DATABASE_URL=postgresql://skateruser:skaterpass@db:5432/skaterdb

# Auth0
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_DOMAIN=YOUR_DOMAIN.auth0.com
AUTH0_CALLBACK_URL=http://localhost:8000/callback
```
---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
