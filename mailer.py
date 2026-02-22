import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FROM_NAME = 'Aether Capsule'


def send_capsule_email(capsule: dict) -> bool:
    """Send a time capsule email to the recipient. Returns True on success."""
    if not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASS env vars.")
        return False

    recipient = capsule['email']
    message_text = capsule['message']
    file_path = capsule.get('file_path')
    created_at = capsule.get('created_at', 'one year ago')

    try:
        # Parse created_at for a human-friendly date
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
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Space+Mono:wght@400&display=swap');
  body {{ margin:0; padding:0; background:#0a0a12; font-family:'Cormorant Garamond',serif; color:#c8c0d8; }}
  .wrap {{ max-width:620px; margin:40px auto; background:#0f0f1a; border:1px solid #2a2040; border-radius:4px; overflow:hidden; }}
  .header {{ background:linear-gradient(135deg,#0d0d22 0%,#1a0a2e 100%); padding:48px 40px 40px; text-align:center; border-bottom:1px solid #2a2040; }}
  .sigil {{ font-size:40px; margin-bottom:16px; }}
  .title {{ font-size:13px; letter-spacing:0.25em; color:#6a5acd; font-family:'Space Mono',monospace; text-transform:uppercase; margin-bottom:12px; }}
  .headline {{ font-size:28px; font-weight:300; color:#e8e0f0; line-height:1.3; font-style:italic; }}
  .body {{ padding:40px; }}
  .meta {{ font-size:12px; font-family:'Space Mono',monospace; color:#4a3f6b; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:24px; }}
  .message-box {{ background:#14102a; border-left:2px solid #6a5acd; border-radius:0 4px 4px 0; padding:28px 32px; margin:24px 0; font-size:17px; line-height:1.8; color:#d0c8e8; font-style:italic; white-space:pre-wrap; }}
  .footer {{ padding:24px 40px; border-top:1px solid #1e1a30; text-align:center; font-size:12px; font-family:'Space Mono',monospace; color:#3a3050; letter-spacing:0.08em; }}
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
    <div class="meta">Your message · Unsealed after 365 days</div>
    <div class="message-box">{message_text}</div>
    <p style="font-size:15px;color:#7a6898;line-height:1.7;">
      This message was written by you, for you — sent forward through time. 
      We hope you find it exactly as meaningful as the moment it was sealed.
    </p>
  </div>
  <div class="footer">aether capsule · memories across time · {friendly_date}</div>
</div>
</body>
</html>"""

        msg.attach(MIMEText(plain, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        # Attach file if present
        if file_path and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            # Strip the timestamp prefix for display
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
