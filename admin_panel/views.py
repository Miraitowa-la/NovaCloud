from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import UserProfile, Role, InvitationCode
from core.models import AuditLog
from core.constants import AuditActionType, AUDIT_ACTION_CHOICES
from .decorators import admin_required
from .forms import AdminUserCreationForm, AdminUserChangeForm, RoleForm, AuditLogFilterForm
from django.http import JsonResponse
from django.db import transaction
import json

# Create your views here.

@login_required
@admin_required
def dashboard_view(request):
    """
    管理首页
    """
    # 用户统计数据
    user_count = User.objects.count()
    active_user_count = User.objects.filter(is_active=True).count()
    
    # 新注册用户（过去7天）
    one_week_ago = timezone.now() - timedelta(days=7)
    new_user_count = User.objects.filter(date_joined__gte=one_week_ago).count()
    
    # 角色统计数据
    role_count = Role.objects.count()
    permission_count = Permission.objects.count()
    
    # 自定义角色（排除可能的系统角色，如管理员、普通用户）
    # 假设ID小于等于2的是系统默认角色
    custom_role_count = Role.objects.filter(id__gt=2).count()
    
    # 审计日志统计
    total_log_count = AuditLog.objects.count()
    
    # 今日日志
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_log_count = AuditLog.objects.filter(timestamp__gte=today_start).count()
    
    # 近7天日志
    week_log_count = AuditLog.objects.filter(timestamp__gte=one_week_ago).count()
    
    # 最近活动（获取最新的5条审计日志）
    recent_activities = AuditLog.objects.select_related('user').all()[:5]
    
    context = {
        'admin_page_title': '系统管理',
        # 用户统计
        'user_count': user_count,
        'active_user_count': active_user_count,
        'new_user_count': new_user_count,
        # 角色统计
        'role_count': role_count, 
        'permission_count': permission_count,
        'custom_role_count': custom_role_count,
        # 审计日志统计
        'total_log_count': total_log_count,
        'today_log_count': today_log_count,
        'week_log_count': week_log_count,
        # 最近活动
        'recent_activities': recent_activities
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
    """切换用户激活状态"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        
        # 防止管理员停用自己的账户
        if user_obj == request.user:
            messages.error(request, '您不能停用自己的账户')
            return redirect('admin_panel:user_list')
        
        # 切换状态
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        
        # 记录审计日志
        action = "启用" if user_obj.is_active else "禁用"
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditActionType.USER_STATUS_CHANGE,
            target_object_id=user_obj.id,
            target_object_repr=f"用户 {user_obj.username}",
            details=f"管理员 {request.user.username} {action}了用户 {user_obj.username}"
        )
        
        messages.success(request, f'用户 {user_obj.username} 已{action}')
    
    return redirect('admin_panel:user_list')

@admin_required
def user_delete_confirm_view(request, user_id):
    """确认删除用户视图"""
    user_obj = get_object_or_404(User, id=user_id)
    
    # 防止管理员删除自己的账户
    if user_obj == request.user:
        messages.error(request, '您不能删除自己的账户')
        return redirect('admin_panel:user_list')
    
    context = {
        'user_obj': user_obj,
        'admin_page_title': '确认删除用户',
    }
    return render(request, 'admin_panel/user_confirm_delete.html', context)

@admin_required
def user_delete_view(request, user_id):
    """删除用户视图"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        
        # 防止管理员删除自己的账户
        if user_obj == request.user:
            messages.error(request, '您不能删除自己的账户')
            return redirect('admin_panel:user_list')
        
        username = user_obj.username
        
        # 记录审计日志
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditActionType.USER_DELETE,
            target_object_id=user_id,
            target_object_repr=f"用户 {username}",
            details=f"管理员 {request.user.username} 删除了用户 {username}"
        )
        
        # 删除用户
        user_obj.delete()
        
        messages.success(request, f'用户 {username} 已删除')
        return redirect('admin_panel:user_list')
    
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

