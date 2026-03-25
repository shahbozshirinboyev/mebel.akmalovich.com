from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from expenses.models import (
    ExpensePaymentStatus,
    Expenses,
    FoodItem,
    FoodProducts,
    OtherExpenseItem,
    OtherExpenseTypes,
    RawItem,
    RawMaterials,
)


class ExpenseItemPaymentStatusTests(TestCase):
    def setUp(self):
        self.expense = Expenses.objects.create(date="2026-03-13")
        self.food_product = FoodProducts.objects.create(food_product_name="Non", measurement_unit="kg")
        self.raw_material = RawMaterials.objects.create(raw_material_name="Temir", measurement_unit="kg")
        self.other_expense_type = OtherExpenseTypes.objects.create(
            expense_type_name="Elektr energiya",
            measurement_unit="oy",
        )

    def test_food_item_paid_status_sets_paid_amount_to_total(self):
        item = FoodItem.objects.create(
            expense=self.expense,
            food_product=self.food_product,
            quantity=Decimal("2"),
            price=Decimal("15"),
            payment_status=ExpensePaymentStatus.PAID,
            paid_amount=Decimal("0"),
        )

        self.assertEqual(item.paid_amount, Decimal("30"))

    def test_raw_item_partial_requires_positive_amount_less_than_total(self):
        item = RawItem(
            expense=self.expense,
            raw_material=self.raw_material,
            quantity=Decimal("5"),
            price=Decimal("10"),
            payment_status=ExpensePaymentStatus.PARTIAL,
            paid_amount=Decimal("50"),
        )

        with self.assertRaises(ValidationError):
            item.save()

    def test_other_expense_paid_status_sets_paid_amount_to_total(self):
        item = OtherExpenseItem.objects.create(
            expense=self.expense,
            expense_type=self.other_expense_type,
            quantity=Decimal("1"),
            price=Decimal("120"),
            payment_status=ExpensePaymentStatus.PAID,
            paid_amount=Decimal("0"),
        )

        self.assertEqual(item.paid_amount, Decimal("120"))

    def test_expense_total_cost_includes_other_items(self):
        FoodItem.objects.create(
            expense=self.expense,
            food_product=self.food_product,
            quantity=Decimal("2"),
            price=Decimal("15"),
        )
        RawItem.objects.create(
            expense=self.expense,
            raw_material=self.raw_material,
            quantity=Decimal("3"),
            price=Decimal("10"),
        )
        OtherExpenseItem.objects.create(
            expense=self.expense,
            expense_type=self.other_expense_type,
            quantity=Decimal("1"),
            price=Decimal("50"),
        )

        self.expense.update_total_cost()
        self.expense.refresh_from_db()

        self.assertEqual(self.expense.total_cost, Decimal("110"))


class ExpenseReferenceNameUniquenessTests(TestCase):
    def test_reference_names_must_be_unique_case_insensitive(self):
        cases = [
            (FoodProducts, "food_product_name", " Non ", "non"),
            (RawMaterials, "raw_material_name", " Temir ", "temir"),
            (OtherExpenseTypes, "expense_type_name", " Elektr energiya ", "elektr energiya"),
        ]

        for model_class, field_name, initial_value, duplicate_value in cases:
            with self.subTest(model=model_class.__name__):
                model_class.objects.create(**{field_name: initial_value, "measurement_unit": "kg"})

                duplicate = model_class(
                    **{field_name: duplicate_value, "measurement_unit": "kg"},
                )

                with self.assertRaises(ValidationError):
                    duplicate.save()
