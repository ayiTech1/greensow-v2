from rest_framework.response import Response
from rest_framework import status
def success_response(message, data=None, status=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status)

def error_response(errors, status=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": "Validation failed",
        "errors": errors
    }, status=status)
