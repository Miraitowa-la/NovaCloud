from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:user_id>/update/', views.user_update_view, name='user_update'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active_view, name='user_toggle_active'),
    path('roles/', views.role_list_view, name='role_list'),
    path('roles/create/', views.role_create_view, name='role_create'),
    path('roles/<int:role_id>/update/', views.role_update_view, name='role_update'),
    path('roles/<int:role_id>/delete/', views.role_delete_view, name='role_delete'),
    path('audit-logs/', views.audit_log_list_view, name='audit_log_list'),
    path('audit-logs/<int:log_id>/', views.audit_log_detail_view, name='audit_log_detail'),
] 