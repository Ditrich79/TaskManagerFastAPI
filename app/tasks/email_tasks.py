import smtplib
from email.message import EmailMessage
from app.tasks.worker import celery_app

# Настройки SMTP (можно вынести в config)
SMTP_HOST = "localhost"
SMTP_PORT = 1025
FROM_EMAIL = "noreply@taskmanager.local"

@celery_app.task(name="send_email")
def send_email(to_email: str, subject: str, body: str):
    """Отправляет email через MailHog (или реальный SMTP)."""
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        # server.starttls()  # не нужен для MailHog
        # server.login(user, password)  # не нужен для MailHog
        server.send_message(msg)
    return {"status": "ok", "to": to_email}