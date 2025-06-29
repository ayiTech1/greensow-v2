
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    # Call DRF’s default handler first to get standard response.
    response = exception_handler(exc, context)

    # Example for expired/invalid token (SimpleJWT style)
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        custom_response_data = {
            "success": False,
            "message": "Authentication failed. " + str(exc.detail),
            "code": "GS401",
            "errors": {
                "detail": str(exc.detail),
                "code": getattr(exc, 'default_code', 'not_authenticated')
            }
        }
        return Response(custom_response_data, status=status.HTTP_401_UNAUTHORIZED)

    # If DRF made a standard response, wrap it too:
    if response is not None:
        response.data = {
            "success": False,
            "message": "Validation failed." if response.status_code == 400 else "An error occurred.",
            "code": f"GS{response.status_code}",
            "errors": response.data
        }

    return response
