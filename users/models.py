from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField( _("Телефон"), max_length=20, blank=True, null=True)
    is_worker = models.BooleanField(
        _("Работник"),
        default=False,
        help_text=_("Отметьте, если пользователь является сотрудником."),
        )

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    full_name.short_description = 'Имя и Фамилия'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"