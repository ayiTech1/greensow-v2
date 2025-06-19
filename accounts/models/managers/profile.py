from django.db import models
from django.utils import timezone

class ProfileManager(models.Manager):
    def create_profile(self, user, **kwargs):
        profile = self.model(user=user, **kwargs)
        profile.status = 'pending'
        profile.last_submitted = timezone.now()
        profile.save()
        return profile

    def update_profile(self, instance, **kwargs):
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.status = 'pending'
        instance.last_submitted = timezone.now()
        instance.save()
        return instance

    def delete_profile(self, instance):
        instance.delete()