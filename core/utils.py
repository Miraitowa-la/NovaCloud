from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


def log_audit(
    action_type,
    user=None,
    target=None,
    target_repr=None,
    details=None,
    ip_address=None
):
    """
    记录审计日志的通用工具函数
    
    参数:
        action_type (str): 操作类型，使用constants.py中定义的常量
        user (User): 执行操作的用户，如果是系统操作则为None
        target (Model instance): 操作目标对象，如Project、Device等
        target_repr (str): 目标对象的字符串表示，如果提供target则可不提供
        details (dict): 操作的详细信息，如修改内容、参数等
        ip_address (str): 操作者的IP地址
    
    返回:
        AuditLog: 创建的审计日志对象
    """
    target_content_type = None
    target_object_id = None
    
    # 如果提供了目标对象
    if target:
        target_content_type = ContentType.objects.get_for_model(target)
        target_object_id = str(target.pk)
        # 如果没有提供目标对象描述，尝试使用对象的字符串表示
        if not target_repr:
            target_repr = str(target)
    
    # 创建审计日志
    log = AuditLog.objects.create(
        user=user,
        action_type=action_type,
        target_content_type=target_content_type,
        target_object_id=target_object_id,
        target_object_repr=target_repr,
        details=details or {},
        ip_address=ip_address
    )
    
    return log


def log_audit_event(request, action_type, target_object=None, details=None):
    """
    从HTTP请求中记录审计日志的便捷函数
    
    参数:
        request (HttpRequest): HTTP请求对象，用于获取用户和IP地址
        action_type (str): 操作类型，使用constants.py中定义的常量
        target_object (Model instance): 操作目标对象，如Project、Device等
        details (dict): 操作的详细信息，可以是字典或字符串
    
    返回:
        AuditLog: 创建的审计日志对象
    """
    # 获取用户（可能是匿名用户）
    user = request.user if request.user.is_authenticated else None
    
    # 获取IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # 如果details是字符串，转换为字典
    if isinstance(details, str):
        details = {"message": details}
    
    # 调用主函数记录日志
    return log_audit(
        action_type=action_type,
        user=user,
        target=target_object,
        details=details,
        ip_address=ip_address
    ) 