@admin_required
def user_hierarchy_view(request):
    """用户层级树视图 - 组织架构"""
    # 获取所有超级管理员（staff用户）
    super_admins = User.objects.filter(
        is_staff=True
    ).select_related('profile').prefetch_related('profile__role').order_by('username')
    
    # 获取超级管理员的ID列表
    admin_ids = list(super_admins.values_list('id', flat=True))
    
    # 获取根节点（超级管理员直接下级的用户）
    root_nodes = User.objects.filter(
        profile__parent_user__in=admin_ids,
        is_staff=False
    ).select_related('profile').prefetch_related('profile__role').distinct().order_by('username')
    
    # 获取所有用户
    all_users = User.objects.select_related('profile').prefetch_related('profile__role').all()
    
    # 构建用户层级数据结构
    user_hierarchy = {}
    
    # 先建立用户ID到用户对象的映射
    user_map = {user.id: user for user in all_users}
    
    # 为每个用户创建层级结构条目
    for user in all_users:
        user_hierarchy[user.id] = {
            'user': user,
            'children': []
        }
    
    # 构建层级关系
    for user in all_users:
        if hasattr(user, 'profile') and user.profile.parent_user_id:
            parent_id = user.profile.parent_user_id
            if parent_id in user_hierarchy:
                user_hierarchy[parent_id]['children'].append(user)
    
    # 为超级管理员找到直接下级（根节点）
    admin_direct_children = {}
    for admin in super_admins:
        admin_direct_children[admin.id] = []
        for user in all_users:
            if (hasattr(user, 'profile') and 
                user.profile.parent_user_id == admin.id):
                admin_direct_children[admin.id].append(user)
    
    # 获取既不是超级管理员、又没有上级用户的孤立用户
    # 1. 不是超级管理员
    # 2. 没有上级用户 (profile__parent_user为空)
    # 3. 不在根节点列表中 (可能已经在其他地方显示)
    orphan_users = User.objects.filter(
        is_staff=False,
        profile__parent_user__isnull=True
    ).exclude(
        id__in=admin_ids  # 排除超级管理员
    ).exclude(
        id__in=root_nodes.values_list('id', flat=True)  # 排除根节点
    ).select_related('profile').prefetch_related('profile__role').distinct().order_by('username')
    
    context = {
        'super_admins': super_admins,
        'root_nodes': root_nodes,
        'user_hierarchy': user_hierarchy,
        'admin_direct_children': admin_direct_children,
        'orphan_users': orphan_users,  # 添加孤立用户到上下文
        'admin_page_title': '用户层级树'
    }
    
    return render(request, 'admin_panel/user_hierarchy.html', context)

@admin_required
def update_user_hierarchy_view(request):
    """更新用户层级关系的API"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '只允许POST请求'})
    
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        source_user_id = data.get('source_user_id')
        target_user_id = data.get('target_user_id')  # None表示移动到根级别
        
        # 验证用户ID
        if not source_user_id:
            return JsonResponse({'success': False, 'message': '缺少源用户ID'})
        
        # 获取源用户
        try:
            source_user = User.objects.get(id=source_user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '源用户不存在'})
        
        # 检查源用户是否为超级管理员，超级管理员不能设置上级用户
        if source_user.is_staff:
            return JsonResponse({'success': False, 'message': '超级管理员不能设置上级用户'})
        
        # 获取目标用户（如果有）
        target_user = None
        if target_user_id:
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': '目标用户不存在'})
            
            # 检查目标用户是否为超级管理员，超级管理员不能作为上级用户
            if target_user.is_staff:
                # 这种情况实际上是合法的，超级管理员可以作为其他用户的上级
                pass
                
            # 检查是否会导致循环引用（目标用户不能是源用户的下级）
            if is_descendant(target_user_id, source_user_id):
                return JsonResponse({'success': False, 'message': '不能将用户移动到自己的下级用户下'})
            
            # 检查是否会导致互为上下级的情况（源用户不能是目标用户的上级）
            if is_ancestor(source_user_id, target_user_id):
                return JsonResponse({'success': False, 'message': '不能将上级用户移动到下级用户下'})
        
        # 更新用户层级关系
        with transaction.atomic():
            source_profile = UserProfile.objects.get(user=source_user)
            old_parent = source_profile.parent_user
            
            # 更新父级用户
            source_profile.parent_user = target_user
            source_profile.save()
            
            # 记录审计日志
            log_message = f"用户层级变更: "
            if old_parent:
                log_message += f"从 '{old_parent.username}' 的下级"
            else:
                log_message += "从根级别"
                
            if target_user:
                log_message += f" 移动到 '{target_user.username}' 的下级"
            else:
                log_message += " 移动到根级别"
            
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditActionType.USER_UPDATE,
                target_object_id=source_user.id,
                target_object_repr=f"User: {source_user.username}",
                details=log_message,
                ip_address=get_client_ip(request)
            )
        
        # 构建成功消息
        message = f"用户 '{source_user.username}' 已"
        if target_user:
            message += f"成为 '{target_user.username}' 的下级"
        else:
            message += "移动到根级别"
            
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'发生错误: {str(e)}'})

def is_descendant(user_id, potential_ancestor_id):
    """检查用户是否是另一个用户的后代（下级）"""
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return False
    
    # 如果没有父级，则不是任何人的后代
    if not user.parent_user_id:
        return False
    
    # 如果直接父级就是潜在祖先，则是后代
    if user.parent_user_id == potential_ancestor_id:
        return True
    
    # 递归检查父级是否是潜在祖先的后代
    return is_descendant(user.parent_user_id, potential_ancestor_id)

def is_ancestor(user_id, potential_descendant_id):
    """检查用户是否是另一个用户的祖先（上级）"""
    # 直接利用已有的is_descendant函数
    return is_descendant(potential_descendant_id, user_id)

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
