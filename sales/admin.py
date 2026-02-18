from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.db import models as dj_models
from .models import Buyer, Product, Sale, SaleItem


class SaleItemInline(admin.TabularInline):
	model = SaleItem
	extra = 0
	fields = ("product", "quantity", "price", "total", "buyer")
	# readonly_fields = ("total",)

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
      list_display = ("date", "created_by", "total_price", "description", "created_at")
      inlines = (SaleItemInline,)
    #   readonly_fields = ("total_price",)

      formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
        dj_models.TextField: {'widget': Textarea(attrs={'cols': 100, 'rows': 5})},
	  }

      class Media:
            js = ('sales/js/calculate_total.js', 'sales/js/decimal_thousands.js',)

      # ADD form ochilganda initial qiymat
      def get_changeform_initial_data(self, request):
          return {"created_by": request.user}

      # Save paytida avtomatik yozish
      def save_model(self, request, obj, form, change):
          if not obj.created_by:
              obj.created_by = request.user
          super().save_model(request, obj, form, change)

      def save_formset(self, request, form, formset, change):
          super().save_formset(request, form, formset, change)
          # Recalculate total_price after saving Sale and all inline items (including deletions)
          obj = form.instance
          total_sum = obj.sotuvlar.aggregate(
              total=models.Sum('total')
          )['total'] or 0
          if obj.total_price != total_sum:
              obj.total_price = total_sum
              obj.save(update_fields=['total_price'])

      # total_price hisoblash
      def total_price(self, obj):
          total = obj.sotuvlar.aggregate(
              sum=models.Sum( models.ExpressionWrapper( models.F("quantity") * models.F("price"), output_field=models.DecimalField() ) ) )["sum"]
          if total is None:
              return "0.00"
          return f"{total:.2f}"

      total_price.short_description = "Umumiy sotuv"
      exclude = ('created_by',)

# ----------------------------------------------------------------------

# @admin.register(SaleItem)
# class SaleItemAdmin(admin.ModelAdmin):
# 	list_display = ("product", "quantity", "price", "total", "buyer", "sale", "created_at" )
# 	# readonly_fields = ("total",)

# 	formfield_overrides = {
# 		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
# 	}

# 	class Media:
# 		js = ('sales/js/calculate_total.js', 'sales/js/decimal_thousands.js',)

# ----------------------------------------------------------------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("product_name", "measurement_unit", "created_at")

	formfield_overrides = {
		dj_models.DecimalField: {'widget': TextInput(attrs={'class': 'thousand-sep'})},
	}

	class Media:
		js = ('sales/js/decimal_thousands.js',)


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
	list_display = ("name", "sign", "phone_number", "created_at")
