"""
策略引擎信号处理模块 - 用于监听SensorData创建和Device状态变化
"""

import asyncio
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils import timezone

from iot_devices.models import SensorData, Device, Sensor
from .models import Strategy
from .execution import trigger_strategy_execution

# 配置日志记录器
logger = logging.getLogger(__name__)

@receiver(post_save, sender=SensorData)
def handle_sensor_data_created(sender, instance, created, **kwargs):
    """
    当新的传感器数据被创建时，触发相关策略
    
    Args:
        sender: 发送信号的模型类
        instance: 保存的SensorData实例
        created: 是否是新创建的实例
    """
    if not created:
        # 只处理新创建的数据
        return
    
    logger.info(f"传感器数据创建: 传感器ID={instance.sensor_id}, 值={instance.get_value()}")
    
    # 查找所有引用此传感器且触发类型为sensor_data的启用策略
    try:
        # 获取传感器的项目ID，用于过滤策略
        sensor = instance.sensor
        project_id = sensor.device.project_id
        
        # 查找可能的策略
        # 注意: 此处的查询是简化的，实际可能需要更复杂的查询
        # 来找到在条件中引用了该传感器的策略
        strategies = Strategy.objects.filter(
            is_enabled=True,
            trigger_type='sensor_data',
            project_id=project_id
        ).distinct()
        
        if not strategies:
            logger.debug(f"未找到与传感器ID={instance.sensor_id}相关的策略")
            return
            
        # 准备触发上下文
        trigger_context = {
            'sensor_id': instance.sensor_id,
            'value': instance.get_value(),
            'timestamp': instance.timestamp.isoformat() if instance.timestamp else timezone.now().isoformat(),
            'sensor_type': sensor.sensor_type,
            'unit': sensor.unit,
            'device_id': sensor.device_id,
            'device_name': sensor.device.name,
            'project_id': project_id
        }
        
        # 对每个策略检查条件并执行
        for strategy in strategies:
            # 注意: 这里使用asyncio.run()在同步环境中运行异步函数
            # 在生产环境中可能需要更复杂的处理方式
            try:
                asyncio.run(trigger_strategy_execution(strategy, trigger_context))
            except Exception as e:
                logger.error(f"执行策略时出错: 策略ID={strategy.id}, 错误={str(e)}")
        
    except Exception as e:
        logger.error(f"处理传感器数据触发时出错: {str(e)}")


@receiver(pre_save, sender=Device)
def handle_device_status_changed(sender, instance, **kwargs):
    """
    当设备状态变化时，触发相关策略
    
    Args:
        sender: 发送信号的模型类
        instance: 要保存的Device实例
    """
    # 检查是否已存在于数据库中
    if not instance.pk:
        # 新设备，无需检查状态变化
        return
    
    try:
        # 获取旧的状态
        old_instance = Device.objects.get(pk=instance.pk)
        old_status = old_instance.status
        
        # 检查状态是否变化
        if instance.status != old_status:
            logger.info(f"设备状态变化: 设备ID={instance.id}, 旧状态={old_status}, 新状态={instance.status}")
            
            # 查找所有与此设备相关且触发类型为device_status的启用策略
            strategies = Strategy.objects.filter(
                is_enabled=True,
                trigger_type='device_status',
                project_id=instance.project_id
            ).distinct()
            
            if not strategies:
                logger.debug(f"未找到与设备ID={instance.id}相关的策略")
                return
            
            # 准备触发上下文
            trigger_context = {
                'device_id': instance.id,
                'device_name': instance.name,
                'old_status': old_status,
                'new_status': instance.status,
                'project_id': instance.project_id,
                'timestamp': timezone.now().isoformat()
            }
            
            # 对每个策略检查条件并执行
            for strategy in strategies:
                try:
                    asyncio.run(trigger_strategy_execution(strategy, trigger_context))
                except Exception as e:
                    logger.error(f"执行策略时出错: 策略ID={strategy.id}, 错误={str(e)}")
    
    except Device.DoesNotExist:
        # 新设备，无需检查状态变化
        pass
    except Exception as e:
        logger.error(f"处理设备状态变化触发时出错: {str(e)}") 