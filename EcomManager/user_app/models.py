from django.contrib.auth.models import AbstractUser
from django.db import models

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

    # Customize how the user is displayed in the admin panel
    def __str__(self):
        return self.email
