from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

from .forms import UserRegistrationForm
from .models import UserProfile

def register_view(request):
    """
    用户注册视图
    处理用户注册表单的提交和验证
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # 保存用户信息
            new_user = form.save()
            
            # 创建用户配置文件
            UserProfile.objects.create(user=new_user)
            
            # 添加成功消息
            messages.success(request, '恭喜您，注册成功！现在您可以登录了。')
            
            # 重定向到登录页面
            return redirect('accounts:login')
        else:
            # 添加错误消息
            messages.error(request, '注册失败，请检查您输入的信息。')
    else:
        # GET请求，显示空表单
        form = UserRegistrationForm()
    
    # 渲染注册模板
    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': '用户注册'
    })
