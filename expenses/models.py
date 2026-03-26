from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower, Trim
from django.utils.formats import number_format
import uuid

class UniqueNamedModel(models.Model):
    name_field = None

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.name_field:
            value = getattr(self, self.name_field, "")
            if isinstance(value, str):
                setattr(self, self.name_field, value.strip())

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


# FoodProducts va RawMaterials alohida qolmoqda
class FoodProducts(UniqueNamedModel):
    name_field = "food_product_name"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    food_product_name = models.CharField(max_length=255, verbose_name="Oziq-ovqat nomi")
    measurement_unit = models.CharField(max_length=64, blank=True, verbose_name="O'lchov birligi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Oziq-ovqat "
        verbose_name_plural = "Oziq-ovqatlar "
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("food_product_name")),
                name="expenses_foodproducts_name_unique_ci",
                violation_error_message="Bu oziq-ovqat nomi allaqachon mavjud.",
            ),
        ]

    def __str__(self):
        return f"{self.food_product_name} ({self.measurement_unit})"


class RawMaterials(UniqueNamedModel):
    name_field = "raw_material_name"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_material_name = models.CharField(max_length=255, verbose_name="Xom-ashyo nomi")
    measurement_unit = models.CharField(max_length=64, blank=True, verbose_name="O'lchov birligi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Xom-ashyo "
        verbose_name_plural = "Xom-ashyolar "
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("raw_material_name")),
                name="expenses_rawmaterials_name_unique_ci",
                violation_error_message="Bu xom-ashyo nomi allaqachon mavjud.",
            ),
        ]

    def __str__(self):
        return f"{self.raw_material_name} ({self.measurement_unit})"


class OtherExpenseTypes(UniqueNamedModel):
    name_field = "expense_type_name"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_type_name = models.CharField(max_length=255, verbose_name="Xarajat turi nomi")
    measurement_unit = models.CharField(max_length=64, blank=True, verbose_name="O'lchov birligi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Boshqa xarajat turi "
        verbose_name_plural = "Boshqa xarajat turlari "
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                Lower(Trim("expense_type_name")),
                name="expenses_otherexpensetypes_name_unique_ci",
                violation_error_message="Bu xarajat turi nomi allaqachon mavjud.",
            ),
        ]

    def __str__(self):
        return f"{self.expense_type_name} ({self.measurement_unit})"


