from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_("Foydalanuvchi nomi"), max_length=150, unique=True)
    first_name = models.CharField(_("Ism"), max_length=150, blank=True)
    last_name = models.CharField(_("Familiya"), max_length=150, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    phone_number = models.CharField(_("Telefon raqami"), max_length=20, blank=True, null=True)
    is_worker = models.BooleanField(_("Ishchi"), default=False, help_text=_("Agar foydalanuvchi ishchi bo'lsa, belgilang."))
    date_joined = models.DateTimeField(_("Ro‘yxatdan o‘tgan sana"), auto_now_add=True)
    
    # Override AbstractUser fields with Uzbek help text
    is_staff = models.BooleanField(
        _("Admin panel"), 
        default=False, 
        help_text=_("Foydalanuvchi admin paneliga kirishi mumkin bo'lsa, belgilang.")
    )
    
    is_active = models.BooleanField(
        _("Faol"), 
        default=True, 
        help_text=_("Agar foydalanuvchi faol bo'lsa, belgilang.")
    )
    
    is_superuser = models.BooleanField(
        _("Super foydalanuvchi  "), 
        default=False, 
        help_text=_("Foydalanuvchining barcha ruxsatlari bor bo'lsa, belgilang.")
    )

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    full_name.short_description = "Ism va familiyasi"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.username}"

    class Meta:
        verbose_name = "Foydalanuvchi "
        verbose_name_plural = "Foydalanuvchilar "