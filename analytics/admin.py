from django.contrib import admin

from .models import FinancialPerformanceIndicator

from core.admin_mixins import PreserveFiltersAdminMixin





@admin.register(FinancialPerformanceIndicator)

class FinancialPerformanceIndicatorAdmin(PreserveFiltersAdminMixin, admin.ModelAdmin):

    list_display = (

        'id',

        'year',

        'month',

        'get_total_expenses',

        'rent',

        'electricity',

        'salaries'

    )

    list_filter = (

        'year',

        'month'

    )

    readonly_fields = ('total_expenses',)

    fieldsets = (

        ('Davr', {

            'fields': ('year', 'month')

        }),

        ('Xarajatlar', {

            'fields': (

                'rent',

                'electricity',

                'gas',

                'water',

                'salaries',

                'machine_equipment',

                'tools_equipment',

                'staff_food',

                'total_expenses'

            )

        }),

    )



    def get_total_expenses(self, obj):

        return obj.total_expenses

    get_total_expenses.short_description = 'Jami xarajatlar'
