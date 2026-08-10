"""
services/email.py
------------------
Very small wrapper around Python's built-in smtplib.
Called by services/monitoring.py after 3 consecutive failures.

The frontend never sends emails -- only the backend does.
"""

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")


def send_failure_alert(api_name: str, api_url: str, last_http_status, failure_count: int):
    """
    Sends a plain-text email alert. If SMTP isn't configured (e.g. local dev
    without credentials), it just prints to the console instead of crashing
    the background monitor.
    """
    subject = f"🚨 API Alert: {api_name} has failed {failure_count} consecutive checks"
    body = (
        f"🚨 API Alert\n\n"
        f"{api_name} has failed {failure_count} consecutive checks.\n\n"
        f"URL:\n{api_url}\n\n"
        f"Last HTTP Status:\n{last_http_status if last_http_status else 'No response'}\n"
    )

    if not SMTP_USERNAME or not SMTP_PASSWORD or not ALERT_EMAIL_TO:
        print("[email] SMTP not configured, skipping real send. Would have sent:")
        print(body)
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = ALERT_EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, [ALERT_EMAIL_TO], msg.as_string())
        print(f"[email] Alert sent for {api_name}")
    except Exception as e:
        # Monitoring must never crash because of an email failure
        print(f"[email] Failed to send alert: {e}")
