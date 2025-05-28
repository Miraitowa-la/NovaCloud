from django.contrib import admin
from .models import UserProfile, Role, InvitationCode


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


@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'issuer', 'is_active_status', 'times_used', 'max_uses', 'expires_at', 'created_at')
    search_fields = ('code', 'issuer__username')
    list_filter = ('is_active', 'issuer')
    readonly_fields = ('code', 'times_used', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'issuer')
        }),
        ('使用限制', {
            'fields': ('is_active', 'times_used', 'max_uses', 'expires_at')
        }),
        ('系统信息', {
            'fields': ('created_at',)
        }),
    )
    
    def is_active_status(self, obj):
        """返回邀请码当前是否有效"""
        return obj.is_currently_valid
    
    is_active_status.boolean = True
    is_active_status.short_description = '当前有效'
