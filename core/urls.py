from django.urls import path
from . import views

app_name = 'core'  # 定义 app 命名空间

urlpatterns = [
    path('', views.index, name='index'),
] 