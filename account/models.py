import uuid

from django.conf import settings
from django.db import models


class PaymentType(models.TextChoices):
    CASH = "cash", "Naqd"
    CARD = "card", "Karta"
    TRANSFER = "transfer", "O'tkazma"


class RecordBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tomonidan yaratilgan",
    )
    date = models.DateField(unique=True, verbose_name="Sana")
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        verbose_name="To'lov turi",
    )
    description = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        abstract = True
        ordering = ["-date", "-created_at"]


class Income(RecordBase):
    income_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Kirim miqdori (so'm)",
    )

    class Meta(RecordBase.Meta):
        verbose_name = "Kirim "
        verbose_name_plural = "Kirimlar "

    def __str__(self):
        return f"Kirim - {self.date}"


class Expense(RecordBase):
    expense_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Chiqim miqdori (so'm)",
    )

    class Meta(RecordBase.Meta):
        verbose_name = "Chiqim "
        verbose_name_plural = "Chiqimlar "

    def __str__(self):
        return f"Chiqim - {self.date}"
