import sqlite3
import datetime
from heap import *
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def login(email=None, password=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.commit()
    conn.close()
    return bool(user)


def generate_otp():
    """Generates a secure 6-digit random code."""
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email, otp_code, name):
    """Sends the OTP code using your verified app password."""
    
    sender_email = os.environ.get("SMTP_EMAIL")
    sender_password = os.environ.get("SMTP_PASSWORD") 
    
    msg = MIMEText(f'''Hi {name},\n
    Your OTP for registration is: {otp_code}\n\nThis code will expire shortly.\n\n
    Regards\n Team Inventrack''')
    msg["Subject"] = "🔐 INVENTRACK Registration OTP"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")
        return False




