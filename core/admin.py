from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """审计日志管理界面"""
    list_display = ('timestamp', 'user_display', 'action_type_display', 'target_link', 'ip_address')
    search_fields = ('user__username', 'action_type', 'target_object_repr', 'ip_address')
    list_filter = ('action_type', 'user', ('timestamp', admin.DateFieldListFilter))
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    date_hierarchy = 'timestamp'
    
    def user_display(self, obj):
        """返回用户名，如果是系统操作则显示'系统'"""
        if obj.user:
            return obj.user.username
        return '系统'
    user_display.short_description = "操作用户"
    
    def action_type_display(self, obj):
        """返回操作类型的可读名称"""
        return obj.get_action_type_display()
    action_type_display.short_description = "操作类型"
    
    def target_link(self, obj):
        """尝试生成到目标对象Admin页面的链接"""
        if not obj.target_content_type or not obj.target_object_id:
            return obj.target_object_repr or '-'
        
        try:
            # 尝试获取目标对象的Admin URL
            app_label = obj.target_content_type.app_label
            model_name = obj.target_content_type.model
            url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.target_object_id])
            return format_html('<a href="{}">{}</a>', url, obj.target_object_repr or f"{model_name} {obj.target_object_id}")
        except Exception:
            # 如果无法生成链接，则只显示文本
            return obj.target_object_repr or f"{obj.target_content_type} {obj.target_object_id}"
    target_link.short_description = "目标对象"
    
    def has_add_permission(self, request):
        """禁止手动添加审计日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改审计日志"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """禁止删除审计日志（可根据需要设置为True）"""
        return False
