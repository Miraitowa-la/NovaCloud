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