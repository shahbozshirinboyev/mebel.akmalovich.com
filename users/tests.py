from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from salary.models import Employee, Salary, SalaryItem


class WorkerDashboardViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="worker",
            password="secret123",
            is_worker=True,
        )
        self.employee = Employee.objects.create(
            user=self.user,
            full_name="Test Worker",
            position="Usta",
            base_salary=Decimal("5000000.00"),
        )

    def test_dashboard_includes_all_month_rows_for_selected_year(self):
        march_salary = Salary.objects.create(date=date(2026, 3, 25))
        april_salary = Salary.objects.create(date=date(2026, 4, 2))
        SalaryItem.objects.create(
            salary=march_salary,
            employee=self.employee,
            earned_amount=Decimal("1400000.00"),
            paid_amount=Decimal("992000.00"),
        )
        SalaryItem.objects.create(
            salary=april_salary,
            employee=self.employee,
            earned_amount=Decimal("700000.00"),
            paid_amount=Decimal("500000.00"),
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("worker_dashboard"),
            {"year": 2026, "month": 3},
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["monthly_rows"]), 12)

        march_row = response.context["monthly_rows"][2]
        april_row = response.context["monthly_rows"][3]
        january_row = response.context["monthly_rows"][0]

        self.assertEqual(march_row["month_name"], "Mart")
        self.assertEqual(march_row["earned"], Decimal("1400000.00"))
        self.assertEqual(march_row["paid"], Decimal("992000.00"))
        self.assertTrue(march_row["is_selected_month"])

        self.assertEqual(april_row["month_name"], "Aprel")
        self.assertEqual(april_row["earned"], Decimal("700000.00"))
        self.assertEqual(april_row["paid"], Decimal("500000.00"))
        self.assertFalse(april_row["is_selected_month"])

        self.assertEqual(january_row["earned"], Decimal("0.00"))
        self.assertEqual(january_row["paid"], Decimal("0.00"))
