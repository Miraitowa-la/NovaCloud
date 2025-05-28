import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Project(models.Model):
    """
    物联网项目模型，代表一个完整的物联网应用场景
    """
    project_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="项目ID"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="项目名称"
    )
    description = models.TextField(
        blank=True,
        verbose_name="项目描述"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="所有者"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Device(models.Model):
    """
    设备模型，代表一个物联网设备
    """
    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('unregistered', '未注册'),
        ('error', '错误'),
        ('disabled', '已禁用'),
    ]

    device_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="设备ID"
    )
    device_identifier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="设备物理标识"
    )
    device_key = models.CharField(
        max_length=128,
        editable=False,
        verbose_name="设备密钥"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="设备名称"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name="所属项目"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unregistered',
        verbose_name="状态"
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="最后在线时间"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'device_identifier'],
                condition=models.Q(device_identifier__isnull=False),
                name='unique_device_identifier_per_project'
            )
        ]

    def save(self, *args, **kwargs):
        """重写保存方法，自动生成设备密钥"""
        # 仅在新对象创建时生成设备密钥
        if not self.device_key:
            self.device_key = get_random_string(64)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class Sensor(models.Model):
    """
    传感器模型，代表设备上的一个传感器
    """
    name = models.CharField(
        max_length=100,
        verbose_name="传感器名称"
    )
    sensor_type = models.CharField(
        max_length=50,
        verbose_name="传感器类型"
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="单位"
    )
    value_key = models.CharField(
        max_length=100,
        verbose_name="数据键名"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='sensors',
        verbose_name="所属设备"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "传感器"
        verbose_name_plural = "传感器"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'value_key'],
                name='unique_value_key_per_device'
            ),
            models.UniqueConstraint(
                fields=['device', 'name'],
                name='unique_sensor_name_per_device'
            )
        ]

    def __str__(self):
        return f"{self.device.name} - {self.name} ({self.sensor_type})"


class Actuator(models.Model):
    """
    执行器模型，代表设备上的一个执行器
    """
    name = models.CharField(
        max_length=100,
        verbose_name="执行器名称"
    )
    actuator_type = models.CharField(
        max_length=50,
        verbose_name="执行器类型"
    )
    command_key = models.CharField(
        max_length=100,
        verbose_name="命令键名"
    )
    current_state_payload = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="当前状态数据"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='actuators',
        verbose_name="所属设备"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "执行器"
        verbose_name_plural = "执行器"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'command_key'],
                name='unique_command_key_per_device'
            ),
            models.UniqueConstraint(
                fields=['device', 'name'],
                name='unique_actuator_name_per_device'
            )
        ]

    def __str__(self):
        return f"{self.device.name} - {self.name} ({self.actuator_type})"
