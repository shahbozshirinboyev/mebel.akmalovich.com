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
		verbose_name = "Работник"
		verbose_name_plural = "Работники"
		ordering = ["created_at"]

	def __str__(self):
		return f"{self.full_name} - {self.position}"


class Salary(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="salaries")
	date = models.DateField(unique=True)
	total_earned_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0)
	total_paid_salary = models.DecimalField(max_digits=20, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Зарплата"
		verbose_name_plural = "Зарплаты"
		ordering = ["-date", "-created_at"]
		unique_together = ("employee", "date")

	def __str__(self):
		return f"Зарплата - {self.date}"


class SalaryItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	salary = models.ForeignKey("Salary", on_delete=models.CASCADE, related_name="salary_items")
	employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="salary_items")
	earned_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
	earned_note = models.CharField(max_length=255, blank=True, null=True)
	paid_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
	paid_note = models.CharField(max_length=255, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Элемент зарплаты"
		verbose_name_plural = "Элементы зарплаты"
		ordering = ["-salary__date", "created_at"]

	def __str__(self):
		return f"SalaryItem({self.employee}, {self.earned_amount}, {self.paid_amount})"
