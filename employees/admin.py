from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Employee, Balance, BalanceStatistics
from .forms import EmployeeAdminForm
from datetime import datetime


class YearFilter(admin.SimpleListFilter):
    """Custom year filter from 2020 to current year"""
    title = _('Yil')
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        """Return list of years from 2020 to current year"""
        current_year = datetime.now().year
        years = []
        for year in range(2020, current_year + 1):
            years.append((str(year), str(year)))
        return years

    def queryset(self, request, queryset):
        """Filter queryset by selected year"""
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


class MonthFilter(admin.SimpleListFilter):
    """Custom month filter for all 12 months"""
    title = _('Oy')
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        """Return list of all 12 months"""
        return [
            ('1', 'Yanvar'),
            ('2', 'Fevral'),
            ('3', 'Mart'),
            ('4', 'Aprel'),
            ('5', 'May'),
            ('6', 'Iyun'),
            ('7', 'Iyul'),
            ('8', 'Avgust'),
            ('9', 'Sentabr'),
            ('10', 'Oktabr'),
            ('11', 'Noyabr'),
            ('12', 'Dekabr'),
        ]

    def queryset(self, request, queryset):
        """Filter queryset by selected month"""
        if self.value():
            return queryset.filter(date__month=self.value())
        return queryset


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm

    list_display = (
        'id',
        'user',
        'full_name',
        'position',
        'salary_type',
        'base_salary',
        'created_at'
    )

    class Media:
        js = ('admin/js/employee_autofill.js',)
    list_filter = (
        'salary_type',
        'position',
        'created_at'
    )
    search_fields = (
        'full_name',
        'position',
        'user__username',
        'user__email'
    )
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'full_name', 'position')
        }),
        ('Информация о зарплате', {
            'fields': ('salary_type', 'base_salary')
        }),
    )


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'formatted_date',
        'employee',
        'earned_amount',
        'paid_amount',
        'description',
        'created_at',
        'actions_column'
    )
    list_filter = (
        YearFilter,
        MonthFilter,
        'employee'
    )
    search_fields = (
        'employee__full_name',
        'employee__position',
        'description'
    )
    readonly_fields = ('created_at', 'net_balance', 'actions_column')
    date_hierarchy = 'date'

    def formatted_date(self, obj):
        """Format date as year, month"""
        return obj.date.strftime('%d.%m.%Y')
    formatted_date.short_description = 'Sana'

    def actions_column(self, obj):
        """Actions column - can be customized with buttons"""
        return "Tugma"
    actions_column.short_description = 'Tugma'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('employee', 'date')
        }),
        ('Summa ma\'lumotlari', {
            'fields': ('earned_amount', 'paid_amount', 'net_balance')
        }),
        ('Qo\'shimcha', {
            'fields': ('description',)
        }),
        ('Vaqt belgilari', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BalanceStatistics)
class BalanceStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'year',
        'month',
        'total_earned',
        'total_paid',
        'net_balance',
        'is_closed'
    )
    list_filter = (
        YearFilter,
        'month',
        'is_closed',
        'employee'
    )
    search_fields = (
        'employee__full_name',
        'employee__position'
    )
    readonly_fields = ('net_balance',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('employee', 'year', 'month')
        }),
        ('Statistika ma\'lumotlari', {
            'fields': ('total_earned', 'total_paid', 'net_balance')
        }),
        ('Holat', {
            'fields': ('is_closed',)
        }),
    )
