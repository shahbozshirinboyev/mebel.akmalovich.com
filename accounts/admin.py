from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User


admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        # 'phone_number',
        'is_superuser', # super foydalanuvchi huquqi
        'is_active',    # faollik holati
        'is_staff',     # admin panelga kirish huquqi
        'is_worker',
        'is_manager',
        # 'date_joined',
        # 'last_login',
    )
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('is_worker', 'is_manager', 'is_active')