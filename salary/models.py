from django.conf import settings
from django.db import models
import uuid


class Employee(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee", verbose_name="Foydalanuvchi")
	full_name = models.CharField(max_length=255, verbose_name="Ismi va Familiyasi")
	phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqami")
	position = models.CharField(max_length=100, blank=True, verbose_name="Lavozimi")
	salary_type = models.CharField(max_length=50, blank=True, verbose_name="Maosh turi")
	base_salary = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Asosiy maosh")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "Ishchi "
		verbose_name_plural = "Ishchilar "
		ordering = ["created_at"]

	def __str__(self):
		return f"{self.full_name} - {self.position}"


class Salary(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kim tomonidan yaratilgan")
	date = models.DateField(unique=True, verbose_name="Sana")
	total_earned_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Kunlik topilgan maosh")
	total_paid_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Kunlik to'langan maosh")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "Ish haqi "
		verbose_name_plural = "Ish haqi "
		ordering = ["-date", "-created_at"]
		unique_together = ("created_by", "date")

	def __str__(self):
		return f"Ish haqi - {self.date}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		total_earned = self.salary_items.aggregate(
			total=models.Sum('earned_amount')
		)['total'] or 0

		total_paid = self.salary_items.aggregate(
			total=models.Sum('paid_amount')
		)['total'] or 0

		if self.total_earned_salary != total_earned or self.total_paid_salary != total_paid:
			self.total_earned_salary = total_earned
			self.total_paid_salary = total_paid
			super().save(update_fields=['total_earned_salary', 'total_paid_salary'])


class SalaryItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	salary = models.ForeignKey("Salary", on_delete=models.CASCADE, related_name="salary_items", verbose_name="Kunlik maosh")
	employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="salary_items", verbose_name="Ishchi")
	earned_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Ishlab topilgan summa")
	earned_note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ishlab topilgan summa uchun izoh")
	paid_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="To'langan summa")
	paid_note = models.CharField(max_length=255, blank=True, null=True, verbose_name="To'langan summa uchun izoh")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

	class Meta:
		verbose_name = "Ishchi ish haqi "
		verbose_name_plural = "Ishchilar ish haqi "
		ordering = ["-salary__date", "created_at"]
		unique_together = ("salary", "employee")

	def __str__(self):
		return f"{self.employee} - {self.salary.date}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		if self.salary:
			self.salary.save()
