import smtplib
import time
from email.message import EmailMessage

def send_email(sender, password, to, subject, body):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(sender, password)
                smtp.send_message(msg)
            return  # Success
        except smtplib.SMTPAuthenticationError as e:
            # Permanent error - do not retry
            print(f"\n⚠️ Gmail authentication failed!")
            print("❌ Make sure you're using a Gmail App Password, not your regular password.")
            print("Steps to fix:")
            print("1. Enable 2FA on your Google Account")
            print("2. Go to myaccount.google.com/apppasswords")
            print("3. Generate a 16-character app password")
            print("4. Update EMAIL_PASSWORD in .env with this password")
            print(f"\nError: {e}\n")
            raise e
        except (smtplib.SMTPException, Exception) as e:
            print(f"⚠️ SMTP error on attempt {attempt+1}/{max_attempts}: {e}")
            if attempt < max_attempts - 1:
                wait_time = 5 * (3 ** attempt)
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print("❌ All SMTP sending attempts failed.")
                raise e
