from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import status

from accounts.models.profile import EmployerProfile

def update_last_login(user):
    """
    Safely updates the last_login timestamp for the given user.
    """
    if user and user.is_authenticated:
        user.last_login = now()
        user.save(update_fields=['last_login'])


def get_or_empty_response(queryset, serializer_class, empty_message="No data found."):
    count = queryset.count()
    if count == 0:
        return Response({"detail": empty_message, "count": 0}, status=status.HTTP_200_OK)
    
    serializer = serializer_class(queryset, many=True)
    return Response({"count": count, "results": serializer.data}, status=status.HTTP_200_OK)


