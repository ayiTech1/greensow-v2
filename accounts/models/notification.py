from django.db import models
from accounts.models.user import User

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, default='info')  # e.g., 'approved', 'rejected'
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} for {self.recipient.username}"
