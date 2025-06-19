from rest_framework.response import Response
from rest_framework import status

def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def error_response(message, status_code=400):
    return Response({
        "success": False,
        "message": message,
        "data": None
    }, status=status_code)