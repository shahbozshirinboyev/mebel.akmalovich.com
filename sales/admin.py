from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import Buyer, Product, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
	model = SaleItem
	extra = 0
	fields = ("product", "quantity", "price", "buyer")

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
      list_display = ("id", "date", "total_price", "created_at")
      inlines = (SaleItemInline,)
      readonly_fields = ("total_price",)

      # ADD form ochilganda initial qiymat
      def get_changeform_initial_data(self, request):
          return {"created_by": request.user}

      # Save paytida avtomatik yozish
      def save_model(self, request, obj, form, change):
          if not obj.created_by:
              obj.created_by = request.user
          super().save_model(request, obj, form, change)

      # total_price hisoblash
      def total_price(self, obj):
          total = obj.sotuvlar.aggregate(
              sum=models.Sum( models.ExpressionWrapper( models.F("soni") * models.F("narxi"), output_field=models.DecimalField() ) ) )["sum"]
          if total is None:
              return "0.00"
          return f"{total:.2f}"

      total_price.short_description = "Umumiy sotuv"


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
	list_display = ("product", "quantity", "price", "buyer", "created_at", "sale", "id" )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("product_name", "measurement_unit", "created_at", "id")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
	list_display = ("name", "sign", "phone_number", "created_at", "id")
