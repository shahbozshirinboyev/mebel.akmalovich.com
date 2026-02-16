from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

# Guruhlarni (Groups) admin panelidan olib tashlash
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Ko'rsatiladigan ustunlar
    list_display = ('username', 'full_name',  'phone_number', 'is_worker', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')
    list_filter = ()
    search_fields = ()

    # Edit (change) sahifadagi inputlar ketma-ketligi
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_worker', 'is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Yangi user qo'shish formidagi inputlar ketma-ketligi
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'password1', 'password2', 'phone_number', 'is_worker', 'is_staff', 'is_active', 'user_permissions'),
        }),
    )