import smtplib
from email.mime.text import MIMEText
from constants import EMAIL

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body + EMAIL.SIGNATURE)
    msg["Subject"] = subject
    msg["From"] = EMAIL.EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP(EMAIL.SMTP_SERVER, EMAIL.SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL.EMAIL_ADDRESS, EMAIL.EMAIL_PASSWORD)
        server.sendmail(EMAIL.EMAIL_ADDRESS, to_email, msg.as_string())
