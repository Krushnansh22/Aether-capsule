# ⟁ Aether Capsule

Send messages and files to your future self. Backend: FastAPI + SQLAlchemy using Supabase (Postgres). A scheduler delivers due capsules via email.

## Quick summary
- FastAPI app serving a simple frontend and API
- SQLAlchemy models stored in PostgreSQL (Supabase)
- APScheduler runs daily delivery jobs
- SMTP used to send emails (use an app password for Gmail)

## Requirements
- Python 3.10+
- Dependencies in requirements.txt (install with pip)

## Setup (Windows)
1. Clone / open project directory:
   ```powershell
   cd d:\Aether-Capsule
   ```

2. Create virtualenv and install:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Create environment file:
   ```powershell
   copy .env.example .env
   # Edit .env and fill values: DATABASE_URL, SMTP_USER, SMTP_PASS, etc.
   ```

4. Start the app (development):
   ```powershell
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
   Visit: http://localhost:8000

## Important environment variables
Fill these in `.env` (see .env.example):
- DATABASE_URL — full Postgres URI from Supabase (postgresql://...?...sslmode=require)
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS — SMTP credentials (use app password for Gmail)
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SECRET_KEY — optional if using Supabase client APIs
- SECRET_KEY — app secret (keep private)

Never commit real secrets to the repo.

## DB notes
- The app uses SQLAlchemy and creates the `capsules` table on startup (init_db()).
- If switching from SQLite to Postgres, ensure DATABASE_URL is correct and accessible.
- For schema migrations in production consider Alembic.

## Testing DB connectivity
Use the included test script:
```powershell
python test_con.py
```
This runs a simple SELECT version() to confirm connection.

## API (high level)
- GET / — serves frontend
- POST /api/capsule — create a capsule (form-data: email, message, file, send_date)
- POST /api/send-capsules — trigger immediate delivery run

Refer to app.py for exact payloads and behavior.

## Scheduler
- start_scheduler() in scheduler.py schedules a daily delivery job (default 00:01).
- For development you can trigger delivery via /api/send-capsules or call deliver_due_capsules() manually.

## Email delivery
- mailer.py uses SMTP to send messages and optional attachments.
- Ensure SMTP credentials are valid and port 587 is allowed outbound.

## Troubleshooting
- DNS / connection errors to Supabase: verify DATABASE_URL, network/firewall, and Supabase project state.
- SMTP auth errors: check SMTP_USER and SMTP_PASS (use app password for Gmail).
- "Tables not created" — check logs for init_db errors and confirm engine can connect.

## Production notes
- Run behind a process manager (systemd, supervisor) and a production-ready ASGI server.
- Move uploaded files out of the repo to object storage (S3) for scalability.
- Secure keys and restrict CORS/origins.

## Files of interest
- app.py — FastAPI app and endpoints
- database.py — SQLAlchemy models & DB helpers
- mailer.py — SMTP sending code
- scheduler.py — APScheduler jobs
- test_con.py — DB connectivity tester
- .env.example — environment template

## License
Example code — adapt, secure, and test before production use.