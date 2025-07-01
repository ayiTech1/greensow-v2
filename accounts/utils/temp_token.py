
import uuid
from django.core import signing
from django.core.cache import cache
from datetime import timedelta

TEMP_TOKEN_TTL = 600  # 10 minutes

def generate_temp_token(user):
    nonce = str(uuid.uuid4())
    data = {
        "user_id": user.id,
        "email": user.email,
        "nonce": nonce,
    }
    token = signing.dumps(data, salt='mfa-login', compress=True)
    # Track phase as "init" instead of True/False
    cache.set(f"temp_token:{nonce}", "init", timeout=TEMP_TOKEN_TTL)
    return token


def validate_temp_token(token, max_age_minutes=10, allow_verified=False):
    try:
        data = signing.loads(token, salt='mfa-login', max_age=timedelta(minutes=max_age_minutes))
        nonce = data.get("nonce")
        cache_key = f"temp_token:{nonce}"
        phase = cache.get(cache_key)

        if not phase:
            return None  # expired
        if phase == "verified" and not allow_verified:
            return None  # already used for verification

        return data
    except signing.BadSignature:
        return None


def mark_temp_token_verified(token):
    try:
        data = signing.loads(token, salt='mfa-login')
        nonce = data.get("nonce")
        cache_key = f"temp_token:{nonce}"
        cache.set(cache_key, "verified", timeout=5)  # short time before final expiry
    except signing.BadSignature:
        pass
