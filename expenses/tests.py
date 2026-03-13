from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from expenses.models import (
    ExpensePaymentStatus,
    Expenses,
    FoodItem,
    FoodProducts,
    RawItem,
    RawMaterials,
)


class ExpenseItemPaymentStatusTests(TestCase):
    def setUp(self):
        self.expense = Expenses.objects.create(date="2026-03-13")
        self.food_product = FoodProducts.objects.create(food_product_name="Non", measurement_unit="kg")
        self.raw_material = RawMaterials.objects.create(raw_material_name="Temir", measurement_unit="kg")

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
