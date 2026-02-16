from django.contrib import admin
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

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
	list_display = ("food_product", "quantity", "price", "total_item_price", "expense", "created_at" )

@admin.register(RawItem)
class RawItemAdmin(admin.ModelAdmin):
	list_display = ("raw_material", "quantity", "price", "total_item_price", "expense", "created_at" )

# --- Inlines: Expenses ichida ko'rinadigan qismlar ---

class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 1  # Bo'sh qatorlar soni
    fields = ('food_product', 'quantity', 'price', 'total_item_price_display')
    readonly_fields = ('total_item_price_display',)

    def total_item_price_display(self, obj):
        return f"{obj.total_item_price:,}" # 1,000,000 ko'rinishida formatlash
    total_item_price_display.short_description = "Total Price"

class RawItemInline(admin.TabularInline):
    model = RawItem
    extra = 1
    fields = ('raw_material', 'quantity', 'price', 'total_item_price_display')
    readonly_fields = ('total_item_price_display',)

    def total_item_price_display(self, obj):
        return f"{obj.total_item_price:,}"
    total_item_price_display.short_description = "Total Price"

# --- Expenses Admin ---

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('date', 'created_by', 'total_cost', 'description', 'created_at')
    # list_filter = ('date', 'created_by')
    # search_fields = ('description',)
    inlines = [FoodItemInline, RawItemInline]

    # total_cost modelda editable=False bo'lgani uchun readonly_fields'ga qo'shish kerak
    readonly_fields = ('total_cost',)
    exclude = ('created_by',)

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