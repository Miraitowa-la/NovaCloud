from django.contrib import admin
from .models import Project, Device, Sensor, Actuator


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
