from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html

from .constants import AUDIT_ACTION_CHOICES


class AuditLog(models.Model):
    """
    审计日志模型，记录平台内的关键操作
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="操作用户"
    )
    action_type = models.CharField(
        max_length=100,
        choices=AUDIT_ACTION_CHOICES,
        db_index=True,
        verbose_name="操作类型"
    )
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="目标对象类型"
    )
    target_object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="目标对象ID"
    )
    target_object_repr = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="目标对象描述"
    )
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )
    details = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="详细信息"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP地址"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="时间戳"
    )

    class Meta:
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "系统"
        target_str = self.target_object_repr or "未指定"
        return f"{self.get_action_type_display()} - 由 {user_str} 在 {self.timestamp} 对 {target_str} 执行"
