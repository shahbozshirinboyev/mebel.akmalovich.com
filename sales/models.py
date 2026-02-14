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
		verbose_name = "Buyer"
		verbose_name_plural = "Buyers"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} - {self.sign}"


class Product(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	product_name = models.CharField(max_length=255)
	measurement_unit = models.CharField(max_length=64, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Product"
		verbose_name_plural = "Products"
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.product_name} ({self.measurement_unit})"


class Sale(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	date = models.DateField()
	description = models.TextField(blank=True)
	total_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Sale {self.date}"


class SaleItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="sotuvlar")
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
	quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
	total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
	buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Sale Item"
		verbose_name_plural = "Sale Items"

	def save(self, *args, **kwargs):
		if self.quantity and self.price:
			self.total = self.quantity * self.price
		else:
			self.total = 0
		super().save(*args, **kwargs)

	def __str__(self):
		return self.product.product_name
