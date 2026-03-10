from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


class DailyFinanceReport(models.Model):
	date = models.DateField(primary_key=True, verbose_name="Sana")
	total_earned_salary = models.DecimalField(
		max_digits=20,
		decimal_places=2,
		default=Decimal("0.00"),
		verbose_name="Ishchilar ishlab topgan summa",
	)
	total_closed_sales = models.DecimalField(
		max_digits=20,
		decimal_places=2,
		default=Decimal("0.00"),
		verbose_name="Yopilgan zakaz savdosi",
	)
	total_expenses = models.DecimalField(
		max_digits=20,
		decimal_places=2,
		default=Decimal("0.00"),
		verbose_name="Umumiy xarajat",
	)
	balance = models.DecimalField(
		max_digits=20,
		decimal_places=2,
		default=Decimal("0.00"),
		verbose_name="Balans",
	)
	updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

	class Meta:
		verbose_name = "Kunlik moliyaviy hisobot"
		verbose_name_plural = "Kunlik moliyaviy hisobotlar"
		ordering = ["-date"]

	def __str__(self):
		return f"Hisobot - {self.date}"

	@classmethod
	def calculate_totals(cls, report_date):
		from expenses.models import Expenses
		from salary.models import SalaryItem
		from sales.models import SaleItem

		zero = Decimal("0.00")
		total_earned_salary = SalaryItem.objects.filter(salary__date=report_date).aggregate(
			total=Coalesce(Sum("earned_amount"), zero)
		)["total"] or zero

		total_closed_sales = SaleItem.objects.filter(
			sale__date=report_date,
			order_status=SaleItem.OrderStatus.CLOSED,
		).aggregate(
			total=Coalesce(Sum("total"), zero)
		)["total"] or zero

		total_expenses = Expenses.objects.filter(date=report_date).aggregate(
			total=Coalesce(Sum("total_cost"), zero)
		)["total"] or zero

		return {
			"total_earned_salary": total_earned_salary,
			"total_closed_sales": total_closed_sales,
			"total_expenses": total_expenses,
			"balance": total_closed_sales - total_earned_salary - total_expenses,
		}

	@classmethod
	def sync_for_date(cls, report_date, totals=None):
		current_totals = totals or cls.calculate_totals(report_date)
		report, created = cls.objects.get_or_create(date=report_date, defaults=current_totals)

		if created:
			return report

		updated_fields = []
		for field, value in current_totals.items():
			if getattr(report, field) != value:
				setattr(report, field, value)
				updated_fields.append(field)

		if updated_fields:
			updated_fields.append("updated_at")
			report.save(update_fields=updated_fields)

		return report

	@classmethod
	def sync_all(cls):
		from expenses.models import Expenses
		from salary.models import Salary, SalaryItem
		from sales.models import Sale, SaleItem

		zero = Decimal("0.00")

		closed_sales_by_date = {
			item["sale__date"]: item["total"] or zero
			for item in SaleItem.objects.filter(order_status=SaleItem.OrderStatus.CLOSED)
			.values("sale__date")
			.annotate(total=Coalesce(Sum("total"), zero))
		}

		earned_salary_by_date = {
			item["salary__date"]: item["total"] or zero
			for item in SalaryItem.objects.values("salary__date").annotate(
				total=Coalesce(Sum("earned_amount"), zero)
			)
		}

		expenses_by_date = {
			item["date"]: item["total"] or zero
			for item in Expenses.objects.values("date").annotate(
				total=Coalesce(Sum("total_cost"), zero)
			)
		}

		all_dates = set(Sale.objects.values_list("date", flat=True))
		all_dates.update(Salary.objects.values_list("date", flat=True))
		all_dates.update(Expenses.objects.values_list("date", flat=True))

		if not all_dates:
			cls.objects.all().delete()
			return 0

		for report_date in sorted(all_dates):
			totals = {
				"total_earned_salary": earned_salary_by_date.get(report_date, zero),
				"total_closed_sales": closed_sales_by_date.get(report_date, zero),
				"total_expenses": expenses_by_date.get(report_date, zero),
			}
			totals["balance"] = (
				totals["total_closed_sales"]
				- totals["total_earned_salary"]
				- totals["total_expenses"]
			)
			cls.sync_for_date(report_date, totals=totals)

		cls.objects.exclude(date__in=all_dates).delete()
		return len(all_dates)
