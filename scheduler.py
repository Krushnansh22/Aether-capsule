import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_scheduler = None

def deliver_due_capsules():
    """Check for capsules due today and deliver them."""
    from database import get_due_capsules, mark_delivered
    from mailer import send_capsule_email

    logger.info(f"[Sentry] Waking up at {datetime.now().isoformat()} — scanning vault...")
    due = get_due_capsules(datetime.now())

    if not due:
        logger.info("[Sentry] No capsules due. Going back to sleep.")
        return

    logger.info(f"[Sentry] Found {len(due)} capsule(s) to deliver.")

    for capsule in due:
        logger.info(f"[Sentry] Delivering capsule ID={capsule['id']} to {capsule['email']}...")
        success = send_capsule_email(capsule)
        if success:
            mark_delivered(capsule['id'])
        else:
            logger.warning(f"[Sentry] Failed to deliver capsule ID={capsule['id']}. Will retry tomorrow.")

    logger.info("[Sentry] Delivery run complete.")

def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler(daemon=True)

    _scheduler.add_job(
        deliver_due_capsules,
        trigger=CronTrigger(hour=0, minute=1),
        id='capsule_delivery',
        name='Daily Capsule Delivery',
        misfire_grace_time=3600
    )

    _scheduler.start()
    logger.info("Scheduler started — Sentry is on duty (runs daily at 00:01).")
    return _scheduler

def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.info("Scheduler stopped.")