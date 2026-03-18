from decimal import Decimal

from django.db import models
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils import timezone


class Statistics(models.Model):
    """
    Admin uchun ko'rsatish maqsadida ishlatiladigan virtual model.
    Bazada jadval yaratmaydi, faqat mavjud ma'lumotlar bo'yicha hisob-kitob qiladi.
    """

    date = models.DateField(primary_key=True, verbose_name="Sana")

    class Meta:
        managed = False
        verbose_name = "Statistika"
        verbose_name_plural = "Statistika"

    @classmethod
    def get_statistics(cls, target_date=None):
        """
        Kunlik, oylik va yillik statistikani qaytaradi.
        """
        from account.models import Income, Expense
        from expenses.models import Expenses, FoodItem, RawItem, ExpensePaymentStatus
        from salary.models import Salary, SalaryItem
        from sales.models import SaleItem

        zero = Decimal("0.00")
        today = target_date or timezone.localdate()

        # === KUNLIK ===
        daily_income = (
            Income.objects.filter(date=today).aggregate(
                total=Coalesce(Sum("income_amount"), zero)
            )["total"]
            or zero
        )
        daily_expense = (
            Expense.objects.filter(date=today).aggregate(
                total=Coalesce(Sum("expense_amount"), zero)
            )["total"]
            or zero
        )

        # Zakazlar bo'yicha
        daily_orders_total = (
            SaleItem.objects.filter(sale__date=today).aggregate(
                total=Coalesce(Sum("total"), zero)
            )["total"]
            or zero
        )
        daily_paid_orders_amount = (
            SaleItem.objects.filter(sale__date=today).aggregate(
                total=Coalesce(Sum("buyers_paid"), zero)
            )["total"]
            or zero
        )
        daily_closed_orders_count = (
            SaleItem.objects.filter(sale__date=today, order_status=SaleItem.OrderStatus.CLOSED).count()
        )
        daily_unpaid_orders_count = (
            SaleItem.objects.filter(sale__date=today)
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .count()
        )
        daily_open_orders_count = (
            SaleItem.objects.filter(sale__date=today)
            .exclude(order_status=SaleItem.OrderStatus.CLOSED)
            .count()
        )
        daily_unpaid_orders_amount = (
            SaleItem.objects.filter(sale__date=today)
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(F("total") - Coalesce(F("buyers_paid"), zero)), zero
                )
            )["total"]
            or zero
        )

        # Ish haqi
        daily_salary_expenses = (
            Salary.objects.filter(date=today).aggregate(
                total=Coalesce(Sum("total_earned_salary"), zero)
            )["total"]
            or zero
        )
        daily_unpaid_salary_expenses = (
            SalaryItem.objects.filter(salary__date=today).aggregate(
                total=Coalesce(
                    Sum(
                        Coalesce(F("earned_amount"), zero)
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        # Oziq-ovqat va xom-ashyo xarajatlari (Expenses jadvali bo'yicha)
        daily_food_expenses = (
            FoodItem.objects.filter(expense__date=today).aggregate(
                total=Coalesce(Sum(F("quantity") * F("price")), zero)
            )["total"]
            or zero
        )
        daily_unpaid_food_expenses = (
            FoodItem.objects.filter(
                expense__date=today
            )
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        daily_raw_expenses = (
            RawItem.objects.filter(expense__date=today).aggregate(
                total=Coalesce(Sum(F("quantity") * F("price")), zero)
            )["total"]
            or zero
        )
        daily_unpaid_raw_expenses = (
            RawItem.objects.filter(
                expense__date=today
            )
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        daily_total_expenses = (
            daily_salary_expenses + daily_food_expenses + daily_raw_expenses
        )

        daily_income_balance = daily_income - daily_orders_total
        daily_expense_balance = daily_expense - daily_total_expenses

        # === OYLIK ===
        month = today.month
        year = today.year

        monthly_income = (
            Income.objects.filter(date__year=year, date__month=month).aggregate(
                total=Coalesce(Sum("income_amount"), zero)
            )["total"]
            or zero
        )
        monthly_expense = (
            Expense.objects.filter(date__year=year, date__month=month).aggregate(
                total=Coalesce(Sum("expense_amount"), zero)
            )["total"]
            or zero
        )

        monthly_orders_total = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month
            ).aggregate(total=Coalesce(Sum("total"), zero))["total"]
            or zero
        )
        monthly_paid_orders_amount = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month
            ).aggregate(total=Coalesce(Sum("buyers_paid"), zero))["total"]
            or zero
        )
        monthly_closed_orders_count = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month, order_status=SaleItem.OrderStatus.CLOSED
            ).count()
        )
        monthly_unpaid_orders_count = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month
            )
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .count()
        )
        monthly_open_orders_count = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month
            )
            .exclude(order_status=SaleItem.OrderStatus.CLOSED)
            .count()
        )
        monthly_unpaid_orders_amount = (
            SaleItem.objects.filter(
                sale__date__year=year, sale__date__month=month
            )
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(F("total") - Coalesce(F("buyers_paid"), zero)), zero
                )
            )["total"]
            or zero
        )

        monthly_salary_expenses = (
            Salary.objects.filter(date__year=year, date__month=month).aggregate(
                total=Coalesce(Sum("total_earned_salary"), zero)
            )["total"]
            or zero
        )
        monthly_unpaid_salary_expenses = (
            SalaryItem.objects.filter(
                salary__date__year=year, salary__date__month=month
            ).aggregate(
                total=Coalesce(
                    Sum(
                        Coalesce(F("earned_amount"), zero)
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        monthly_food_expenses = (
            FoodItem.objects.filter(
                expense__date__year=year, expense__date__month=month
            ).aggregate(total=Coalesce(Sum(F("quantity") * F("price")), zero))["total"]
            or zero
        )
        monthly_unpaid_food_expenses = (
            FoodItem.objects.filter(
                expense__date__year=year, expense__date__month=month
            )
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        monthly_raw_expenses = (
            RawItem.objects.filter(
                expense__date__year=year, expense__date__month=month
            ).aggregate(total=Coalesce(Sum(F("quantity") * F("price")), zero))["total"]
            or zero
        )
        monthly_unpaid_raw_expenses = (
            RawItem.objects.filter(
                expense__date__year=year, expense__date__month=month
            )
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        monthly_total_expenses = (
            monthly_salary_expenses + monthly_food_expenses + monthly_raw_expenses
        )

        monthly_income_balance = monthly_income - monthly_orders_total
        monthly_expense_balance = monthly_expense - monthly_total_expenses

        # === YILLIK ===
        yearly_income = (
            Income.objects.filter(date__year=year).aggregate(
                total=Coalesce(Sum("income_amount"), zero)
            )["total"]
            or zero
        )
        yearly_expense = (
            Expense.objects.filter(date__year=year).aggregate(
                total=Coalesce(Sum("expense_amount"), zero)
            )["total"]
            or zero
        )

        yearly_orders_total = (
            SaleItem.objects.filter(sale__date__year=year).aggregate(
                total=Coalesce(Sum("total"), zero)
            )["total"]
            or zero
        )
        yearly_paid_orders_amount = (
            SaleItem.objects.filter(
                sale__date__year=year
            ).aggregate(total=Coalesce(Sum("buyers_paid"), zero))["total"]
            or zero
        )
        yearly_closed_orders_count = (
            SaleItem.objects.filter(
                sale__date__year=year, order_status=SaleItem.OrderStatus.CLOSED
            ).count()
        )
        yearly_unpaid_orders_count = (
            SaleItem.objects.filter(sale__date__year=year)
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .count()
        )
        yearly_open_orders_count = (
            SaleItem.objects.filter(sale__date__year=year)
            .exclude(order_status=SaleItem.OrderStatus.CLOSED)
            .count()
        )
        yearly_unpaid_orders_amount = (
            SaleItem.objects.filter(sale__date__year=year)
            .exclude(payment_status=SaleItem.PaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(F("total") - Coalesce(F("buyers_paid"), zero)), zero
                )
            )["total"]
            or zero
        )

        yearly_salary_expenses = (
            Salary.objects.filter(date__year=year).aggregate(
                total=Coalesce(Sum("total_earned_salary"), zero)
            )["total"]
            or zero
        )
        yearly_unpaid_salary_expenses = (
            SalaryItem.objects.filter(salary__date__year=year).aggregate(
                total=Coalesce(
                    Sum(
                        Coalesce(F("earned_amount"), zero)
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        yearly_food_expenses = (
            FoodItem.objects.filter(expense__date__year=year).aggregate(
                total=Coalesce(Sum(F("quantity") * F("price")), zero)
            )["total"]
            or zero
        )
        yearly_unpaid_food_expenses = (
            FoodItem.objects.filter(expense__date__year=year)
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        yearly_raw_expenses = (
            RawItem.objects.filter(expense__date__year=year).aggregate(
                total=Coalesce(Sum(F("quantity") * F("price")), zero)
            )["total"]
            or zero
        )
        yearly_unpaid_raw_expenses = (
            RawItem.objects.filter(expense__date__year=year)
            .exclude(payment_status=ExpensePaymentStatus.PAID)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("price")
                        - Coalesce(F("paid_amount"), zero)
                    ),
                    zero,
                )
            )["total"]
            or zero
        )

        yearly_total_expenses = (
            yearly_salary_expenses + yearly_food_expenses + yearly_raw_expenses
        )

        yearly_income_balance = yearly_income - yearly_orders_total
        yearly_expense_balance = yearly_expense - yearly_total_expenses

        return {
            "date": today,
            "daily": {
                "income": daily_income,
                "orders_total": daily_orders_total,
                "paid_orders_amount": daily_paid_orders_amount,
                "closed_orders_count": daily_closed_orders_count,
                "unpaid_orders_count": daily_unpaid_orders_count,
                "unpaid_orders_amount": daily_unpaid_orders_amount,
                "open_orders_count": daily_open_orders_count,
                "expense": daily_expense,
                "total_expenses": daily_total_expenses,
                "income_balance": daily_income_balance,
                "expense_balance": daily_expense_balance,
                "salary_expenses": daily_salary_expenses,
                "unpaid_salary_expenses": daily_unpaid_salary_expenses,
                "food_expenses": daily_food_expenses,
                "unpaid_food_expenses": daily_unpaid_food_expenses,
                "raw_expenses": daily_raw_expenses,
                "unpaid_raw_expenses": daily_unpaid_raw_expenses,
            },
            "monthly": {
                "year": year,
                "month": month,
                "income": monthly_income,
                "orders_total": monthly_orders_total,
                "paid_orders_amount": monthly_paid_orders_amount,
                "closed_orders_count": monthly_closed_orders_count,
                "unpaid_orders_count": monthly_unpaid_orders_count,
                "unpaid_orders_amount": monthly_unpaid_orders_amount,
                "open_orders_count": monthly_open_orders_count,
                "expense": monthly_expense,
                "total_expenses": monthly_total_expenses,
                "income_balance": monthly_income_balance,
                "expense_balance": monthly_expense_balance,
                "salary_expenses": monthly_salary_expenses,
                "unpaid_salary_expenses": monthly_unpaid_salary_expenses,
                "food_expenses": monthly_food_expenses,
                "unpaid_food_expenses": monthly_unpaid_food_expenses,
                "raw_expenses": monthly_raw_expenses,
                "unpaid_raw_expenses": monthly_unpaid_raw_expenses,
            },
            "yearly": {
                "year": year,
                "income": yearly_income,
                "orders_total": yearly_orders_total,
                "paid_orders_amount": yearly_paid_orders_amount,
                "closed_orders_count": yearly_closed_orders_count,
                "unpaid_orders_count": yearly_unpaid_orders_count,
                "unpaid_orders_amount": yearly_unpaid_orders_amount,
                "open_orders_count": yearly_open_orders_count,
                "expense": yearly_expense,
                "total_expenses": yearly_total_expenses,
                "income_balance": yearly_income_balance,
                "expense_balance": yearly_expense_balance,
                "salary_expenses": yearly_salary_expenses,
                "unpaid_salary_expenses": yearly_unpaid_salary_expenses,
                "food_expenses": yearly_food_expenses,
                "unpaid_food_expenses": yearly_unpaid_food_expenses,
                "raw_expenses": yearly_raw_expenses,
                "unpaid_raw_expenses": yearly_unpaid_raw_expenses,
            },
        }


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
        total_earned_salary = (
            SalaryItem.objects.filter(salary__date=report_date).aggregate(
                total=Coalesce(Sum("earned_amount"), zero)
            )["total"]
            or zero
        )

        total_closed_sales = (
            SaleItem.objects.filter(
                sale__date=report_date,
                order_status=SaleItem.OrderStatus.CLOSED,
            ).aggregate(total=Coalesce(Sum("total"), zero))["total"]
            or zero
        )

        total_expenses = (
            Expenses.objects.filter(date=report_date).aggregate(
                total=Coalesce(Sum("total_cost"), zero)
            )["total"]
            or zero
        )

        return {
            "total_earned_salary": total_earned_salary,
            "total_closed_sales": total_closed_sales,
            "total_expenses": total_expenses,
            "balance": total_closed_sales - total_earned_salary - total_expenses,
        }

    @classmethod
    def sync_for_date(cls, report_date, totals=None):
        current_totals = totals or cls.calculate_totals(report_date)
        report, created = cls.objects.get_or_create(
            date=report_date, defaults=current_totals
        )

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
            for item in SaleItem.objects.filter(
                order_status=SaleItem.OrderStatus.CLOSED
            )
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
