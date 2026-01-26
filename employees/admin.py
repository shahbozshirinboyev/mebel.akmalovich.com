from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from datetime import datetime
from core.admin_mixins import PreserveFiltersAdminMixin, LocalizedAmountAdminMixin, format_amount
from .models import Employee, Balance, MonthBalanceStatistics, YearlyBalanceStatistics
from .forms import EmployeeAdminForm


class YearFilter(admin.SimpleListFilter):
    """Custom year filter from 2020 to current year for models with date field"""
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
    """Custom month filter for all 12 months for models with date field"""
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


class StatisticsYearFilter(admin.SimpleListFilter):
    """Custom year filter for BalanceStatistics model"""
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
        """Filter queryset by selected year for BalanceStatistics"""
        if self.value():
            return queryset.filter(year=self.value())
        return queryset


class StatisticsMonthFilter(admin.SimpleListFilter):
    """Custom month filter for BalanceStatistics model"""
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
        """Filter queryset by selected month for BalanceStatistics"""
        if self.value():
            return queryset.filter(month=self.value())
        return queryset


@admin.register(Employee)
class EmployeeAdmin(LocalizedAmountAdminMixin, PreserveFiltersAdminMixin, admin.ModelAdmin):
    form = EmployeeAdminForm

    list_display = (
        'id',
        'user',
        'full_name',
        'position',
        'salary_type',
        'formatted_base_salary',
        'created_at'
    )

    class Media:
        js = ('admin/js/employee_autofill.js', 'admin/js/format_thousands.js')
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

    def formatted_base_salary(self, obj):
        return format_amount(obj.base_salary)
    formatted_base_salary.short_description = 'Базовая зарплата'


