import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_registration_alert(name, user_email ):
    """
    Sends a completely free expiration alert email directly to the supervisor.
    """
    # 1. Setup your sender credentials (using a standard Gmail account)
    sender_email = "noreply.inventrack2026@gmail.com"
    sender_password = "fwrfhdhxrfjfkbsq" # Generated via Google Account security
     
    # 2. Build the structured message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user_email
    message["Subject"] = f"  Registration Successful - INVENTRACK  "
    
    body = (
        f"Hello {name},\n\n"
        f"Registration at the INVENTRACK is successful.\n"
        f"Thankyou for registering and very congratulations for expanding your inventory with INVENTRACK.\n\n"
        f"Regards,\nTeam INVENTRACK"
         
    )
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # 3. Establish a secure connection to Gmail's free SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() # Encrypt the connection
        server.login(sender_email, sender_password)
        
        # 4. Fire the alert
        server.sendmail(sender_email, user_email, message.as_string())
        server.quit()
        print(f"📬 Registration alert successfully routed to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Email notification engine failed: {e}")
        return False

if __name__ == "__main__":
    send_free_expiry_alert()