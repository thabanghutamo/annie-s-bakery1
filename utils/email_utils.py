"""Email utility functions for sending notifications"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email=None):
    """Send an email using SMTP settings from environment"""
    if not to_email:
        to_email = os.getenv('ADMIN_EMAIL')
    
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_FROM', 'Annie\'s Bakery <noreply@example.com>')
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Skip if SMTP not configured
    if not all([
        os.getenv('SMTP_HOST'),
        os.getenv('SMTP_PORT'),
        os.getenv('SMTP_USER'),
        os.getenv('SMTP_PASSWORD')
    ]):
        print('SMTP not configured, skipping email')
        return False

    try:
        with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT', '587'))) as s:
            s.starttls()
            s.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            s.send_message(msg)
        return True
    except Exception as e:
        print('Email error:', str(e))
        return False