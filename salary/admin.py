from django.contrib import admin
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import path
from .models import Employee, Salary

User = get_user_model()


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ("full_name", "user", "phone_number", "position", "salary_type", "base_salary")
	search_fields = ()

	class Media:
		js = ("admin/js/user_autofill.js",)

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('get-user-details/<uuid:user_id>/', self.admin_site.admin_view(self.get_user_details), name='employee_get_user_details'),
		]
		return custom_urls + urls

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

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
	list_display = ("employee", "date", "earned_amount", "paid_amount")
	list_filter = ("date",)
	search_fields = ("full_name_position",)
