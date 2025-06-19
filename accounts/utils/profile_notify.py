from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.models.notification import Notification
from accounts.models.user import User


def notify_user_status(user_id, status, message, title=None):
    """
    Notifies a single user with a status message via DB and WebSocket.
    """
    user = User.objects.get(pk=user_id)
    
    # Store in DB
    notification = Notification.objects.create(
        recipient=user,
        title=title or f"Profile {status.capitalize()}",
        message=message,
        status=status
    )

    # Send via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",  # user-specific group
        {
            "type": "user.status",
            "status": status,
            "message": message,
            "notification_id": notification.id,
            "title": notification.title,
            "timestamp": str(notification.timestamp),
        }
    )


def notify_managers_about_profile(user_type, user_email):
    """
    Notifies all managers when a new employee/employer profile is submitted.
    """
    managers = User.objects.filter(role__name='manager')
    message = f"A new {user_type} profile was submitted by {user_email} and needs your approval."
    title = f"{user_type.capitalize()} Profile Submitted"

    for manager in managers:
        notify_user_status(
            user_id=manager.id,
            status='pending_approval',
            message=message,
            title=title
        )
