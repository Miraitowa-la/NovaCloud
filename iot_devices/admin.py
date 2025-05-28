from django.contrib import admin
from .models import Project, Device, Sensor, Actuator, SensorData, ActuatorCommandLog


class SensorInline(admin.TabularInline):
    """传感器内联编辑"""
    model = Sensor
    extra = 1


class ActuatorInline(admin.TabularInline):
    """执行器内联编辑"""
    model = Actuator
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """项目管理界面"""
    list_display = ('name', 'project_id', 'owner', 'created_at')
    search_fields = ('name', 'project_id', 'owner__username')
    list_filter = ('owner',)
    readonly_fields = ('project_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """设备管理界面"""
    list_display = ('name', 'device_id', 'project', 'status', 'last_seen', 'device_identifier')
    search_fields = ('name', 'device_id', 'project__name', 'device_identifier')
    list_filter = ('project', 'status')
    readonly_fields = ('device_id', 'device_key', 'created_at', 'updated_at', 'last_seen')
    inlines = [SensorInline, ActuatorInline]
    date_hierarchy = 'created_at'


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    """传感器数据管理界面"""
    list_display = ('sensor', 'timestamp', 'value_float', 'value_string', 'value_boolean')
    search_fields = ('sensor__name', 'sensor__device__name')
    list_filter = ('sensor__device', 'sensor', 'timestamp')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(ActuatorCommandLog)
class ActuatorCommandLogAdmin(admin.ModelAdmin):
    """执行器命令日志管理界面"""
    list_display = ('actuator', 'user', 'status', 'source', 'created_at', 'sent_at', 'acknowledged_at')
    search_fields = ('actuator__name', 'actuator__device__name', 'user__username')
    list_filter = ('status', 'source', 'actuator__device', 'actuator')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
