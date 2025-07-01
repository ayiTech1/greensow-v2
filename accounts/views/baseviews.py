import logging
from rest_framework import viewsets, status
from core.response import success_response, error_response

logger = logging.getLogger(__name__)

class BaseViewSet(viewsets.ViewSet):
    def handle_success(self, message: str, data=None, status_code=status.HTTP_200_OK):
        return success_response(message=message, data=data, status_code=status_code)

    def handle_error(self, message: str, status_code=status.HTTP_400_BAD_REQUEST, errors=None, exc=None):
        if exc:
            logger.exception(f"{message} | Exception: {str(exc)}")
        else:
            logger.error(f"{message}")
        return error_response(message=message, errors=errors or {}, status_code=status_code)