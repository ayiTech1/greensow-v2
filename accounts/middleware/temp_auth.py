# authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.utils.token_utils import validate_temp_token
from accounts.models import User

class TempTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None
        token = token.replace("Bearer ", "")
        data = validate_temp_token(token, allow_verified=True)
        if not data:
            raise AuthenticationFailed("Invalid or expired temp token.")
        try:
            user = User.objects.get(id=data['user_id'], email=data['email'])
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")
