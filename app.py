import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db, save_capsule, get_due_capsules
from mailer import send_capsule_email
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ROOT = Path(__file__).parent
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")

scheduler = BackgroundScheduler()

def send_due_capsules():
    """Send all due capsules"""
    from database import mark_delivered
    try:
        due_capsules = get_due_capsules(datetime.now())
        for capsule in due_capsules:
            if send_capsule_email(capsule):
                mark_delivered(capsule['id'])
                logger.info(f"✓ Capsule email sent to: {capsule.get('email', 'Unknown')}")
            else:
                logger.warning(f"✗ Failed to send capsule {capsule['id']} to {capsule.get('email', 'Unknown')}")
    except Exception as e:
        logger.error(f"Error sending capsules: {e}", exc_info=True)

@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()
    scheduler.add_job(send_due_capsules, "interval", minutes=10, id="send_capsules")
    scheduler.start()
    logger.info("Aether Capsule server started. Capsule scheduler running every 1 minute.")

@app.get("/")
async def index():
    index_path = ROOT / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)

@app.post("/api/capsule")
async def create_capsule(
    email: str = Form(...),
    message: str = Form(...),
    file: UploadFile | None = File(None),
):
    if not email or "@" not in email:
        return JSONResponse({"success": False, "error": "Invalid email address."}, status_code=400)
    if not message.strip():
        return JSONResponse({"success": False, "error": "Message cannot be empty."}, status_code=400)

    file_path = None
    if file and file.filename:
        safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        dest = UPLOADS / safe_name
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = str(dest)
        logger.info(f"Saved uploaded file: {dest}")

    send_date = datetime.now() + timedelta(days=365)
    try:
        capsule_id = save_capsule(email, message, file_path, send_date)
        logger.info(f"Capsule #{capsule_id} sealed for {email}, delivers on {send_date.date()}")
    except Exception as e:
        logger.error(f"Failed to save capsule: {e}", exc_info=True)
        return JSONResponse({"success": False, "error": "Failed to store capsule. Please try again."}, status_code=500)

    return JSONResponse({
        "success": True,
        "capsule_id": capsule_id,
        "deliver_on": send_date.strftime("%B %d, %Y"),
    })

@app.post("/api/send-capsules")
async def trigger_send_capsules():
    """Manual trigger to send due capsules"""
    send_due_capsules()
    return JSONResponse({"success": True, "message": "Capsule sending triggered."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)