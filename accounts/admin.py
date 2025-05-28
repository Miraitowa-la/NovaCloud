from django.contrib import admin
from .models import UserProfile, Role


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'parent_user', 'phone_number')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('role',)
    raw_id_fields = ('user', 'parent_user')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'description')
    search_fields = ('name', 'codename')
    filter_horizontal = ('permissions',)
