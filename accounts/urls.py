from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),  # 主页
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # 邀请码相关URL
    path('invitations/', views.invitation_list_view, name='invitation_list'),
    path('invitations/create/', views.create_invitation_view, name='create_invitation'),
    path('invitations/<int:invitation_id>/delete/', views.delete_invitation_view, name='delete_invitation'),
    path('invitations/<int:invitation_id>/toggle/', views.toggle_invitation_status_view, name='toggle_invitation_status'),
] 