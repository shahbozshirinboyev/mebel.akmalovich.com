from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User
from core.admin_mixins import PreserveFiltersAdminMixin
from django.utils.html import format_html
from datetime import datetime

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(PreserveFiltersAdminMixin, admin.ModelAdmin):

    def superuser_col(self, obj):
        return obj.is_superuser
    superuser_col.short_description = 'Суперпользователь'
    superuser_col.boolean = True

    def formatted_date_joined(self, obj):
        return format_html('<span style="font-size: 12px;">{}</span>', obj.date_joined.strftime('%d.%m.%Y, %H:%M'))

    def formatted_last_login(self, obj):
        if obj.last_login:
            return format_html('<span style="font-size: 12px;">{}</span>', obj.last_login.strftime('%d.%m.%Y, %H:%M'))
        else:
            return format_html('<span style="font-size: 12px;">{}</span>', '-')

    def username_col(self, obj):
        return obj.username
    username_col.short_description = 'Пользователь'

    formatted_date_joined.short_description = 'Дата регистрации'
    formatted_last_login.short_description = 'Последний вход'

    list_display = (
        'id',
        'username_col',
        'first_name',
        'last_name',
        'phone_number',
        'superuser_col', # super foydalanuvchi huquqi
        'is_active',    # faollik holati
        'is_staff',     # admin panelga kirish huquqi
        'is_worker',
        'is_manager',
        'formatted_date_joined',
        'formatted_last_login',
    )
    def is_superuser_short(self, obj):
        return obj.is_superuser
    is_superuser_short.short_description = 'Суперпользователь'
    is_superuser_short.boolean = True
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ()

    class Media:
        css = {
            'all': ('/static/admin/css/custom_admin.css',)
        }