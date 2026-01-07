from django.contrib import admin
from .models import Employee, DailyWork

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'base_salary')

@admin.register(DailyWork)
class DailyWorkAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours_worked', 'earned_amount')
    list_filter = ('date', 'employee')
