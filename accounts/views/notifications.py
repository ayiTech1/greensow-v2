from rest_framework import viewsets
from accounts.models.notification import Notification
from accounts.serializers.notifications import NotificationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import  IsAuthenticated

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-timestamp')

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'detail': 'Marked as read'}, status=status.HTTP_200_OK)
