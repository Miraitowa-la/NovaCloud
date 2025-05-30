from django.urls import path
from . import views

app_name = 'iot_devices'

urlpatterns = [
    # 项目管理URLs
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<uuid:project_id>/update/', views.project_update_view, name='project_update'),
    path('projects/<uuid:project_id>/delete/', views.project_delete_view, name='project_delete'),
    
    # 设备管理URLs
    path('projects/<uuid:project_id>/devices/', views.device_list_view, name='device_list'),
    path('projects/<uuid:project_id>/devices/create/', views.device_create_view, name='device_create'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/', views.device_detail_view, name='device_detail'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/update/', views.device_update_view, name='device_update'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/delete/', views.device_delete_view, name='device_delete'),
    
    # 传感器管理URLs
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/sensors/add/', views.sensor_add_view, name='sensor_add'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/sensors/<int:sensor_id>/update/', views.sensor_update_view, name='sensor_update'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/sensors/<int:sensor_id>/delete/', views.sensor_delete_view, name='sensor_delete'),
    
    # 执行器管理URLs
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/actuators/add/', views.actuator_add_view, name='actuator_add'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/actuators/<int:actuator_id>/update/', views.actuator_update_view, name='actuator_update'),
    path('projects/<uuid:project_id>/devices/<uuid:device_id>/actuators/<int:actuator_id>/delete/', views.actuator_delete_view, name='actuator_delete'),
] 