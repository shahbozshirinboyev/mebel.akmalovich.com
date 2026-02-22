from django.conf import settings
from django.db import models
import uuid


class Buyer(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	sign = models.CharField(max_length=255, blank=True)
	phone_number = models.CharField(max_length=50, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Xaridor "
		verbose_name_plural = "Xaridorlar "
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} - {self.sign}"


class Product(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	product_name = models.CharField(max_length=255)
	measurement_unit = models.CharField(max_length=64, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Mahsulot "
		verbose_name_plural = "Mahsulotlar "
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.product_name} ({self.measurement_unit})"


class Sale(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	date = models.DateField(unique=True)
	description = models.TextField(blank=True)
	total_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Sale - {self.date}"

	def save(self, *args, **kwargs):
		# Just save the Sale instance without automatic total calculation
		# Total calculation will be handled by SaleAdmin.save_formset
		super().save(*args, **kwargs)

	class Meta:
		verbose_name = "Savdo "
		verbose_name_plural = "Savdolar "
		ordering = ["-created_at"]


class SaleItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="sotuvlar")
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sale_items")
	quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
	price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
	total = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, default=0)
	buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "[ Savdo elementi ] "
		verbose_name_plural = "[ Savdo elementlari ] "

	def save(self, *args, **kwargs):
		if self.quantity and self.price:
			self.total = self.quantity * self.price
		else:
			self.total = 0
		super().save(*args, **kwargs)

		# Don't call self.sale.save() here to avoid conflicts with save_formset
		# The total_price will be updated by the SaleAdmin.save_formset method

	def __str__(self):
		if self.product:
			return self.product.product_name
		return "Mahsulot tanlanmagan"