class Expenses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yaratgan foydalanuvchi")
    date = models.DateField(unique=True, verbose_name="Sana")
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0, editable=False, verbose_name="Umumiy summa")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    def clean(self):
        if self.date and Expenses.objects.filter(date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError({'date': 'Bu sana uchun xarajat allaqachon yaratilgan.'})

    def update_total_cost(self):
        """
        Xarajatning umumiy summasini barcha itemlar asosida hisoblaydi.
        """
        food_sum = sum(item.total_item_price for item in self.food_items.all())
        raw_sum = sum(item.total_item_price for item in self.raw_items.all())
        other_sum = sum(item.total_item_price for item in self.other_items.all())
        self.total_cost = food_sum + raw_sum + other_sum
        self.save()

    @property
    def food_items_total(self):
        return sum(item.total_item_price for item in self.food_items.all())

    @property
    def raw_items_total(self):
        return sum(item.total_item_price for item in self.raw_items.all())

    @property
    def other_items_total(self):
        return sum(item.total_item_price for item in self.other_items.all())

    class Meta:
        verbose_name = "Xarajat "
        verbose_name_plural = "Xarajatlar "
        ordering = ['date']

    def __str__(self):
        return f"Expense - {self.date}"


class ExpensePaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "To'lanmagan"
    PARTIAL = "partial", "Qisman"
    PAID = "paid", "To'langan"


class FoodItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="food_items")
    food_product = models.ForeignKey(FoodProducts, on_delete=models.CASCADE, verbose_name="Oziq-ovqat nomi")
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Miqdori")
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Narxi") # Narx majburiy bo'lgani ma'qul
    payment_status = models.CharField(
        max_length=10,
        choices=ExpensePaymentStatus.choices,
        default=ExpensePaymentStatus.UNPAID,
        verbose_name="To'lov holati",
    )
    paid_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name="To'langan summa",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Oziq-ovqat xarajati "
        verbose_name_plural = "Oziq-ovqat xarajatlari "

    @property
    def total_item_price(self):
        total = self.quantity * self.price
        return total

    def clean(self):
        total_value = self.total_item_price or 0
        paid_value = self.paid_amount or 0

        if self.payment_status == ExpensePaymentStatus.UNPAID:
            self.paid_amount = 0
        elif self.payment_status == ExpensePaymentStatus.PAID:
            self.paid_amount = total_value
        elif self.payment_status == ExpensePaymentStatus.PARTIAL:
            if paid_value <= 0:
                raise ValidationError({"paid_amount": "Qisman to'lov uchun summa 0 dan katta bo'lishi kerak."})
            if total_value and paid_value >= total_value:
                raise ValidationError({"paid_amount": "Qisman to'lov jami summadan kichik bo'lishi kerak."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_product.food_product_name} - {self.quantity}"


class RawItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="raw_items")
    raw_material = models.ForeignKey(RawMaterials, on_delete=models.CASCADE, verbose_name="Xom-ashyo nomi")
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Miqdori")
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Narxi")
    payment_status = models.CharField(
        max_length=10,
        choices=ExpensePaymentStatus.choices,
        default=ExpensePaymentStatus.UNPAID,
        verbose_name="To'lov holati",
    )
    paid_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name="To'langan summa",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Xom-ashyo xarajati "
        verbose_name_plural = "Xom-ashyo xarajatlari "

    @property
    def total_item_price(self):
        total = self.quantity * self.price
        return total

    def clean(self):
        total_value = self.total_item_price or 0
        paid_value = self.paid_amount or 0

        if self.payment_status == ExpensePaymentStatus.UNPAID:
            self.paid_amount = 0
        elif self.payment_status == ExpensePaymentStatus.PAID:
            self.paid_amount = total_value
        elif self.payment_status == ExpensePaymentStatus.PARTIAL:
            if paid_value <= 0:
                raise ValidationError({"paid_amount": "Qisman to'lov uchun summa 0 dan katta bo'lishi kerak."})
            if total_value and paid_value >= total_value:
                raise ValidationError({"paid_amount": "Qisman to'lov jami summadan kichik bo'lishi kerak."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.raw_material.raw_material_name} - {self.quantity}"


class OtherExpenseItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="other_items")
    expense_type = models.ForeignKey(
        OtherExpenseTypes,
        on_delete=models.CASCADE,
        verbose_name="Xarajat turi",
    )
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Miqdori")
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Narxi")
    payment_status = models.CharField(
        max_length=10,
        choices=ExpensePaymentStatus.choices,
        default=ExpensePaymentStatus.UNPAID,
        verbose_name="To'lov holati",
    )
    paid_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name="To'langan summa",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Boshqa xarajat "
        verbose_name_plural = "Boshqa xarajatlar "

    @property
    def total_item_price(self):
        total = self.quantity * self.price
        return total

    def clean(self):
        total_value = self.total_item_price or 0
        paid_value = self.paid_amount or 0

        if self.payment_status == ExpensePaymentStatus.UNPAID:
            self.paid_amount = 0
        elif self.payment_status == ExpensePaymentStatus.PAID:
            self.paid_amount = total_value
        elif self.payment_status == ExpensePaymentStatus.PARTIAL:
            if paid_value <= 0:
                raise ValidationError({"paid_amount": "Qisman to'lov uchun summa 0 dan katta bo'lishi kerak."})
            if total_value and paid_value >= total_value:
                raise ValidationError({"paid_amount": "Qisman to'lov jami summadan kichik bo'lishi kerak."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.expense_type.expense_type_name} - {self.quantity}"