@admin.register(Balance)
class BalanceAdmin(LocalizedAmountAdminMixin, PreserveFiltersAdminMixin, admin.ModelAdmin):
    class Media:
        js = ('admin/js/format_thousands.js',)

    list_display = (
        # 'id',
        'formatted_date',
        'employee',
        'formatted_earned_amount',
        'formatted_paid_amount',
        'description',
        'formatted_net_balance',
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
    # Date hierarchy removed as requested

    def formatted_date(self, obj):
        """Format date as year, month"""
        return obj.date.strftime('%d.%m.%Y')
    formatted_date.short_description = 'Sana'

    def formatted_earned_amount(self, obj):
        return format_amount(obj.earned_amount)
    formatted_earned_amount.short_description = 'Topilgan summa'

    def formatted_paid_amount(self, obj):
        return format_amount(obj.paid_amount)
    formatted_paid_amount.short_description = 'To\'langan summa'

    def formatted_net_balance(self, obj):
        return format_amount(obj.net_balance)
    formatted_net_balance.short_description = 'Qolgan balans'

    def actions_column(self, obj):
        """Display edit icon that links to the change form"""
        if obj.id:  # Only show for existing records
            url = reverse('admin:employees_balance_change', args=[obj.id])
            return format_html(
                '<a href="{}" title="O\'zgartirish">'
                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">'
                '<path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>'
                '<path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/>'
                '</svg>'
                '</a>',
                url
            )
        return ""
    actions_column.short_description = 'Action'
    actions_column.allow_tags = True

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


@admin.register(MonthBalanceStatistics)
class MonthBalanceStatisticsAdmin(LocalizedAmountAdminMixin, PreserveFiltersAdminMixin, admin.ModelAdmin):
    # Faqat ko'rish uchun, qo'lda kiritish mumkin emas
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        'formatted_month',
        'employee',
        'formatted_total_earned',
        'formatted_total_paid',
        'formatted_net_balance'
    )

    def formatted_month(self, obj):
        """Oy nomini chiroyli ko'rsatish"""
        month_names = {
            1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
            5: 'May', 6: 'Iyun', 7: 'Iyul', 8: 'Avgust',
            9: 'Sentabr', 10: 'Oktabr', 11: 'Noyabr', 12: 'Dekabr'
        }
        return month_names.get(obj.month, f'Oy {obj.month}')
    formatted_month.short_description = 'Sana (faqat oy)'

    def formatted_total_earned(self, obj):
        return format_amount(obj.total_earned)
    formatted_total_earned.short_description = 'Jami topilgan'

    def formatted_total_paid(self, obj):
        return format_amount(obj.total_paid)
    formatted_total_paid.short_description = 'Jami to\'langan'

    def formatted_net_balance(self, obj):
        return format_amount(obj.net_balance)
    formatted_net_balance.short_description = 'Oy bo\'yicha qoldig\'i'
    list_filter = (
        StatisticsYearFilter,
        'employee'
    )
    search_fields = (
        'employee__full_name',
        'employee__position'
    )
    readonly_fields = ('net_balance',)

    def changelist_view(self, request, extra_context=None):
        # Call parent changelist_view first
        response = super().changelist_view(request, extra_context)

        # Check if year and employee are selected
        year_filter = request.GET.get('year')
        employee_filter = request.GET.get('employee')

        if year_filter and employee_filter:
            # Get all months for the selected year and employee
            from django.contrib import messages
            from django.db.models import Sum, Q

            # Calculate yearly totals
            yearly_data = MonthBalanceStatistics.objects.filter(
                year=year_filter,
                employee_id=employee_filter
            ).aggregate(
                total_earned=Sum('total_earned'),
                total_paid=Sum('total_paid'),
                total_balance=Sum('net_balance')
            )

            messages.info(
                request,
                f"{year_filter}-yil uchun barcha 12 oy ma'lumotlari. "
                f"Jami topilgan: {format_amount(yearly_data['total_earned'] or 0)}, "
                f"Jami to'langan: {format_amount(yearly_data['total_paid'] or 0)}, "
                f"Jami balans: {format_amount(yearly_data['total_balance'] or 0)}"
            )

        return response

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Check if year and employee are selected
        year_filter = request.GET.get('year')
        employee_filter = request.GET.get('employee')

        if year_filter and employee_filter:
            # Filter by year and employee, show all months
            qs = qs.filter(year=year_filter, employee_id=employee_filter)
            # Order by month to show January to December
            qs = qs.order_by('month')

        return qs

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('employee', 'year', 'month')
        }),
        ('Statistika ma\'lumotlari', {
            'fields': ('total_earned', 'total_paid', 'net_balance')
        }),
    )


@admin.register(YearlyBalanceStatistics)
class YearlyBalanceStatisticsAdmin(LocalizedAmountAdminMixin, PreserveFiltersAdminMixin, admin.ModelAdmin):
    # Faqat ko'rish uchun, qo'lda kiritish mumkin emas
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = (
        'year',
        'employee',
        'formatted_total_earned',
        'formatted_total_paid',
        'formatted_net_balance'
    )
    list_filter = (
        'employee',
    )
    search_fields = (
        'employee__full_name',
        'employee__position'
    )
    readonly_fields = ('total_earned', 'total_paid', 'net_balance')

    def formatted_total_earned(self, obj):
        return format_amount(obj.total_earned)
    formatted_total_earned.short_description = 'Yil bo\'yicha jami topilgan'

    def formatted_total_paid(self, obj):
        return format_amount(obj.total_paid)
    formatted_total_paid.short_description = 'Yil bo\'yicha jami to\'langan'

    def formatted_net_balance(self, obj):
        return format_amount(obj.net_balance)
    formatted_net_balance.short_description = 'Yil bo\'yicha qoldig\'i'

    def changelist_view(self, request, extra_context=None):
        # Call parent changelist_view first
        response = super().changelist_view(request, extra_context)

        return response

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('employee',)
        }),
        ('Statistika ma\'lumotlari', {
            'fields': ('total_earned', 'total_paid', 'net_balance')
        }),
    )
