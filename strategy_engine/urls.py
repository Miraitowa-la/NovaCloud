from django.urls import path
from . import views

app_name = 'strategy_engine'

urlpatterns = [
    # 策略CRUD相关URL
    path('strategies/', views.strategy_list_view, name='strategy_list'),
    path('strategies/create/', views.strategy_create_view, name='strategy_create'),
    path('strategies/<int:strategy_id>/update/', views.strategy_update_view, name='strategy_update'),
    path('strategies/<int:strategy_id>/delete/', views.strategy_delete_view, name='strategy_delete'),
    
    # 策略详情和配置URL
    path('strategies/<int:strategy_id>/', views.strategy_detail_view, name='strategy_detail'),
] 