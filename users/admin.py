from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'full_name',  'phone_number', 'is_worker', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')
    list_filter = ()
    search_fields = ()
    readonly_fields = ('date_joined',)  

    fieldsets = (
        ('Foydalanuvchi nomi va Parol', {'fields': ('username', 'password')}),
        ('Shaxsiy ma’lumotlar', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Ruxsat darajalari', {'fields': ('is_worker', 'is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Harakat vaqtlari', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('Foydalanuvchi nomi va Parol', {
        'classes': ('wide',),
        'fields': ('username', 'password1', 'password2')
    }),
    ('Shaxsiy ma’lumotlar', {
        'fields': ('first_name', 'last_name', 'phone_number')
    }),
    ('Ruxsat darajalari', {
        'fields': ('is_worker', 'is_staff', 'is_active')
    }),
    )

    def response_add(self, request, obj, post_url_continue=None):
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:users_user_changelist'))