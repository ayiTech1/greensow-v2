from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _



class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        # Validate email format
        try:
            EmailValidator()(email)
        except ValidationError:
            raise ValueError(_('Enter a valid email address.'))
        if not password:
            raise ValueError(_('A password must be set'))

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError(_('Password validation error: ') + ', '.join(e.messages))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
   

    def create_manager(self, email, password=None, **extra_fields):
        if not password:
            raise ValidationError(_('A password must be set for manager.'))

        # Force manager role regardless of passed-in role
        
        from accounts.models.user import Role
        role, _ = Role.objects.get_or_create(name='manager')
        extra_fields['role'] = role

        # Force is_staff to be True
        extra_fields['is_superuser'] = True
        extra_fields['is_staff'] = True
        extra_fields['is_active'] = True

        return self.create_user(email, password, **extra_fields)



