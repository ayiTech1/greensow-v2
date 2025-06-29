from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.stores.validators import validate_file_size
from accounts.models.user import User
from accounts.managers.profile import ProfileManager

APPROVAL_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('suspended', 'Suspended'),
]


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    last_submitted = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)


    objects = ProfileManager()

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"
    

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    id_card = models.FileField(upload_to='documents/id_cards/', blank=True, null=True,
                               validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']), validate_file_size])
    passport = models.FileField(upload_to='documents/passports/', blank=True, null=True,
                                validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']), validate_file_size])
    profile_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True,
                                      validators=[validate_file_size])
    certificates = models.FileField(upload_to='documents/certificates/', blank=True, null=True,
                                    validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']), validate_file_size])
    status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')
    average_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)
    last_submitted = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileManager()

    def __str__(self):
        return f"Employee Profile for {self.user.email}"