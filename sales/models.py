from django.conf import settings
from django.db import models
import uuid


class Buyer(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255, verbose_name="Ismi")
	sign = models.CharField(max_length=255, blank=True, verbose_name="Belgisi")
	phone_number = models.CharField(max_length=50, blank=True, verbose_name="Telefon raqami")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "Xaridor "
		verbose_name_plural = "Xaridorlar "
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} - {self.sign}"


class Product(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	product_name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
	measurement_unit = models.CharField(max_length=64, blank=True, verbose_name="O'lchov birligi")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "Mahsulot "
		verbose_name_plural = "Mahsulotlar "
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.product_name} ({self.measurement_unit})"


class Sale(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yaratgan foydalanuvchi")
	date = models.DateField(unique=True, verbose_name="Sana")
	description = models.TextField(blank=True, verbose_name="Tavsif")
	total_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Jami narx")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Sale - {self.date}"

	def save(self, *args, **kwargs):
		# Just save the Sale instance without automatic total calculation
		# Total calculation will be handled by SaleAdmin.save_formset
		super().save(*args, **kwargs)

	class Meta:
		verbose_name = "Zakaz "
		verbose_name_plural = "Zakazlar "
		ordering = ["-created_at"]


class SaleItem(models.Model):
	class PaymentStatus(models.TextChoices):
		UNPAID = 'unpaid', "Yo'q"
		PARTIAL = 'partial', "Qisman"
		PAID = 'paid', "Ha"

	class OrderStatus(models.TextChoices):
		OPEN = 'open', "Yo'q"
		CLOSED = 'closed', "Ha"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="sotuvlar", verbose_name="Savdo")
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sale_items", verbose_name="Mahsulot")
	quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Miqdor")
	price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Narx")
	total = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, default=0, verbose_name="Jami")
	buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xaridor")

	payment_status = models.CharField(
    max_length=10,
    choices=PaymentStatus.choices,
    default=PaymentStatus.UNPAID,
    verbose_name="To'lov holati"
		)

	order_status = models.CharField(
    max_length=10,
    choices=OrderStatus.choices,
    default=OrderStatus.OPEN,
    verbose_name="Zakaz yopilganmi"
    )

	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "[ Zakaz elementi ] "
		verbose_name_plural = "[ Zakaz elementlari ] "

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
