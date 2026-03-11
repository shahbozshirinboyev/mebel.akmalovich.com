from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import path
from django.forms import TextInput, Textarea
from django.db import models as dj_models
from import_export.admin import ExportMixin
from .models import Employee, Salary, SalaryItem

User = get_user_model()


class SalaryItemInline(admin.TabularInline):
	model = SalaryItem
	extra = 0
	fields = ('employee', 'earned_amount', 'earned_note', 'paid_amount', 'paid_note')
	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}


class SalaryItemYearFilter(admin.SimpleListFilter):
	title = "Yil"
	parameter_name = "year"

	def lookups(self, request, model_admin):
		return [(str(year), str(year)) for year in range(2020, 2027)]

	def queryset(self, request, queryset):
		value = self.value()
		if not value:
			return queryset
		try:
			return queryset.filter(salary__date__year=int(value))
		except (TypeError, ValueError):
			return queryset


class SalaryItemMonthFilter(admin.SimpleListFilter):
	title = "Oy"
	parameter_name = "month"

	def lookups(self, request, model_admin):
		return (
			("1", "Yanvar"),
			("2", "Fevral"),
			("3", "Mart"),
			("4", "Aprel"),
			("5", "May"),
			("6", "Iyun"),
			("7", "Iyul"),
			("8", "Avgust"),
			("9", "Sentabr"),
			("10", "Oktabr"),
			("11", "Noyabr"),
			("12", "Dekabr"),
		)

	def queryset(self, request, queryset):
		value = self.value()
		if not value:
			return queryset
		try:
			return queryset.filter(salary__date__month=int(value))
		except (TypeError, ValueError):
			return queryset


@admin.register(Employee)
class EmployeeAdmin(ExportMixin, admin.ModelAdmin):
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
class SalaryItemAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ("salary", "employee", "earned_amount", "earned_note", "paid_amount", "paid_note", "created_at")
	list_filter = ("employee", SalaryItemYearFilter, SalaryItemMonthFilter)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	class Media:
		js = ('salary/js/calculate_salary_total.js', 'salary/js/decimal_thousands.js',)


@admin.register(Salary)
class SalaryAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ("date", "created_by", "total_earned_salary", "total_paid_salary", "created_at")
	inlines = [SalaryItemInline]
	exclude = ("created_by",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		deleted_instances = formset.deleted_objects
		
		# O'chirilgan itemlarni saqlash
		for obj in deleted_instances:
			obj.delete()
		
		# Yangi va o'zgartirilgan itemlarni saqlash
		for instance in instances:
			if hasattr(instance, 'salary') and instance.salary:
				instance.save()
		
		# Saqlangandan keyin total larni qayta hisoblash
		if form.instance and hasattr(form.instance, 'salary_items'):
			total_earned = sum(item.earned_amount or 0 for item in form.instance.salary_items.all())
			total_paid = sum(item.paid_amount or 0 for item in form.instance.salary_items.all())
			form.instance.total_earned_salary = total_earned
			form.instance.total_paid_salary = total_paid
			form.instance.save(update_fields=['total_earned_salary', 'total_paid_salary'])
		
		formset.save_m2m()

	def save_model(self, request, obj, form, change):
		if not obj.pk:  # Only set created_by on creation
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

	class Media:
		js = ('salary/js/calculate_salary_total.js', 'salary/js/decimal_thousands.js',)
