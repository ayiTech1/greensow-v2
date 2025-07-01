from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def blacklist_refresh_token(refresh_token_str):
    """
    Blacklist the given refresh token.
    """
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
        return {"success": True, "detail": "Successfully blacklisted."}, status.HTTP_200_OK
    except TokenError as e:
        return {"success": False, "detail": str(e)}, status.HTTP_400_BAD_REQUEST
