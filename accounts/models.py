from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Phone number"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Profile picture"
    )
    worker = models.BooleanField(
        default=False,
        verbose_name="Worker"
    )

    def __str__(self):
        return self.username
