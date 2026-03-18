import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0004_alter_fooditem_options_alter_rawitem_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="OtherExpenseTypes",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("expense_type_name", models.CharField(max_length=255, verbose_name="Xarajat turi nomi")),
                ("measurement_unit", models.CharField(blank=True, max_length=64, verbose_name="O'lchov birligi")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")),
            ],
            options={
                "verbose_name": "Boshqa xarajat turi ",
                "verbose_name_plural": "Boshqa xarajat turlari ",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OtherExpenseItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("quantity", models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name="Miqdori")),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name="Narxi")),
                (
                    "payment_status",
                    models.CharField(
                        choices=[("unpaid", "To'lanmagan"), ("partial", "Qisman"), ("paid", "To'langan")],
                        default="unpaid",
                        max_length=10,
                        verbose_name="To'lov holati",
                    ),
                ),
                ("paid_amount", models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name="To'langan summa")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")),
                (
                    "expense",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="other_items",
                        to="expenses.expenses",
                    ),
                ),
                (
                    "expense_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="expenses.otherexpensetypes",
                        verbose_name="Xarajat turi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Boshqa xarajat ",
                "verbose_name_plural": "Boshqa xarajatlar ",
            },
        ),
    ]
