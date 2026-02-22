# ⟁ Aether Capsule

> Send messages and files to your future self. Delivered exactly 365 days later.

## Project Structure

```
aether_capsule/
├── app.py              # Flask server — the Post Office
├── database.py         # SQLite logic — the Logbook
├── scheduler.py        # APScheduler — the Sentry
├── mailer.py           # smtplib email delivery
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── static/
│   └── index.html      # Single-page frontend
└── capsules/           # Uploaded files (auto-created)
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure email credentials
```bash
cp .env.example .env
# Edit .env with your SMTP credentials
```

> **Gmail users:** Enable 2-Factor Auth and generate an [App Password](https://myaccount.google.com/apppasswords). Use that as `SMTP_PASS`.

### 3. Load environment variables & run
```bash
# Linux / macOS
export $(grep -v '^#' .env | xargs)
python app.py

# Windows (PowerShell)
Get-Content .env | ForEach-Object { if ($_ -notmatch '^#' -and $_ -ne '') { $k,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($k,$v) } }
python app.py
```

The server starts at **http://localhost:5000**

## How It Works

| Step | What happens |
|------|-------------|
| User submits form | Flask receives POST with email, message, optional file |
| Storage | File saved to `/capsules/`, record inserted into `aether.db` with `send_date = now + 365 days` |
| Scheduler | APScheduler wakes at **00:01 AM** daily |
| Delivery | Queries `SELECT * WHERE send_date <= today AND delivered = 0`, sends email via SMTP, marks record delivered |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Your email address | — |
| `SMTP_PASS` | SMTP password / App Password | — |

## Manual Delivery Test

To test email delivery without waiting a year:
```python
# In a Python shell from the project directory:
from database import init_db, save_capsule, get_due_capsules
from mailer import send_capsule_email
from datetime import datetime

init_db()

# Create a test capsule with send_date in the past
from datetime import timedelta
cid = save_capsule("you@email.com", "Hello future me!", None, datetime.now() - timedelta(days=1))
due = get_due_capsules(datetime.now())
send_capsule_email(due[0])
```

## Security Notes

- The `/capsules` folder is server-side only — not web-accessible
- File uploads are validated by extension and capped at 10MB
- Filenames are sanitized with `werkzeug.utils.secure_filename`
- SMTP credentials are environment variables, never hardcoded
