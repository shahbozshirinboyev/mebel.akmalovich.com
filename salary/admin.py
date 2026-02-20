from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import path
from django.forms import TextInput, Textarea
from django.db import models as dj_models
from .models import Employee, Salary, SalaryItem

User = get_user_model()


class SalaryItemInline(admin.TabularInline):
	model = SalaryItem
	extra = 1
	fields = ('employee', 'earned_amount', 'earned_note', 'paid_amount', 'paid_note')
	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ("full_name", "user", "phone_number", "position", "salary_type", "base_salary", "created_at")

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	class Media:
		js = ("admin/js/user_autofill.js", "salary/js/decimal_thousands.js",)

	def clean_user(self, form_data):
		"""Validate that user is not already assigned to another employee."""
		cleaned_data = form_data
		if 'user' in cleaned_data:
			user = cleaned_data['user']
			if user and Employee.objects.filter(user=user).exclude(id=self.instance.id if self.instance else None).exists():
				raise admin.ValidationError("Bu foydalanuvchi allaqachon xodim sifatida belgilangan.")
		return cleaned_data

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('get-user-details/<uuid:user_id>/', self.admin_site.admin_view(self.get_user_details), name='employee_get_user_details'),
		]
		return custom_urls + urls

	def save_model(self, request, obj, form, change):
		"""Validate before saving that this user isn't already assigned."""
		if obj.user and Employee.objects.filter(user=obj.user).exclude(id=obj.id).exists():
			from django.core.exceptions import ValidationError
			raise ValidationError("Bu foydalanuvchi allaqachon xodim sifatida belgilangan.")
		super().save_model(request, obj, form, change)

	def get_user_details(self, request, user_id):
		try:
			user = User.objects.get(pk=user_id)
			full_name = f"{user.first_name} {user.last_name}".strip() or user.username
			phone = getattr(user, 'phone_number', '') or ''
			return JsonResponse({
				'full_name': full_name,
				'phone_number': phone
			})
		except User.DoesNotExist:
			return JsonResponse({'error': 'User not found'}, status=404)


@admin.register(SalaryItem)
class SalaryItemAdmin(admin.ModelAdmin):
	list_display = ("salary", "employee", "earned_amount", "paid_amount", "created_at")

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	class Media:
		js = ("salary/js/decimal_thousands.js",)


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
	list_display = ("date", "created_by", "total_earned_salary", "total_paid_salary", "created_at")
	inlines = [SalaryItemInline]
	exclude = ("created_by",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	def save_model(self, request, obj, form, change):
		if not obj.pk:  # Only set created_by on creation
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

	class Media:
		js = ("salary/js/decimal_thousands.js",)
