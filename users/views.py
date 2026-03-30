from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from salary.models import SalaryItem


class WorkerLoginView(LoginView):
	template_name = "users/login.html"
	redirect_authenticated_user = False

	def dispatch(self, request, *args, **kwargs):
		# Worker foydalanuvchi authenticated bo'lsa darhol kabinetga yuboramiz.
		# Admin authenticated bo'lsa login sahifasini o'zini ko'rsatamiz.
		if request.user.is_authenticated and getattr(request.user, "is_worker", False):
			return redirect("worker_dashboard")
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		user = form.get_user()
		if not getattr(user, "is_worker", False):
			form.add_error(None, "Siz ishchi emassiz.")
			return self.form_invalid(form)
		return super().form_valid(form)

	def get_success_url(self):
		redirect_to = self.get_redirect_url()
		if redirect_to:
			return redirect_to

		return reverse_lazy("worker_dashboard")


class WorkerDashboardView(LoginRequiredMixin, View):
	login_url = reverse_lazy("login")

	@staticmethod
	def _safe_int(value, default):
		try:
			return int(value)
		except (TypeError, ValueError):
			return default

	def get(self, request):
		if not getattr(request.user, "is_worker", False):
			logout(request)
			return redirect("login")

		today = timezone.localdate()
		current_year = today.year
		selected_year = self._safe_int(request.GET.get("year"), current_year)
		selected_month = self._safe_int(request.GET.get("month"), today.month)

		if selected_year < 2020 or selected_year > 2030:
			selected_year = current_year
		if selected_month < 1 or selected_month > 12:
			selected_month = today.month

		month_names = [
			"Yanvar",
			"Fevral",
			"Mart",
			"Aprel",
			"May",
			"Iyun",
			"Iyul",
			"Avgust",
			"Sentabr",
			"Oktabr",
			"Noyabr",
			"Dekabr",
		]
		years = list(range(2020, 2031))
		months = list(enumerate(month_names, start=1))

		employee = getattr(request.user, "employee", None)
		if employee is None:
			return render(
				request,
				"users/worker_dashboard.html",
				{
					"employee_missing": True,
					"selected_year": selected_year,
					"selected_month": selected_month,
					"selected_month_name": month_names[selected_month - 1],
					"years": years,
					"months": months,
				},
			)

		zero = Decimal("0.00")
		year_items = SalaryItem.objects.filter(
			employee=employee,
			salary__date__year=selected_year,
		)
		month_items = year_items.filter(salary__date__month=selected_month)
		daily_totals = (
			month_items.values("salary__date")
			.annotate(
				total_earned=Coalesce(Sum("earned_amount"), zero),
				total_paid=Coalesce(Sum("paid_amount"), zero),
			)
			.order_by("salary__date")
		)

		totals = month_items.aggregate(
			total_earned=Coalesce(Sum("earned_amount"), zero),
			total_paid=Coalesce(Sum("paid_amount"), zero),
		)
		year_totals = year_items.aggregate(
			total_earned=Coalesce(Sum("earned_amount"), zero),
			total_paid=Coalesce(Sum("paid_amount"), zero),
		)
		year_difference = (year_totals["total_earned"] or zero) - (year_totals["total_paid"] or zero)
		monthly_totals = {
			item["salary__date__month"]: {
				"earned": item["total_earned"] or zero,
				"paid": item["total_paid"] or zero,
			}
			for item in year_items.values("salary__date__month").annotate(
				total_earned=Coalesce(Sum("earned_amount"), zero),
				total_paid=Coalesce(Sum("paid_amount"), zero),
			)
		}
		daily_rows = [
			{
				"date": item["salary__date"],
				"earned": item["total_earned"] or zero,
				"paid": item["total_paid"] or zero,
				"difference": (item["total_earned"] or zero) - (item["total_paid"] or zero),
			}
			for item in daily_totals
		]
		monthly_rows = [
			{
				"month_number": month_number,
				"month_name": month_name,
				"earned": monthly_totals.get(month_number, {}).get("earned", zero),
				"paid": monthly_totals.get(month_number, {}).get("paid", zero),
				"difference": monthly_totals.get(month_number, {}).get("earned", zero)
				- monthly_totals.get(month_number, {}).get("paid", zero),
				"is_selected_month": month_number == selected_month,
			}
			for month_number, month_name in months
		]

		context = {
			"employee": employee,
			"base_salary": employee.base_salary or zero,
			"total_earned": totals["total_earned"] or zero,
			"total_paid": totals["total_paid"] or zero,
			"balance": (employee.base_salary or zero) + (totals["total_earned"] or zero) - (totals["total_paid"] or zero),
			"daily_rows": daily_rows,
			"monthly_rows": monthly_rows,
			"year_total_earned": year_totals["total_earned"] or zero,
			"year_total_paid": year_totals["total_paid"] or zero,
			"year_difference": year_difference or zero,
			"selected_year": selected_year,
			"selected_month": selected_month,
			"selected_month_name": month_names[selected_month - 1],
			"years": years,
			"months": months,
			"employee_missing": False,
		}
		return render(request, "users/worker_dashboard.html", context)


class WorkerLogoutView(View):
	def get(self, request):
		logout(request)
		return redirect("login")

	def post(self, request):
		logout(request)
		return redirect("login")
