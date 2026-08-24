import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

# ---- OTP hashing ----
# HMAC-SHA256 with SECRET_KEY as pepper (not plain SHA-256) so the hash
# can't be reproduced without the server's secret, even if the DB leaks.


def hash_otp(otp: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(), otp.encode(), hashlib.sha256
    ).hexdigest()


def verify_otp_hash(otp: str, expected_hash: str) -> bool:
    """Constant-time comparison - avoids timing side-channel attacks."""
    return hmac.compare_digest(hash_otp(otp), expected_hash)


def otp_expiry():
    return timezone.now() + timedelta(minutes=5)


# ---- Resend cooldown ----
# Prevents a user (or a bot) from spamming the send-OTP endpoint every
# request even inside the hourly throttle window. Backed by cache so it
# works correctly across multiple app server processes when Redis is used.

OTP_RESEND_COOLDOWN_SECONDS = 45


def seconds_until_resend_allowed(email: str) -> int:
    key = f"otp_cooldown:{email}"
    ttl = cache.ttl(key) if hasattr(cache, "ttl") else None
    if ttl is None:
        # LocMemCache (dev) has no ttl(); fall back to a simple existence check.
        return OTP_RESEND_COOLDOWN_SECONDS if cache.get(key) else 0
    return max(ttl, 0)


def start_resend_cooldown(email: str):
    cache.set(f"otp_cooldown:{email}", True, timeout=OTP_RESEND_COOLDOWN_SECONDS)


# ---- Email delivery ----
# Sending mail synchronously inside the request/response cycle blocks the
# worker on SMTP latency. At scale this tanks throughput and can time out
# under load. send_otp_email() below hands off to a Celery task so the API
# responds immediately; the task itself does the SMTP call in the background
# with automatic retries on transient failure.


def send_otp_email(email: str, otp: str):
    from .tasks import send_otp_email_task

    send_otp_email_task.delay(email, otp)
