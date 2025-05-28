from django.db import models
from django.contrib.auth.models import User
from iot_devices.models import Project, Sensor, Actuator


class Strategy(models.Model):
    """
    策略模型，定义自动化策略的基本信息
    """
    TRIGGER_TYPE_CHOICES = [
        ('sensor_data', '传感器数据'),
        ('schedule', '定时触发'),
        ('device_status', '设备状态变化'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="策略名称"
    )
    description = models.TextField(
        blank=True,
        verbose_name="策略描述"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name="所有者"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name="所属项目"
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name="是否启用"
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=TRIGGER_TYPE_CHOICES,
        verbose_name="触发类型"
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
        verbose_name = "策略"
        verbose_name_plural = "策略"
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class ConditionGroup(models.Model):
    """
    条件组模型，将多个条件组合在一起，使用同一个逻辑运算符
    """
    LOGICAL_OPERATOR_CHOICES = [
        ('AND', '所有条件必须满足(AND)'),
        ('OR', '任一条件满足即可(OR)'),
    ]

    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='condition_groups',
        verbose_name="所属策略"
    )
    logical_operator = models.CharField(
        max_length=3,
        choices=LOGICAL_OPERATOR_CHOICES,
        default='AND',
        verbose_name="逻辑运算符"
    )
    execution_order = models.PositiveIntegerField(
        default=0,
        verbose_name="执行顺序"
    )

    class Meta:
        verbose_name = "条件组"
        verbose_name_plural = "条件组"
        ordering = ['execution_order']

    def __str__(self):
        return f"条件组 {self.id} - {self.strategy.name} ({self.get_logical_operator_display()})"


class Condition(models.Model):
    """
    条件模型，定义策略触发的具体条件
    """
    DATA_SOURCE_TYPE_CHOICES = [
        ('sensor', '传感器值'),
        ('device_attribute', '设备属性'),
        ('time_of_day', '一天中的时间'),
        ('specific_time', '特定日期时间'),
    ]

    OPERATOR_CHOICES = [
        ('>', '大于'),
        ('<', '小于'),
        ('==', '等于'),
        ('!=', '不等于'),
        ('>=', '大于等于'),
        ('<=', '小于等于'),
        ('contains', '包含(字符串)'),
        ('not_contains', '不包含(字符串)'),
    ]

    THRESHOLD_VALUE_TYPE_CHOICES = [
        ('static', '静态值'),
        ('sensor_value', '另一个传感器的值'),
        ('device_attribute_value', '另一个设备属性'),
    ]

    group = models.ForeignKey(
        ConditionGroup,
        on_delete=models.CASCADE,
        related_name='conditions',
        verbose_name="所属条件组"
    )
    data_source_type = models.CharField(
        max_length=30,
        choices=DATA_SOURCE_TYPE_CHOICES,
        verbose_name="数据源类型"
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='conditions',
        verbose_name="传感器"
    )
    device_attribute = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="设备属性"
    )
    operator = models.CharField(
        max_length=20,
        choices=OPERATOR_CHOICES,
        verbose_name="比较运算符"
    )
    threshold_value_type = models.CharField(
        max_length=30,
        choices=THRESHOLD_VALUE_TYPE_CHOICES,
        default='static',
        verbose_name="阈值类型"
    )
    threshold_value_static = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="静态阈值"
    )
    threshold_value_sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='threshold_conditions',
        verbose_name="阈值来源传感器"
    )
    threshold_value_device_attribute = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="阈值来源设备属性"
    )

    class Meta:
        verbose_name = "条件"
        verbose_name_plural = "条件"

    def __str__(self):
        source_desc = ""
        if self.data_source_type == 'sensor' and self.sensor:
            source_desc = f"传感器 {self.sensor.name}"
        elif self.data_source_type == 'device_attribute':
            source_desc = f"设备属性 {self.device_attribute}"
        elif self.data_source_type == 'time_of_day':
            source_desc = "一天中的时间"
        elif self.data_source_type == 'specific_time':
            source_desc = "特定日期时间"

        threshold_desc = ""
        if self.threshold_value_type == 'static':
            threshold_desc = self.threshold_value_static or "未设置"
        elif self.threshold_value_type == 'sensor_value' and self.threshold_value_sensor:
            threshold_desc = f"传感器 {self.threshold_value_sensor.name} 的值"
        elif self.threshold_value_type == 'device_attribute_value':
            threshold_desc = f"设备属性 {self.threshold_value_device_attribute} 的值"

        return f"{source_desc} {self.get_operator_display()} {threshold_desc}"


class Action(models.Model):
    """
    动作模型，定义策略触发后要执行的操作
    """
    ACTION_TYPE_CHOICES = [
        ('control_actuator', '控制执行器'),
        ('send_notification', '发送通知'),
        ('call_webhook', '调用Webhook'),
    ]

    NOTIFICATION_RECIPIENT_TYPE_CHOICES = [
        ('user_email', '所有者邮箱'),
        ('specific_email', '指定邮箱'),
        ('platform_message', '平台消息'),
    ]

    WEBHOOK_METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
    ]

    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='actions',
        verbose_name="所属策略"
    )
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPE_CHOICES,
        verbose_name="动作类型"
    )
    execution_order = models.PositiveIntegerField(
        default=0,
        verbose_name="执行顺序"
    )
    target_actuator = models.ForeignKey(
        Actuator,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='strategy_actions',
        verbose_name="目标执行器"
    )
    command_payload_template = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="命令内容模板"
    )
    notification_recipient_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_RECIPIENT_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="通知接收者类型"
    )
    notification_recipient_value = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="通知接收者值"
    )
    notification_message_template = models.TextField(
        null=True,
        blank=True,
        verbose_name="通知消息模板"
    )
    webhook_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Webhook URL"
    )
    webhook_method = models.CharField(
        max_length=10,
        choices=WEBHOOK_METHOD_CHOICES,
        null=True,
        blank=True,
        verbose_name="Webhook方法"
    )
    webhook_headers_template = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="Webhook请求头模板"
    )
    webhook_payload_template = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="Webhook内容模板"
    )

    class Meta:
        verbose_name = "动作"
        verbose_name_plural = "动作"
        ordering = ['execution_order']

    def __str__(self):
        action_desc = self.get_action_type_display()
        details = ""
        if self.action_type == 'control_actuator' and self.target_actuator:
            details = f"控制 {self.target_actuator.name}"
        elif self.action_type == 'send_notification':
            recipient_type = self.get_notification_recipient_type_display() if self.notification_recipient_type else "未设置"
            details = f"发送到 {recipient_type}"
        elif self.action_type == 'call_webhook' and self.webhook_url:
            details = f"调用 {self.webhook_url}"

        return f"{self.strategy.name} - {action_desc} - {details}"


class ExecutionLog(models.Model):
    """
    执行日志模型，记录策略执行的历史和结果
    """
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('partial_success', '部分成功'),
    ]

    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.SET_NULL,
        null=True,
        related_name='execution_logs',
        verbose_name="策略"
    )
    triggered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="触发时间"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="状态"
    )
    trigger_details = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        verbose_name="触发详情"
    )
    action_results = models.JSONField(
        default=list,
        null=True,
        blank=True,
        verbose_name="动作执行结果"
    )

    class Meta:
        verbose_name = "执行日志"
        verbose_name_plural = "执行日志"
        ordering = ['-triggered_at']

    def __str__(self):
        strategy_name = self.strategy.name if self.strategy else "已删除的策略"
        return f"日志 - {strategy_name} - {self.triggered_at} - {self.get_status_display()}"
