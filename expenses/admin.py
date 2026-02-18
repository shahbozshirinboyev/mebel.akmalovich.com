from django.contrib import admin
from django.db import models as dj_models
from django.forms import TextInput, Textarea
from django.utils.formats import number_format
from .models import FoodProducts, RawMaterials, Expenses, FoodItem, RawItem

# Mahsulotlar va xomashyolarni oddiy ro'yxat sifatida ro'yxatdan o'tkazamiz
@admin.register(FoodProducts)
class FoodProductsAdmin(admin.ModelAdmin):
    list_display = ('food_product_name', 'measurement_unit', 'created_at')
    # search_fields = ('food_product_name',)

@admin.register(RawMaterials)
class RawMaterialsAdmin(admin.ModelAdmin):
    list_display = ('raw_material_name', 'measurement_unit', 'created_at')
    # search_fields = ('raw_material_name',)
    
# ----------------------------------------------------------------------
# @admin.register(FoodItem)
# class FoodItemAdmin(admin.ModelAdmin):
# 	list_display = ("food_product", "quantity", "price", "total_item_price", "expense", "created_at" )
# 	readonly_fields = ("total_item_price",)

# 	formfield_overrides = {
# 		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
# 	}

# 	class Media:
# 		js = ('expenses/js/calculate_total.js', 'expenses/js/decimal_thousands.js',)

# @admin.register(RawItem)
# class RawItemAdmin(admin.ModelAdmin):
# 	list_display = ("raw_material", "quantity", "price", "total_item_price", "expense", "created_at" )
# 	readonly_fields = ("total_item_price",)

# 	formfield_overrides = {
# 		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
# 	}

# 	class Media:
# 		js = ('expenses/js/calculate_total.js', 'expenses/js/decimal_thousands.js',)

# ----------------------------------------------------------------------

# --- Inlines: Expenses ichida ko'rinadigan qismlar ---

class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 0  # Bo'sh qatorlar soni
    fields = ('food_product', 'quantity', 'price', 'total_item_price_display')
    readonly_fields = ('total_item_price_display',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

    def total_item_price_display(self, obj):
        if obj.pk:
            return number_format(obj.total_item_price, decimal_pos=2, use_l10n=True)
        return '<span class="total-item-price-display">0.00</span>'
    total_item_price_display.short_description = "Total Price"
    total_item_price_display.allow_tags = True

class RawItemInline(admin.TabularInline):
    model = RawItem
    extra = 0
    fields = ('raw_material', 'quantity', 'price', 'total_item_price_display')
    readonly_fields = ('total_item_price_display',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

    def total_item_price_display(self, obj):
        if obj.pk:
            return number_format(obj.total_item_price, decimal_pos=2, use_l10n=True)
        return '<span class="total-item-price-display">0.00</span>'
    total_item_price_display.short_description = "Total Price"
    total_item_price_display.allow_tags = True

# --- Expenses Admin ---

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_by', 'total_cost', 'description', 'created_at')
    # list_filter = ('date', 'created_by')
    # search_fields = ('description',)
    inlines = [FoodItemInline, RawItemInline]

    # total_cost modelda editable=False bo'lgani uchun readonly_fields'ga qo'shish kerak
    readonly_fields = ('food_items_total', 'raw_items_total', 'total_cost')
    exclude = ('created_by',)

    formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
        dj_models.TextField: {'widget': Textarea(attrs={'cols': 100, 'rows': 5})},
	}

    class Media:
        js = ('expenses/js/calculate_total.js', 'expenses/js/decimal_thousands.js',)

    def save_formset(self, request, form, formset, change):
        """
        Inline mahsulotlar saqlangandan so'ng Expenses'ning total_cost'ini
        avtomatik qayta hisoblash uchun ushbu metoddan foydalanamiz.
        """
        instances = formset.save()
        # Asosiy Expense obyektini yangilash
        form.instance.update_total_cost()
        return instances

    def save_model(self, request, obj, form, change):
        # Yaratuvchini avtomatik joriy foydalanuvchiga sozlash
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)