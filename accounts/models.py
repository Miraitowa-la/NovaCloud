from django.db import models
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from django.utils.crypto import get_random_string


class Role(models.Model):
    """
    角色模型，定义用户角色及其权限
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="角色名称")
    codename = models.CharField(max_length=50, unique=True, verbose_name="角色代码")
    description = models.TextField(blank=True, verbose_name="角色描述")
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="权限"
    )

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    用户配置文件，扩展Django内置用户模型
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="用户"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="角色"
    )
    parent_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_profiles',
        verbose_name="上级用户"
    )
    avatar = models.URLField(
        null=True,
        blank=True,
        verbose_name="头像"
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="电话号码"
    )

    class Meta:
        verbose_name = "用户配置文件"
        verbose_name_plural = "用户配置文件"
    
    def __str__(self):
        return self.user.username


class InvitationCode(models.Model):
    """
    邀请码模型，用于邀请新用户注册
    """
    code = models.CharField(
        max_length=32, 
        unique=True,
        db_index=True,
        verbose_name="邀请码"
    )
    issuer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='issued_invitations',
        verbose_name="发行者"
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="最大使用次数"
    )
    times_used = models.PositiveIntegerField(
        default=0,
        verbose_name="已使用次数"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="过期时间"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )

    class Meta:
        verbose_name = "邀请码"
        verbose_name_plural = "邀请码"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """重写保存方法，自动生成邀请码"""
        # 仅在新对象创建且未设置code时生成邀请码
        if not self.code:
            # 循环尝试生成唯一邀请码，直到成功
            while True:
                # 生成16位随机字符串，包含字母和数字
                new_code = get_random_string(16, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                # 检查是否已存在相同邀请码
                if not InvitationCode.objects.filter(code=new_code).exists():
                    self.code = new_code
                    break
        super().save(*args, **kwargs)
    
    @property
    def is_currently_valid(self):
        """
        判断邀请码当前是否有效
        条件：1.处于激活状态 2.未超过最大使用次数 3.未过期
        """
        # 检查是否激活
        if not self.is_active:
            return False
        
        # 检查是否达到最大使用次数限制
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        
        # 检查是否过期
        if self.expires_at is not None and timezone.now() > self.expires_at:
            return False
            
        return True

    def __str__(self):
        return self.code
