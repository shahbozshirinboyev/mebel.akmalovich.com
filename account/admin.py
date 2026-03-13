from django.contrib import admin
from django.db import models as dj_models
from django.forms import TextInput, Textarea
from import_export.admin import ExportMixin

from .models import Expense, Income


class RecordAdmin(admin.ModelAdmin):
    # list_filter = ("date", "payment_type")
    exclude = ("created_by",)
    readonly_fields = ("created_by",)
    formfield_overrides = {
        dj_models.DecimalField: {"widget": TextInput(attrs={"class": "thousand-sep"})},
        dj_models.TextField: {"widget": Textarea(attrs={"cols": 100, "rows": 4})},
    }

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj:
            return [*fields, "created_by"]
        return fields

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        js = ("expenses/js/decimal_thousands.js",)


@admin.register(Income)
class IncomeAdmin(ExportMixin, RecordAdmin):
    list_display = ("date", "income_amount", "payment_type", "description", "created_by", "created_at")
    fields = ("date", "income_amount", "payment_type", "description")


@admin.register(Expense)
class ExpenseAdmin(ExportMixin, RecordAdmin):
    list_display = ("date", "expense_amount", "payment_type", "description", "created_by", "created_at")
    fields = ("date", "expense_amount", "payment_type", "description")
