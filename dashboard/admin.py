from django.contrib import admin
from import_export.admin import ExportMixin
from datetime import date
from django.utils import timezone

from .models import DailyFinanceReport, Statistics


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    change_list_template = "admin/dashboard/statistics_change_list.html"
    list_display = ("date",)
    list_display_links = None
    ordering = ("-date",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # Haqiqiy jadval yo'q, shunchaki bo'sh queryset
        return Statistics.objects.none()

    def changelist_view(self, request, extra_context=None):
        today = timezone.localdate()
        valid_tabs = {"daily", "monthly", "yearly"}
        custom_query_params = {
            "daily_date",
            "monthly_year",
            "monthly_month",
            "yearly_year",
            "active_tab",
            "e",
        }
        params = request.GET if request.GET else request.POST

        def _parse_int(value, default):
            if value is None:
                return default
            try:
                if isinstance(value, str):
                    value = value.replace(" ", "").replace("\u00a0", "")
                return int(value)
            except (TypeError, ValueError):
                return default

        def _parse_date(value, default):
            if not value:
                return default
            try:
                return date.fromisoformat(value)
            except (TypeError, ValueError):
                return default

        def _parse_month(value, default):
            parsed_value = _parse_int(value, default)
            if 1 <= parsed_value <= 12:
                return parsed_value
            return default

        def _parse_active_tab(value, default):
            if value in valid_tabs:
                return value
            return default

        daily_date = _parse_date(params.get("daily_date"), today)
        monthly_year = _parse_int(params.get("monthly_year"), today.year)
        monthly_month = _parse_month(params.get("monthly_month"), today.month)
        yearly_year = _parse_int(params.get("yearly_year"), today.year)
        active_tab = _parse_active_tab(params.get("active_tab"), "")

        base_stats = {
            "date": daily_date,
            "daily": Statistics.get_period_statistics(daily_date, period="daily"),
        }

        try:
            monthly_date = date(monthly_year, monthly_month, 1)
        except ValueError:
            monthly_date = date(today.year, today.month, 1)
        monthly_stats = Statistics.get_period_statistics(monthly_date, period="monthly")

        try:
            yearly_date = date(yearly_year, 1, 1)
        except ValueError:
            yearly_date = date(today.year, 1, 1)
        yearly_stats = Statistics.get_period_statistics(yearly_date, period="yearly")

        base_stats["monthly"] = monthly_stats
        base_stats["yearly"] = yearly_stats

        context = extra_context or {}
        context["statistics"] = base_stats
        context["daily_date"] = daily_date
        context["monthly_year"] = monthly_year
        context["monthly_month"] = monthly_month
        context["yearly_year"] = yearly_year
        context["active_tab"] = active_tab
        context["year_choices"] = list(range(2020, 2031))
        context["month_choices"] = [
            (1, "Yanvar"),
            (2, "Fevral"),
            (3, "Mart"),
            (4, "Aprel"),
            (5, "May"),
            (6, "Iyun"),
            (7, "Iyul"),
            (8, "Avgust"),
            (9, "Sentabr"),
            (10, "Oktabr"),
            (11, "Noyabr"),
            (12, "Dekabr"),
        ]
        month_names = dict(context["month_choices"])
        context["monthly_month_name"] = month_names.get(monthly_month)
        context["yearly_monthly_breakdown"] = []
        for month_stats, (_, month_name) in zip(
            Statistics.get_yearly_month_breakdown(yearly_year),
            context["month_choices"],
        ):
            month_number = month_stats["month"]
            month_stats["month_name"] = month_name
            month_stats["net_result"] = (
                month_stats["orders_total"] - month_stats["total_expenses"]
            )
            month_stats["expense_debt_total"] = (
                month_stats["unpaid_salary_expenses"]
                + month_stats["unpaid_food_expenses"]
                + month_stats["unpaid_raw_expenses"]
                + month_stats["unpaid_other_expenses"]
            )
            month_stats["is_selected_month"] = (
                yearly_year == monthly_year and month_number == monthly_month
            )
            context["yearly_monthly_breakdown"].append(month_stats)

        if request.method == "GET":
            sanitized_get = request.GET.copy()
            changed = False
            for key in custom_query_params:
                if key in sanitized_get:
                    sanitized_get.pop(key, None)
                    changed = True
            if changed:
                request.GET = sanitized_get
                request.META["QUERY_STRING"] = sanitized_get.urlencode()

        return super().changelist_view(request, extra_context=context)


class ReportYearFilter(admin.SimpleListFilter):
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


class ReportMonthFilter(admin.SimpleListFilter):
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


@admin.register(DailyFinanceReport)
class DailyFinanceReportAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "date",
        "total_closed_sales",
        "total_earned_salary",
        "total_expenses",
        "balance",
        "updated_at",
    )
    list_filter = (ReportYearFilter, ReportMonthFilter)
    readonly_fields = list_display
    list_display_links = None
    actions = ("sync_selected_reports", "sync_all_reports")
    ordering = ("-date",)

    def changelist_view(self, request, extra_context=None):
        DailyFinanceReport.sync_all()
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Tanlangan hisobotlarni qayta hisoblash")
    def sync_selected_reports(self, request, queryset):
        for report in queryset:
            DailyFinanceReport.sync_for_date(report.date)
        self.message_user(request, "Tanlangan sanalar uchun hisobotlar yangilandi.")

    @admin.action(description="Barcha hisobotlarni qayta hisoblash")
    def sync_all_reports(self, request, queryset):
        total = DailyFinanceReport.sync_all()
        self.message_user(request, f"{total} ta sana bo'yicha hisobot yangilandi.")
