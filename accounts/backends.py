from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameModelBackend(ModelBackend):
    """
    自定义认证后端，允许用户使用邮箱或用户名登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # 尝试通过用户名或邮箱查找用户
        try:
            # 先检查输入是否是邮箱
            if '@' in username:
                user = UserModel.objects.get(email=username)
            else:
                # 否则认为是用户名
                user = UserModel.objects.get(username=username)
                
            # 检查密码
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # 返回None表示认证失败
            return None 