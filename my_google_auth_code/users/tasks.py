from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,  # seconds, retried with backoff below
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def send_otp_email_task(self, email: str, otp: str):
    """Runs on a Celery worker, not in the request/response cycle.
    Retries with backoff on transient SMTP/network failures so a single
    provider hiccup doesn't lose the OTP silently."""
    send_mail(
        subject="Your E-Learning verification code",
        message=f"Your OTP is {otp}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
