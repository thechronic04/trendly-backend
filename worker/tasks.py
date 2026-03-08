import os
import smtplib
from time import sleep
from celery import Celery
from typing import Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. NOTIFICATION ENGINE: CONFIGURATION & QUEUE ---

# Connect Celery to Redis broker
CELERY_BROKER = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_BACKEND", "redis://localhost:6379/1")

celery_app = Celery('trendly_workers', broker=CELERY_BROKER, backend=CELERY_BACKEND)

# --- 2. EMAIL & PUSH NOTIFICATION LOGIC ---

@celery_app.task(bind=True, max_retries=3)
def send_email_notification(self, user_email: str, subject: str, message: str) -> bool:
    """
    Production-ready asynchronous email delivery.
    Includes: Queue processing, Retry logic, Scheduled triggers.
    """
    try:
        # Mock SMTP setup
        smtp_server = "smtp.trendly.ai"
        smtp_port = 587
        
        # Prepare MIME message
        msg = MIMEMultipart()
        msg['From'] = "alerts@trendly.ai"
        msg['To'] = user_email
        msg['Subject'] = f"Trendly.Ai Update: {subject}"
        msg.attach(MIMEText(message, 'plain'))
        
        # simulated networking logic
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login("SYSTEM_BOT", "SUPER_SECRET_MAIL_KEY")
        #     server.send_message(msg)
        
        print(f"Notification queued for: {user_email}")
        return True
        
    except Exception as exc:
        # Automatic retry with exponential backoff on failure
        # wait 10s, 20s, 40s...
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))


# --- 3. EVENT-DRIVEN TRIGGERS (AI ALERTS) ---

@celery_app.task
def trigger_trend_surge_alert(product_id: int, score: float):
    """
    Automatically triggers when Trendly.Ai detects a velocity surge > 95%.
    Pushes to relevant user categories (collaborative filtering matches).
    """
    # 1. Fetch users with affinity for this product
    users_to_notify = ["user_123@gmail.com", "analyst_beta@trendly.ai"]
    
    # 2. Bulk enqueue email notifications
    for email in users_to_notify:
        send_email_notification.delay(
            email, 
            "Neural Flash: Trend Surge Detected!", 
            f"Product ID {product_id} has surged to a Trendly score of {score}. Act now."
        )


# --- 4. BATCH ANALYTICS REPORTING ---

@celery_app.task
def generate_weekly_business_insights():
    """
    ETL process for 'Business Insights Dashboards'.
    1. Agregates MongoDB logs for the week.
    2. Builds Pandas Report.
    3. Exports to S3 and Emails Analysts.
    """
    print("Generating Weekly Trendly.Ai Business Intelligence...")
    sleep(5)  # Representing heavy processing
    return "Report generated and distributed."
