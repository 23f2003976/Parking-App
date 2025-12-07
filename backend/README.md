# Flask + VueJS Application

This project is built using the required frameworks:

- Flask for API
- VueJS for UI
- Bootstrap for styling
- SQLite database
- Redis for caching
- Redis + Celery for batch/background jobs
- Jinja2 only for initial HTML entry point (if using CDN)

---

## Project Structure

Backend (Flask)
- Auth endpoints (register, login)
- Token-based authentication
- SQLite using SQLAlchemy
- Redis caching
- Celery for batch jobs
- Migrations via Flask-Migrate

Frontend (VueJS)
- VueJS or Vue CLI
- Bootstrap for UI components
- Calls backend API

---