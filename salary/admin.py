from django.contrib import admin
from .models import Employee, Salary


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ("full_name", "user", "phone_number", "position", "base_salary")
	search_fields = ("full_name", "phone_number", "position")

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
	list_display = ("employee", "date", "earned_amount", "paid_amount")
	list_filter = ("date",)
	search_fields = ("full_name_position",)
