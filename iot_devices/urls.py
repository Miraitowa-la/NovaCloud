from django.urls import path
from . import views

app_name = 'iot_devices'

urlpatterns = [
    # 项目管理URLs
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<uuid:project_id>/update/', views.project_update_view, name='project_update'),
    path('projects/<uuid:project_id>/delete/', views.project_delete_view, name='project_delete'),
] 