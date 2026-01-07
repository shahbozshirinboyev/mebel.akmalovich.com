from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'phone', 'is_active', 'is_staff', 'is_superuser', 'worker')
    list_filter = ('worker', 'is_staff')
    search_fields = ('username', 'phone')


# Admin paneldan group’ni olib tashlash
admin.site.unregister(Group)