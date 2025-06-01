from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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

# 用于后续实现的用户管理视图占位
@login_required
def user_list_view(request):
    """
    用户列表页面
    """
    context = {
        'admin_page_title': '用户管理'
    }
    return render(request, 'admin_panel/user_list.html', context)

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
