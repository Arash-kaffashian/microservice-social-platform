from email.message import EmailMessage
from decouple import config
import smtplib

from ..celery_app import celery


""" system celery tasks """


# sender email config
EMAIL = config("EMAIL")
APP_PASSWORD = config("APP_PASSWORD")

# celery task config
@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
# send_verification_email celery task
def send_verification_email(to_email, token):
    verify_link = f"http://localhost:8000/api/settings/verify/{token}"

    # email message config
    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg.set_content(
        f"Click here:\n{verify_link}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
