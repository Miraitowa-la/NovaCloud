# Generated by Django 5.2.1 on 2025-05-28 03:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('iot_devices', '0002_actuatorcommandlog_sensordata'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConditionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logical_operator', models.CharField(choices=[('AND', '所有条件必须满足(AND)'), ('OR', '任一条件满足即可(OR)')], default='AND', max_length=3, verbose_name='逻辑运算符')),
                ('execution_order', models.PositiveIntegerField(default=0, verbose_name='执行顺序')),
            ],
            options={
                'verbose_name': '条件组',
                'verbose_name_plural': '条件组',
                'ordering': ['execution_order'],
            },
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_source_type', models.CharField(choices=[('sensor', '传感器值'), ('device_attribute', '设备属性'), ('time_of_day', '一天中的时间'), ('specific_time', '特定日期时间')], max_length=30, verbose_name='数据源类型')),
                ('device_attribute', models.CharField(blank=True, max_length=50, null=True, verbose_name='设备属性')),
                ('operator', models.CharField(choices=[('>', '大于'), ('<', '小于'), ('==', '等于'), ('!=', '不等于'), ('>=', '大于等于'), ('<=', '小于等于'), ('contains', '包含(字符串)'), ('not_contains', '不包含(字符串)')], max_length=20, verbose_name='比较运算符')),
                ('threshold_value_type', models.CharField(choices=[('static', '静态值'), ('sensor_value', '另一个传感器的值'), ('device_attribute_value', '另一个设备属性')], default='static', max_length=30, verbose_name='阈值类型')),
                ('threshold_value_static', models.CharField(blank=True, max_length=255, null=True, verbose_name='静态阈值')),
                ('threshold_value_device_attribute', models.CharField(blank=True, max_length=50, null=True, verbose_name='阈值来源设备属性')),
                ('sensor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='iot_devices.sensor', verbose_name='传感器')),
                ('threshold_value_sensor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='threshold_conditions', to='iot_devices.sensor', verbose_name='阈值来源传感器')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions', to='strategy_engine.conditiongroup', verbose_name='所属条件组')),
            ],
            options={
                'verbose_name': '条件',
                'verbose_name_plural': '条件',
            },
        ),
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='策略名称')),
                ('description', models.TextField(blank=True, verbose_name='策略描述')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='是否启用')),
                ('trigger_type', models.CharField(choices=[('sensor_data', '传感器数据'), ('schedule', '定时触发'), ('device_status', '设备状态变化')], max_length=50, verbose_name='触发类型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strategies', to=settings.AUTH_USER_MODEL, verbose_name='所有者')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strategies', to='iot_devices.project', verbose_name='所属项目')),
            ],
            options={
                'verbose_name': '策略',
                'verbose_name_plural': '策略',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ExecutionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('triggered_at', models.DateTimeField(auto_now_add=True, verbose_name='触发时间')),
                ('status', models.CharField(choices=[('pending', '等待中'), ('success', '成功'), ('failed', '失败'), ('partial_success', '部分成功')], default='pending', max_length=20, verbose_name='状态')),
                ('trigger_details', models.JSONField(blank=True, default=dict, null=True, verbose_name='触发详情')),
                ('action_results', models.JSONField(blank=True, default=list, null=True, verbose_name='动作执行结果')),
                ('strategy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='execution_logs', to='strategy_engine.strategy', verbose_name='策略')),
            ],
            options={
                'verbose_name': '执行日志',
                'verbose_name_plural': '执行日志',
                'ordering': ['-triggered_at'],
            },
        ),
        migrations.AddField(
            model_name='conditiongroup',
            name='strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='condition_groups', to='strategy_engine.strategy', verbose_name='所属策略'),
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('control_actuator', '控制执行器'), ('send_notification', '发送通知'), ('call_webhook', '调用Webhook')], max_length=30, verbose_name='动作类型')),
                ('execution_order', models.PositiveIntegerField(default=0, verbose_name='执行顺序')),
                ('command_payload_template', models.JSONField(blank=True, default=dict, null=True, verbose_name='命令内容模板')),
                ('notification_recipient_type', models.CharField(blank=True, choices=[('user_email', '所有者邮箱'), ('specific_email', '指定邮箱'), ('platform_message', '平台消息')], max_length=30, null=True, verbose_name='通知接收者类型')),
                ('notification_recipient_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='通知接收者值')),
                ('notification_message_template', models.TextField(blank=True, null=True, verbose_name='通知消息模板')),
                ('webhook_url', models.URLField(blank=True, null=True, verbose_name='Webhook URL')),
                ('webhook_method', models.CharField(blank=True, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT')], max_length=10, null=True, verbose_name='Webhook方法')),
                ('webhook_headers_template', models.JSONField(blank=True, default=dict, null=True, verbose_name='Webhook请求头模板')),
                ('webhook_payload_template', models.JSONField(blank=True, default=dict, null=True, verbose_name='Webhook内容模板')),
                ('target_actuator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='strategy_actions', to='iot_devices.actuator', verbose_name='目标执行器')),
                ('strategy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='strategy_engine.strategy', verbose_name='所属策略')),
            ],
            options={
                'verbose_name': '动作',
                'verbose_name_plural': '动作',
                'ordering': ['execution_order'],
            },
        ),
    ]
