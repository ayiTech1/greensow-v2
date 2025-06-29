from django.db import models
from django.utils import timezone
from accounts.models.user import User


PURPOSE_CHOICES = [
        ('account_verification', 'Account Verification'),
        ('password_reset', 'Password Reset'),
    ]


class OneTimePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    failed_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default='account_verification')

    def is_valid(self):
        return timezone.now() < self.expires_at