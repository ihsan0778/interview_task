from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """
    Class for customizing the User Model objects manager class
    """

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('role', 'admin')  # Set the role to 'admin'
        
        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password=None, **other_fields):
        user = self.model(email=email, **other_fields)
        if password:
            user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractUser):
    role_choices = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('end_user', 'End User'),
    )
    role = models.CharField(max_length=20, choices=role_choices, default='end_user')
    activation_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=120, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # Customize how the user is displayed in the admin panel
    def __str__(self):
        return self.email
