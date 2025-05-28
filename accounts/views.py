from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages

from .forms import UserRegistrationForm, UserLoginForm
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


def login_view(request):
    """
    用户登录视图
    处理用户登录表单的提交和验证
    """
    # 获取用户可能要登录后重定向的URL
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            # 获取认证通过的用户
            user = form.get_user()
            
            # 检查用户是否有效
            if user is not None and user.is_active:
                # 登录用户
                login(request, user)
                
                # 添加成功消息
                messages.success(request, f'欢迎回来，{user.username}！')
                
                # 根据next参数决定重定向URL
                if 'next' in request.POST and request.POST.get('next'):
                    return redirect(request.POST.get('next'))
                else:
                    return redirect('core:index')  # 默认重定向到首页
            else:
                # 用户无效或未激活
                messages.error(request, '登录失败：账户未激活或已被禁用。')
        else:
            # 表单验证失败
            messages.error(request, '登录失败：请输入有效的用户名/邮箱和密码。')
    else:
        # GET请求，显示空表单
        form = UserLoginForm()
    
    # 渲染登录模板
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'page_title': '用户登录'
    })
