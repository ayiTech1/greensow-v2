from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.stores.constants import ROLE_CHOICES
from accounts.models.managers.user import UserManager

class Role(models.Model):
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def primary_role(self):
        return self.role.name if self.role else None

    @property
    def get_username(self):
        return self.username

    @property
    def is_manager(self):
        return self.primary_role and self.primary_role.lower() == 'manager'

    @property
    def is_employer(self):
        return self.primary_role and self.primary_role.lower() == 'employer'

    @property
    def is_employee(self):
        return self.primary_role and self.primary_role.lower() == 'employee'

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
