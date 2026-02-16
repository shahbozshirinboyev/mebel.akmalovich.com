from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
import uuid

# FoodProducts va RawMaterials alohida qolmoqda
class FoodProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    food_product_name = models.CharField(max_length=255)
    measurement_unit = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Food Product"
        verbose_name_plural = "Food Products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.food_product_name} ({self.measurement_unit})"

class RawMaterials(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_material_name = models.CharField(max_length=255)
    measurement_unit = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raw Material"
        verbose_name_plural = "Raw Materials"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.raw_material_name} ({self.measurement_unit})"

class Expenses(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(unique=True)

    # ManyToMany olib tashlandi, chunki bog'liqlik
    # FoodItem va RawItem modellaridagi ForeignKey orqali boshqariladi.

    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.date and Expenses.objects.filter(date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError({'date': 'Bu sana uchun xarajat allaqachon yaratilgan.'})

    def update_total_cost(self):
        """
        Xarajatning umumiy summasini FoodItem va RawItem'lar asosida hisoblaydi.
        """
        food_sum = sum(item.total_item_price for item in self.food_items.all())
        raw_sum = sum(item.total_item_price for item in self.raw_items.all())
        self.total_cost = food_sum + raw_sum
        self.save()

    def __str__(self):
        return f"Expense - {self.date}"

class FoodItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="food_items")
    food_product = models.ForeignKey(FoodProducts, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0) # Narx majburiy bo'lgani ma'qul
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"

    @property
    def total_item_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.food_product.food_product_name} - {self.quantity}"

class RawItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name="raw_items")
    raw_material = models.ForeignKey(RawMaterials, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raw Item"
        verbose_name_plural = "Raw Items"

    @property
    def total_item_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.raw_material.raw_material_name} - {self.quantity}"