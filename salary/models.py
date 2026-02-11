from django.conf import settings
from django.db import models
import uuid


class Employee(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees"
	)
	full_name = models.CharField(max_length=255)
	phone_number = models.CharField(max_length=20, blank=True, null=True)
	position = models.CharField(max_length=100, blank=True)
	salary_type = models.CharField(max_length=50, blank=True)
	base_salary = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]

	def __str__(self):
		return f"{self.full_name}"


class Salary(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	employee = models.ForeignKey(
		"Employee", on_delete=models.CASCADE, related_name="salaries"
	)
	full_name_position = models.CharField(max_length=255, blank=True)
	date = models.DateField()
	earned_amount = models.IntegerField(default=0)
	earned_note = models.TextField(blank=True, null=True)
	paid_amount = models.IntegerField(default=0)
	paid_note = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-date", "-created_at"]

	def __str__(self):
		return f"Salary({self.employee}, {self.date})"
