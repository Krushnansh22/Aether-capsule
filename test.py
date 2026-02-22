from datetime import datetime, timedelta

from database import get_due_capsules, save_capsule
from mailer import send_capsule_email
cid = save_capsule("vikrantkthakur123@gmail.com", "Hello future me!", None, datetime.now() - timedelta(days=1))
due = get_due_capsules(datetime.now())
for i in due:
    send_capsule_email(i)