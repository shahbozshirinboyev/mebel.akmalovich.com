from django.conf import settings
from django.db import models
import uuid


class Employee(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee", verbose_name="Имя пользователя")
	full_name = models.CharField(max_length=255, verbose_name="Имя и Фамилия")
	phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
	position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
	salary_type = models.CharField(max_length=50, blank=True, verbose_name="Тип зарплаты")
	base_salary = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Базовая зарплата")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

	class Meta:
		verbose_name = "Ishchi "
		verbose_name_plural = "Ishchilar "
		ordering = ["created_at"]

	def __str__(self):
		return f"{self.full_name} - {self.position}"


class Salary(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Создал")
	date = models.DateField(unique=True, verbose_name="Дата")
	total_earned_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Общая заработанная зарплата")
	total_paid_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Общая выплаченная зарплата")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

	class Meta:
		verbose_name = "Oylik maosh "
		verbose_name_plural = "Oylik maoshlar "
		ordering = ["-date", "-created_at"]
		unique_together = ("created_by", "date")

	def __str__(self):
		return f"Oylik maosh - {self.date}"

	def save(self, *args, **kwargs):
		# First save the Salary instance
		super().save(*args, **kwargs)

		# Calculate totals from related SalaryItems
		total_earned = self.salary_items.aggregate(
			total=models.Sum('earned_amount')
		)['total'] or 0

		total_paid = self.salary_items.aggregate(
			total=models.Sum('paid_amount')
		)['total'] or 0

		# Update totals if different
		if self.total_earned_salary != total_earned or self.total_paid_salary != total_paid:
			self.total_earned_salary = total_earned
			self.total_paid_salary = total_paid
			super().save(update_fields=['total_earned_salary', 'total_paid_salary'])


class SalaryItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	salary = models.ForeignKey("Salary", on_delete=models.CASCADE, related_name="salary_items", verbose_name="Зарплата")
	employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="salary_items", verbose_name="Работник")
	earned_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Заработанная сумма")
	earned_note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Примечание заработанной суммы")
	paid_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name="Выплаченная сумма")
	paid_note = models.CharField(max_length=255, blank=True, null=True, verbose_name="Примечание выплаченной суммы")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

	class Meta:
		verbose_name = "[ Oylik maosh elementi ] "
		verbose_name_plural = "[ Oylik maosh elementlari ] "
		ordering = ["-salary__date", "created_at"]
		unique_together = ("salary", "employee")

	def __str__(self):
		return f"{self.employee} - {self.salary.date}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		# Update the parent Salary's totals after saving SalaryItem
		if self.salary:
			self.salary.save()
