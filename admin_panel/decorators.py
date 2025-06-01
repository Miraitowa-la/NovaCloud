from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    """
    要求用户必须是管理员的装饰器
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # 检查用户是否是管理员 (is_staff)
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("您没有访问此页面的权限")
    return _wrapped_view 