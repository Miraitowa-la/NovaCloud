from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import UserProfile, Role
from core.models import AuditLog
from core.constants import AuditActionType, AUDIT_ACTION_CHOICES
from .decorators import admin_required
from .forms import AdminUserCreationForm, AdminUserChangeForm, RoleForm, AuditLogFilterForm

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
    
    # 处理URL参数，为分页准备
    filter_params = request.GET.copy()
    if 'page' in filter_params:
        filter_params.pop('page')
    filter_params_encoded = filter_params.urlencode()
    
    # 查询用户列表
    users = User.objects.select_related('profile').all()
    
    # 应用搜索条件
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    # 应用角色筛选
    if role_filter:
        users = users.filter(profile__role_id=role_filter)
    
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
        'filter_params_encoded': filter_params_encoded,
        'filter_params_with_amp': f'&{filter_params_encoded}' if filter_params_encoded else ''
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

@admin_required
def role_list_view(request):
    """角色列表视图"""
    # 获取搜索参数
    search_query = request.GET.get('search', '')
    
    # 查询角色列表，并关联用户数量
    roles = Role.objects.annotate(user_count=Count('userprofile'))
    
    # 应用搜索条件
    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) | 
            Q(codename__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 排序
    roles = roles.order_by('name')
    
    # 分页
    paginator = Paginator(roles, 10)  # 每页10条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 渲染模板
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'admin_page_title': '角色与权限管理',
    }
    return render(request, 'admin_panel/role_list.html', context)

@admin_required
def role_create_view(request):
    """创建角色视图"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditActionType.ROLE_CREATE,
                target_object_id=role.id,
                target_object_repr=f"角色 {role.name}",
                details=f"管理员 {request.user.username} 创建了角色 {role.name}"
            )
            
            messages.success(request, f'角色 {role.name} 已成功创建')
            return redirect('admin_panel:role_list')
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'is_create': True,
        'admin_page_title': '创建角色',
    }
    return render(request, 'admin_panel/role_form.html', context)

@admin_required
def role_update_view(request, role_id):
    """更新角色视图"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditActionType.ROLE_UPDATE,
                target_object_id=role.id,
                target_object_repr=f"角色 {role.name}",
                details=f"管理员 {request.user.username} 更新了角色 {role.name} 的信息和权限"
            )
            
            messages.success(request, f'角色 {role.name} 已成功更新')
            return redirect('admin_panel:role_list')
    else:
        form = RoleForm(instance=role)
    
    # 获取关联到此角色的用户数量
    user_count = UserProfile.objects.filter(role=role).count()
    
    context = {
        'form': form,
        'role': role,
        'user_count': user_count,
        'is_create': False,
        'admin_page_title': f'编辑角色 - {role.name}',
    }
    return render(request, 'admin_panel/role_form.html', context)

@admin_required
@require_POST
def role_delete_view(request, role_id):
    """删除角色视图"""
    role = get_object_or_404(Role, id=role_id)
    
    # 检查是否有用户使用此角色
    user_count = UserProfile.objects.filter(role=role).count()
    if user_count > 0:
        messages.error(request, f'无法删除角色 {role.name}，因为有 {user_count} 个用户正在使用此角色')
        return redirect('admin_panel:role_list')
    
    role_name = role.name
    role.delete()
    
    # 记录审计日志
    AuditLog.objects.create(
        user=request.user,
        action_type=AuditActionType.ROLE_DELETE,
        target_object_repr=f"角色 {role_name}",
        details=f"管理员 {request.user.username} 删除了角色 {role_name}"
    )
    
    messages.success(request, f'角色 {role_name} 已成功删除')
    return redirect('admin_panel:role_list')

@admin_required
def audit_log_list_view(request):
    """
    审计日志列表页面，支持多条件筛选和分页
    """
    # 初始化筛选表单
    form = AuditLogFilterForm(request.GET)
    
    # 获取基础查询集
    logs_query = AuditLog.objects.select_related('user', 'target_content_type').order_by('-timestamp')
    
    # 处理URL参数，为分页准备
    filter_params = request.GET.copy()
    if 'page' in filter_params:
        filter_params.pop('page')
    filter_params_encoded = filter_params.urlencode()
    
    # 应用筛选条件
    if form.is_valid():
        # 用户筛选
        user_id = form.cleaned_data.get('user')
        if user_id:
            logs_query = logs_query.filter(user=user_id)
        
        # 操作类型筛选
        action_type = form.cleaned_data.get('action_type')
        if action_type:
            logs_query = logs_query.filter(action_type=action_type)
        
        # 日期范围筛选
        start_date = form.cleaned_data.get('start_date')
        if start_date:
            logs_query = logs_query.filter(timestamp__gte=start_date)
        
        end_date = form.cleaned_data.get('end_date')
        if end_date:
            # 调整结束日期到当天结束
            end_date_adjusted = datetime.combine(end_date, datetime.max.time())
            logs_query = logs_query.filter(timestamp__lte=end_date_adjusted)
        
        # IP地址筛选
        ip_address = form.cleaned_data.get('ip_address')
        if ip_address:
            logs_query = logs_query.filter(ip_address__icontains=ip_address)
        
        # 详情搜索
        search_query = form.cleaned_data.get('search_query')
        if search_query:
            logs_query = logs_query.filter(
                Q(target_object_repr__icontains=search_query) | 
                Q(details__icontains=search_query)
            )
    
    # 分页处理
    paginator = Paginator(logs_query, 20)  # 每页显示20条记录
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 构建上下文
    context = {
        'admin_page_title': '审计日志',
        'form': form,
        'page_obj': page_obj,
        'action_choices': AUDIT_ACTION_CHOICES,
        # 构建分页URL时保留筛选参数
        'filter_params_encoded': filter_params_encoded,
        'filter_params_with_amp': f'&{filter_params_encoded}' if filter_params_encoded else ''
    }
    
    return render(request, 'admin_panel/audit_log_list.html', context)

@admin_required
def audit_log_detail_view(request, log_id):
    """
    审计日志详情页面
    """
    # 获取指定ID的审计日志记录
    log = get_object_or_404(AuditLog, id=log_id)
    
    # 构建返回列表页的URL，保留筛选参数
    back_url = f"{reverse('admin_panel:audit_log_list')}?{request.GET.urlencode()}" if request.GET else reverse('admin_panel:audit_log_list')
    
    # 构建上下文
    context = {
        'admin_page_title': '审计日志详情',
        'log': log,
        'back_url': back_url
    }
    
    return render(request, 'admin_panel/audit_log_detail.html', context)
