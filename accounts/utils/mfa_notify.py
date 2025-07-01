import pyotp
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from twilio.rest import Client
import logging
from accounts.stores.constants import OTP_ACCOUNT_VERIFICATION, OTP_PASSWORD_RESET
from accounts.models import User, OneTimePassword

logger = logging.getLogger(__name__)

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

def generate_otp(length=6):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, digits=length, interval=300)
    return totp.now()

@shared_task
def send_code_to_user_email(contact, purpose=OTP_ACCOUNT_VERIFICATION):
    try:
        otp_code = generate_otp()
        user = User.objects.get(email=contact)
        app_name = 'greensnow'
        if purpose == OTP_ACCOUNT_VERIFICATION:
            subject = "Verify your email"
            message = (f"Hi {user.username}, thanks for signing up on {app_name}. " f"Please enter the code {otp_code} to verify your account. It expires in 5 minutes.")
        elif purpose == OTP_PASSWORD_RESET:
            subject = "Reset your password"
            message = (f"Hi {user.username}, you requested to reset your password on {app_name}. " f"Use this code: {otp_code} to continue. It expires in 5 minutes.")
        expires_at = timezone.now() + timedelta(minutes=5)
        OneTimePassword.objects.update_or_create(user=user, purpose=purpose, defaults={'code': otp_code, 'expires_at': expires_at})
        send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[contact])
    except Exception as e:
        logging.exception("Error sending OTP email")
        return f"Error: {str(e)}"


@shared_task
def send_code_to_user_phone(phone_number, purpose=OTP_ACCOUNT_VERIFICATION):
    try:
        otp_code = generate_otp()
        user = User.objects.get(phone_number=phone_number)
        app_name = 'greensnow'
        if purpose == OTP_ACCOUNT_VERIFICATION:
            message = (f"Hi {user.username}, thanks for signing up on {app_name}. " f"Your OTP for account verification is {otp_code}. It expires in 5 minutes.")
        elif purpose == OTP_PASSWORD_RESET:
            message = (f"Hi {user.username}, you requested a password reset on {app_name}. " f"Your OTP is {otp_code}. It expires in 5 minutes.")
        expires_at = timezone.now() + timedelta(minutes=5)
        OneTimePassword.objects.update_or_create(user=user, purpose=purpose, defaults={'code': otp_code, 'expires_at': expires_at})
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=phone_number)
    except Exception as e:
        logging.exception("Error sending OTP SMS")
        return f"Error: {str(e)}"


def notify_user(subject, message, recipient_email):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
