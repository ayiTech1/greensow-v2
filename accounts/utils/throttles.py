import logging
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.throttling import AnonRateThrottle
logger = logging.getLogger(__name__)

class OTPThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        identifier = request.data.get('email') or request.data.get('phone_number')
        if identifier:
            identifier = identifier.strip().lower()
            return f"otp-throttle:{identifier}"
        #log fallback usage
        logger.warning("OTPThrottle fallback to IP throttle.")
        return self.get_ident(request)


class SocialLoginThrottle(AnonRateThrottle):
    scope = 'social_login'
