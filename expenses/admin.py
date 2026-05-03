from django.contrib import admin
from django import forms
from django.db import models as dj_models
from django.forms import TextInput, Textarea
from django.utils.formats import number_format
from import_export.admin import ExportMixin
from .models import (
    ExpensePaymentStatus,
    FoodProducts,
    RawMaterials,
    OtherExpenseTypes,
    Expenses,
    FoodItem,
    RawItem,
    OtherExpenseItem,
)


class ExpenseItemAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["paid_amount"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("payment_status") != ExpensePaymentStatus.PARTIAL and not cleaned_data.get("paid_amount"):
            cleaned_data["paid_amount"] = 0
        return cleaned_data


class FoodItemAdminForm(ExpenseItemAdminForm):
    class Meta:
        model = FoodItem
        fields = "__all__"


class RawItemAdminForm(ExpenseItemAdminForm):
    class Meta:
        model = RawItem
        fields = "__all__"


class OtherExpenseItemAdminForm(ExpenseItemAdminForm):
    class Meta:
        model = OtherExpenseItem
        fields = "__all__"

# Mahsulotlar va xomashyolarni oddiy ro'yxat sifatida ro'yxatdan o'tkazamiz
@admin.register(FoodProducts)
class FoodProductsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('food_product_name', 'measurement_unit', 'created_at')
    ordering = ('-created_at',)

@admin.register(RawMaterials)
class RawMaterialsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('raw_material_name', 'measurement_unit', 'created_at')
    ordering = ('-created_at',)


@admin.register(OtherExpenseTypes)
class OtherExpenseTypesAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('expense_type_name', 'measurement_unit', 'created_at')
    ordering = ('-created_at',)

# ----------------------------------------------------------------------
class FoodItemYearFilter(admin.SimpleListFilter):
    title = "Yil"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        return [(str(year), str(year)) for year in range(2020, 2031)]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(expense__date__year=int(value))
        except (TypeError, ValueError):
            return queryset


class FoodItemMonthFilter(admin.SimpleListFilter):
    title = "Oy"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        return (
            ("1", "Yanvar"),
            ("2", "Fevral"),
            ("3", "Mart"),
            ("4", "Aprel"),
            ("5", "May"),
            ("6", "Iyun"),
            ("7", "Iyul"),
            ("8", "Avgust"),
            ("9", "Sentabr"),
            ("10", "Oktabr"),
            ("11", "Noyabr"),
            ("12", "Dekabr"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(expense__date__month=int(value))
        except (TypeError, ValueError):
            return queryset


class RawItemYearFilter(admin.SimpleListFilter):
    title = "Yil"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        return [(str(year), str(year)) for year in range(2020, 2031)]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(expense__date__year=int(value))
        except (TypeError, ValueError):
            return queryset


class RawItemMonthFilter(admin.SimpleListFilter):
    title = "Oy"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        return (
            ("1", "Yanvar"),
            ("2", "Fevral"),
            ("3", "Mart"),
            ("4", "Aprel"),
            ("5", "May"),
            ("6", "Iyun"),
            ("7", "Iyul"),
            ("8", "Avgust"),
            ("9", "Sentabr"),
            ("10", "Oktabr"),
            ("11", "Noyabr"),
            ("12", "Dekabr"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(expense__date__month=int(value))
        except (TypeError, ValueError):
            return queryset


@admin.register(FoodItem)
class FoodItemAdmin(ExportMixin, admin.ModelAdmin):
	form = FoodItemAdminForm
	list_display = ("food_product", "quantity", "price", "total_item_price", "payment_status", "paid_amount", "expense", "created_at" )
	list_filter = (FoodItemYearFilter, FoodItemMonthFilter, "payment_status")
	readonly_fields = ("total_item_price",)
	ordering = ("-created_at",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)

		# FoodItem saqlangandan keyin tegishli Expenses ning total_cost ni yangilash
		if obj.expense:
			obj.expense.update_total_cost()

	class Media:
		js = ('expenses/js/calculate_total.js', 'expenses/js/payment_status_toggle.js', 'expenses/js/decimal_thousands.js',)

@admin.register(RawItem)
class RawItemAdmin(ExportMixin, admin.ModelAdmin):
	form = RawItemAdminForm
	list_display = ("raw_material", "quantity", "price", "total_item_price", "payment_status", "paid_amount", "expense", "created_at" )
	list_filter = (RawItemYearFilter, RawItemMonthFilter, "payment_status")
	readonly_fields = ("total_item_price",)
	ordering = ("-created_at",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)

		# RawItem saqlangandan keyin tegishli Expenses ning total_cost ni yangilash
		if obj.expense:
			obj.expense.update_total_cost()

	class Media:
		js = ('expenses/js/calculate_total.js', 'expenses/js/payment_status_toggle.js', 'expenses/js/decimal_thousands.js',)


@admin.register(OtherExpenseItem)
class OtherExpenseItemAdmin(ExportMixin, admin.ModelAdmin):
	form = OtherExpenseItemAdminForm
	list_display = ("expense_type", "quantity", "price", "total_item_price", "payment_status", "paid_amount", "expense", "created_at" )
	list_filter = (FoodItemYearFilter, FoodItemMonthFilter, "payment_status")
	readonly_fields = ("total_item_price",)
	ordering = ("-created_at",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)

		if obj.expense:
			obj.expense.update_total_cost()

	class Media:
		js = ('expenses/js/calculate_total.js', 'expenses/js/payment_status_toggle.js', 'expenses/js/decimal_thousands.js',)

# ----------------------------------------------------------------------
# --- Inlines: Expenses ichida ko'rinadigan qismlar ---

class FoodItemInline(admin.TabularInline):
    form = FoodItemAdminForm
    model = FoodItem
    extra = 0  # Bo'sh qatorlar soni
    fields = ('food_product', 'quantity', 'price', 'total_item_price_display', 'payment_status', 'paid_amount')
    readonly_fields = ('total_item_price_display',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

    def total_item_price_display(self, obj):
        if obj.pk:
            return number_format(obj.total_item_price, decimal_pos=2, use_l10n=True)
        return '<span class="total-item-price-display">0.00</span>'
    total_item_price_display.short_description = "Umumiy narx"
    total_item_price_display.allow_tags = True

class RawItemInline(admin.TabularInline):
    form = RawItemAdminForm
    model = RawItem
    extra = 0
    fields = ('raw_material', 'quantity', 'price', 'total_item_price_display', 'payment_status', 'paid_amount')
    readonly_fields = ('total_item_price_display',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

    def total_item_price_display(self, obj):
        if obj.pk:
            return number_format(obj.total_item_price, decimal_pos=2, use_l10n=True)
        return '<span class="total-item-price-display">0.00</span>'
    total_item_price_display.short_description = "Umumiy narx"
    total_item_price_display.allow_tags = True


class OtherExpenseItemInline(admin.TabularInline):
    form = OtherExpenseItemAdminForm
    model = OtherExpenseItem
    extra = 0
    fields = ('expense_type', 'quantity', 'price', 'total_item_price_display', 'payment_status', 'paid_amount')
    readonly_fields = ('total_item_price_display',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

    def total_item_price_display(self, obj):
        if obj.pk:
            return number_format(obj.total_item_price, decimal_pos=2, use_l10n=True)
        return '<span class="total-item-price-display">0.00</span>'
    total_item_price_display.short_description = "Umumiy narx"
    total_item_price_display.allow_tags = True

# --- Expenses Admin ---

class ExpensesYearFilter(admin.SimpleListFilter):
    title = "Yil"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        return [(str(year), str(year)) for year in range(2020, 2031)]

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(date__year=int(value))
        except (TypeError, ValueError):
            return queryset


class ExpensesMonthFilter(admin.SimpleListFilter):
    title = "Oy"
    parameter_name = "month"

    def lookups(self, request, model_admin):
        return (
            ("1", "Yanvar"),
            ("2", "Fevral"),
            ("3", "Mart"),
            ("4", "Aprel"),
            ("5", "May"),
            ("6", "Iyun"),
            ("7", "Iyul"),
            ("8", "Avgust"),
            ("9", "Sentabr"),
            ("10", "Oktabr"),
            ("11", "Noyabr"),
            ("12", "Dekabr"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            return queryset.filter(date__month=int(value))
        except (TypeError, ValueError):
            return queryset

@admin.register(Expenses)
class ExpensesAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('date', 'total_cost', 'description', 'created_by', 'created_at')
    list_filter = (ExpensesYearFilter, ExpensesMonthFilter)
    # search_fields = ('description',)
    inlines = [FoodItemInline, RawItemInline, OtherExpenseItemInline]
    ordering = ('-date',)

    # total_cost modelda editable=False bo'lgani uchun readonly_fields'ga qo'shish kerak
    readonly_fields = ('food_items_total', 'raw_items_total', 'other_items_total', 'total_cost')
    exclude = ('created_by',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
        dj_models.TextField: {'widget': Textarea(attrs={'cols': 100, 'rows': 5})},
	}

    class Media:
        js = ('expenses/js/calculate_total.js', 'expenses/js/payment_status_toggle.js', 'expenses/js/decimal_thousands.js',)

    def save_formset(self, request, form, formset, change):
        """
        Inline mahsulotlar saqlangandan so'ng Expenses'ning total_cost'ini
        avtomatik qayta hisoblash uchun ushbu metoddan foydalanamiz.
        """
        instances = formset.save(commit=False)
        deleted_instances = formset.deleted_objects

        # O'chirilgan itemlarni saqlash
        for obj in deleted_instances:
            obj.delete()

        # Yangi va o'zgartirilgan itemlarni saqlash
        for instance in instances:
            instance.save()

        formset.save_m2m()

        # Asosiy Expense obyektini yangilash
        form.instance.update_total_cost()
        return instances

    def save_model(self, request, obj, form, change):
        # Yaratuvchini avtomatik joriy foydalanuvchiga sozlash
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
