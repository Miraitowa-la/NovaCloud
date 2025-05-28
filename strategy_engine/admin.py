from django.contrib import admin
from .models import Strategy, ConditionGroup, Condition, Action, ExecutionLog


class ConditionInline(admin.TabularInline):
    """条件内联编辑"""
    model = Condition
    extra = 1


class ConditionGroupInline(admin.StackedInline):
    """条件组内联编辑"""
    model = ConditionGroup
    extra = 1
    classes = ['collapse', 'open']


class ActionInline(admin.TabularInline):
    """动作内联编辑"""
    model = Action
    extra = 1
    classes = ['collapse', 'open']


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    """策略管理界面"""
    list_display = ('name', 'project', 'owner', 'trigger_type', 'is_enabled', 'updated_at')
    list_filter = ('is_enabled', 'trigger_type', 'project', 'owner')
    search_fields = ('name', 'description', 'project__name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'updated_at'
    inlines = [ConditionGroupInline, ActionInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'owner', 'project')
        }),
        ('触发设置', {
            'fields': ('trigger_type', 'is_enabled')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ConditionGroup)
class ConditionGroupAdmin(admin.ModelAdmin):
    """条件组管理界面（可独立访问以管理条件）"""
    list_display = ('id', 'strategy', 'logical_operator', 'execution_order')
    list_filter = ('logical_operator', 'strategy')
    inlines = [ConditionInline]


class ConditionAdmin(admin.ModelAdmin):
    """条件管理界面（一般不单独使用，主要通过ConditionGroup内联）"""
    list_display = ('id', 'group', 'data_source_type', 'operator')
    list_filter = ('data_source_type', 'operator', 'group__strategy')


class ActionAdmin(admin.ModelAdmin):
    """动作管理界面（一般不单独使用，主要通过Strategy内联）"""
    list_display = ('id', 'strategy', 'action_type', 'execution_order')
    list_filter = ('action_type', 'strategy')


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    """执行日志管理界面"""
    list_display = ('strategy_name_display', 'triggered_at', 'status')
    list_filter = ('status', 'strategy')
    search_fields = ('strategy__name',)
    date_hierarchy = 'triggered_at'
    readonly_fields = [f.name for f in ExecutionLog._meta.fields]
    
    def strategy_name_display(self, obj):
        """返回策略名称，处理策略可能为空的情况"""
        if obj.strategy:
            return obj.strategy.name
        return "已删除的策略"
    
    strategy_name_display.short_description = "策略名称"


# 如果需要单独管理这些模型，取消注释以下行
# admin.site.register(Condition, ConditionAdmin)
# admin.site.register(Action, ActionAdmin)
