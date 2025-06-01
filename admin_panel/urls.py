from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('roles/', views.role_list_view, name='role_list'),
    path('audit-logs/', views.audit_log_list_view, name='audit_log_list'),
] 