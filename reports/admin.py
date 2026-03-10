from django.contrib import admin

from .models import DailyFinanceReport


class ReportYearFilter(admin.SimpleListFilter):
	title = "Yil"
	parameter_name = "year"

	def lookups(self, request, model_admin):
		return [(str(year), str(year)) for year in range(2020, 2027)]

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
class DailyFinanceReportAdmin(admin.ModelAdmin):
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
