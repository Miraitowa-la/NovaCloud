from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.http import require_POST
from accounts.models import UserProfile, Role
from core.models import AuditLog
from core.constants import AuditActionType
from .decorators import admin_required
from .forms import AdminUserCreationForm, AdminUserChangeForm

# Create your views here.

@login_required
def dashboard_view(request):
    """
    管理首页
    """
    # 权限检查逻辑应在这里或装饰器中实现
    # if not request.user.is_staff and not request.user.userprofile.role_has_permission('can_access_admin_panel'):
    #     return HttpResponseForbidden("您没有权限访问该页面")
    
    context = {
        'admin_page_title': '系统管理'
    }
    return render(request, 'admin_panel/dashboard.html', context)

@admin_required
def user_list_view(request):
    """用户列表视图"""
    # 获取搜索和筛选参数
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # 查询用户列表
    users = User.objects.select_related('userprofile').all()
    
    # 应用搜索条件
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    # 应用角色筛选
    if role_filter:
        users = users.filter(userprofile__role_id=role_filter)
    
    # 应用状态筛选
    if status_filter:
        is_active = status_filter == 'active'
        users = users.filter(is_active=is_active)
    
    # 排序（默认按注册时间降序）
    users = users.order_by('-date_joined')
    
    # 分页
    paginator = Paginator(users, 10)  # 每页10条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 获取所有角色供筛选使用
    roles = Role.objects.all()
    
    # 渲染模板
    context = {
        'page_obj': page_obj,
        'roles': roles,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'admin_page_title': '用户管理',
    }
    return render(request, 'admin_panel/user_list.html', context)

@admin_required
def user_create_view(request):
    """创建用户视图"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditActionType.USER_CREATE,
                target_object_id=user.id,
                target_object_repr=f"用户 {user.username}",
                details=f"管理员 {request.user.username} 创建了用户 {user.username}"
            )
            
            messages.success(request, f'用户 {user.username} 已成功创建')
            return redirect('admin_panel:user_list')
    else:
        form = AdminUserCreationForm()
    
    context = {
        'form': form,
        'is_create': True,
        'admin_page_title': '创建用户',
    }
    return render(request, 'admin_panel/user_form.html', context)

@admin_required
def user_update_view(request, user_id):
    """更新用户视图"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditActionType.USER_UPDATE,
                target_object_id=user.id,
                target_object_repr=f"用户 {user.username}",
                details=f"管理员 {request.user.username} 更新了用户 {user.username} 的信息"
            )
            
            messages.success(request, f'用户 {user.username} 已成功更新')
            return redirect('admin_panel:user_list')
    else:
        form = AdminUserChangeForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user,  # 避免与模板上下文中的user冲突
        'is_create': False,
        'admin_page_title': f'编辑用户 - {user.username}',
    }
    return render(request, 'admin_panel/user_form.html', context)

@admin_required
@require_POST
def user_toggle_active_view(request, user_id):
    """切换用户活动状态视图"""
    user = get_object_or_404(User, id=user_id)
    
    # 不允许管理员停用自己的账户
    if user == request.user:
        messages.error(request, '不能停用您自己的账户')
        return redirect('admin_panel:user_list')
    
    # 切换状态
    user.is_active = not user.is_active
    user.save()
    
    # 记录审计日志
    status_text = "启用" if user.is_active else "停用"
    AuditLog.objects.create(
        user=request.user,
        action_type=AuditActionType.USER_STATUS_CHANGE,
        target_object_id=user.id,
        target_object_repr=f"用户 {user.username}",
        details=f"管理员 {request.user.username} {status_text}了用户 {user.username}"
    )
    
    messages.success(request, f'用户 {user.username} 已被{status_text}')
    return redirect('admin_panel:user_list')

# 用于后续实现的角色与权限管理视图占位
@login_required
def role_list_view(request):
    """
    角色列表页面
    """
    context = {
        'admin_page_title': '角色与权限'
    }
    return render(request, 'admin_panel/role_list.html', context)

# 用于后续实现的审计日志视图占位
@login_required
def audit_log_list_view(request):
    """
    审计日志列表页面
    """
    context = {
        'admin_page_title': '审计日志'
    }
    return render(request, 'admin_panel/audit_log_list.html', context)
