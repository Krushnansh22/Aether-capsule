import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_NAME = 'Aether Capsule'

def send_capsule_email(capsule: dict) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASS env vars.")
        return False

    recipient = capsule['email']
    message_text = capsule['message']
    file_path = capsule.get('file_path')
    created_at = capsule.get('created_at', 'one year ago')

    try:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(created_at)
            friendly_date = dt.strftime('%B %d, %Y')
        except Exception:
            friendly_date = 'one year ago'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = '✉️ A Message From Your Past Self — Aether Capsule'
        msg['From'] = f'{FROM_NAME} <{SMTP_USER}>'
        msg['To'] = recipient

        plain = (
            f"Hello,\n\n"
            f"One year ago, on {friendly_date}, you sealed a message to yourself.\n"
            f"It has traveled through time — and it is now ready for you.\n\n"
            f"--- YOUR MESSAGE ---\n\n{message_text}\n\n"
            f"--- END OF MESSAGE ---\n\n"
            f"With warmth,\nAether Capsule\n"
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Montserrat:wght@400;500;600&display=swap');
  body {{ margin:0; padding:0; background:#0a0a0a; font-family:'Cormorant Garamond', serif; color:#F3EFE6; }}
  .wrap {{ max-width:620px; margin:40px auto; background:#161616; border:1px solid #2a2a2a; border-radius:2px; overflow:hidden; box-shadow: 0 16px 32px rgba(0,0,0,0.5); }}
  .header {{ background:#0d0d0d; padding:56px 40px 48px; text-align:center; border-bottom:1px solid #2a2a2a; }}
  .sigil {{ font-size:42px; margin-bottom:20px; color:#C2A271; }}
  .title {{ font-size:11px; letter-spacing:0.3em; color:#C2A271; font-family:'Montserrat', sans-serif; text-transform:uppercase; margin-bottom:16px; font-weight:500; }}
  .headline {{ font-size:32px; font-weight:300; color:#F3EFE6; line-height:1.25; font-style:italic; }}
  .body {{ padding:48px 48px; }}
  .meta {{ font-size:10px; font-family:'Montserrat', sans-serif; color:#a39e93; letter-spacing:0.2em; text-transform:uppercase; margin-bottom:24px; font-weight:600; border-bottom:1px solid #2a2a2a; padding-bottom:16px; }}
  .message-box {{ background:#0a0a0a; border-left:3px solid #8B2627; padding:32px; margin:32px 0; font-size:19px; line-height:1.7; color:#F3EFE6; font-style:italic; white-space:pre-wrap; }}
  .footer-note {{ font-size:16px; color:#a39e93; line-height:1.6; text-align:center; padding:0 24px; }}
  .footer {{ padding:32px 40px; border-top:1px solid #2a2a2a; background:#0d0d0d; text-align:center; font-size:10px; font-family:'Montserrat', sans-serif; color:#555555; letter-spacing:0.2em; text-transform:uppercase; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="sigil">⟁</div>
    <div class="title">Aether Capsule · Time Delivered</div>
    <div class="headline">A letter from your past self,<br>sealed on {friendly_date}</div>
  </div>
  <div class="body">
    <div class="meta">Your Message · Unsealed After 365 Days</div>
    <div class="message-box">{message_text}</div>
    <p class="footer-note">
      This message was written by you, for you — sent forward through time. 
      We hope you find it exactly as meaningful as the moment it was sealed.
    </p>
  </div>
  <div class="footer">Aether Capsule · Memories Across Time · {friendly_date}</div>
</div>
</body>
</html>"""

        msg.attach(MIMEText(plain, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            parts = filename.split('_', 3)
            display_name = parts[-1] if len(parts) == 4 else filename

            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{display_name}"')
            msg.attach(part)
            logger.info(f"Attached file: {file_path}")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, recipient, msg.as_string())

        logger.info(f"Capsule email sent to {recipient}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}", exc_info=True)
        return False