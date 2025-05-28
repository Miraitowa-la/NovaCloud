from django.db import models
from django.contrib.auth.models import User, Permission


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
    avatar = models.ImageField(
        upload_to='avatars/',
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
