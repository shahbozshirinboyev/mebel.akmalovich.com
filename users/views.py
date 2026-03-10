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
		if request.user.is_authenticated and not request.user.is_staff:
			return redirect("worker_dashboard")
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		redirect_to = self.get_redirect_url()
		if redirect_to:
			return redirect_to

		if self.request.user.is_staff:
			return reverse_lazy("admin:index")
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
		if request.user.is_staff and not getattr(request.user, "is_worker", False):
			return redirect("admin:index")

		today = timezone.localdate()
		current_year = today.year
		selected_year = self._safe_int(request.GET.get("year"), current_year)
		selected_month = self._safe_int(request.GET.get("month"), today.month)

		if selected_year < 2020 or selected_year > current_year + 1:
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
		years = list(range(2020, current_year + 1))
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

		month_items = SalaryItem.objects.filter(
			employee=employee,
			salary__date__year=selected_year,
			salary__date__month=selected_month,
		)
		daily_totals = (
			month_items.values("salary__date")
			.annotate(
				total_earned=Coalesce(Sum("earned_amount"), Decimal("0.00")),
				total_paid=Coalesce(Sum("paid_amount"), Decimal("0.00")),
			)
			.order_by("salary__date")
		)

		zero = Decimal("0.00")
		totals = month_items.aggregate(
			total_earned=Coalesce(Sum("earned_amount"), zero),
			total_paid=Coalesce(Sum("paid_amount"), zero),
		)
		daily_rows = [
			{
				"date": item["salary__date"],
				"earned": item["total_earned"] or zero,
				"paid": item["total_paid"] or zero,
			}
			for item in daily_totals
		]

		context = {
			"employee": employee,
			"base_salary": employee.base_salary or zero,
			"total_earned": totals["total_earned"] or zero,
			"total_paid": totals["total_paid"] or zero,
			"daily_rows": daily_rows,
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
