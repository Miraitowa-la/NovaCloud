"""
策略执行服务模块 - 包含策略条件评估和动作执行的核心逻辑
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Union, Optional
from datetime import datetime

from django.utils import timezone
import httpx

from .models import Strategy, ConditionGroup, Condition, Action, ExecutionLog
from iot_devices.models import Device, Sensor, Actuator, SensorData, ActuatorCommandLog

# 配置日志记录器
logger = logging.getLogger(__name__)

# ============= 条件评估函数 =============

def evaluate_condition(condition: Condition, trigger_context: Dict[str, Any]) -> bool:
    """
    评估单个条件是否满足
    
    Args:
        condition: 要评估的条件对象
        trigger_context: 触发上下文，包含触发事件的相关数据
        
    Returns:
        bool: 条件是否满足
    """
    logger.debug(f"评估条件: {condition.id}, 数据源类型: {condition.data_source_type}")
    
    # 获取实际值
    actual_value = None
    
    # 根据数据源类型获取实际值
    if condition.data_source_type == 'sensor':
        # 如果条件的传感器就是触发者，直接使用触发上下文中的值
        if trigger_context.get('sensor_id') == condition.sensor_id:
            actual_value = trigger_context.get('value')
            logger.debug(f"从触发上下文获取传感器值: {actual_value}")
        # 否则查询数据库获取最新值
        elif condition.sensor_id:
            try:
                latest_data = SensorData.objects.filter(
                    sensor_id=condition.sensor_id
                ).order_by('-timestamp').first()
                
                if latest_data:
                    actual_value = latest_data.get_value()
                    logger.debug(f"从数据库获取传感器值: {actual_value}")
                else:
                    logger.warning(f"找不到传感器 {condition.sensor_id} 的数据")
                    return False
            except Exception as e:
                logger.error(f"获取传感器数据时出错: {str(e)}")
                return False
        else:
            logger.warning("条件中缺少传感器ID")
            return False
            
    elif condition.data_source_type == 'device_attribute':
        # 从触发上下文中获取设备ID
        device_id = None
        if 'device_id' in trigger_context:
            device_id = trigger_context['device_id']
        elif 'sensor_id' in trigger_context:
            try:
                sensor = Sensor.objects.get(id=trigger_context['sensor_id'])
                device_id = sensor.device_id
            except Sensor.DoesNotExist:
                logger.warning(f"找不到传感器 {trigger_context['sensor_id']}")
                return False
                
        if device_id:
            try:
                device = Device.objects.get(id=device_id)
                # 获取设备的指定属性
                attribute = condition.device_attribute
                if hasattr(device, attribute):
                    actual_value = getattr(device, attribute)
                    logger.debug(f"设备属性 {attribute} 的值: {actual_value}")
                else:
                    logger.warning(f"设备没有属性: {attribute}")
                    return False
            except Device.DoesNotExist:
                logger.warning(f"找不到设备 {device_id}")
                return False
        else:
            logger.warning("无法确定要检查的设备")
            return False
            
    elif condition.data_source_type == 'time_of_day':
        # 获取当前时间
        now = timezone.localtime()
        # 格式为"HH:MM"
        actual_value = f"{now.hour:02d}:{now.minute:02d}"
        logger.debug(f"当前时间: {actual_value}")
        
    elif condition.data_source_type == 'specific_time':
        # 当前时间戳
        now = timezone.now()
        actual_value = now.timestamp()
        logger.debug(f"当前时间戳: {actual_value}")
    
    else:
        logger.warning(f"不支持的数据源类型: {condition.data_source_type}")
        return False
    
    # 获取阈值
    threshold_value = None
    
    if condition.threshold_value_type == 'static':
        threshold_value = condition.threshold_value_static
        logger.debug(f"静态阈值: {threshold_value}")
        
    elif condition.threshold_value_type == 'sensor_value':
        if condition.threshold_value_sensor_id:
            try:
                latest_data = SensorData.objects.filter(
                    sensor_id=condition.threshold_value_sensor_id
                ).order_by('-timestamp').first()
                
                if latest_data:
                    threshold_value = latest_data.get_value()
                    logger.debug(f"从传感器获取阈值: {threshold_value}")
                else:
                    logger.warning(f"找不到阈值传感器 {condition.threshold_value_sensor_id} 的数据")
                    return False
            except Exception as e:
                logger.error(f"获取阈值传感器数据时出错: {str(e)}")
                return False
        else:
            logger.warning("条件中缺少阈值传感器ID")
            return False
            
    elif condition.threshold_value_type == 'device_attribute_value':
        # 类似于device_attribute数据源，但用于阈值
        try:
            # 假设condition中存储了设备ID和属性名
            device_id = condition.threshold_value_device_id
            attribute = condition.threshold_value_device_attribute
            
            if device_id and attribute:
                device = Device.objects.get(id=device_id)
                if hasattr(device, attribute):
                    threshold_value = getattr(device, attribute)
                    logger.debug(f"从设备属性获取阈值: {threshold_value}")
                else:
                    logger.warning(f"设备没有属性: {attribute}")
                    return False
            else:
                logger.warning("条件中缺少阈值设备ID或属性名")
                return False
        except Device.DoesNotExist:
            logger.warning(f"找不到阈值设备 {device_id}")
            return False
        except Exception as e:
            logger.error(f"获取阈值设备属性时出错: {str(e)}")
            return False
    
    else:
        logger.warning(f"不支持的阈值类型: {condition.threshold_value_type}")
        return False
    
    # 确保实际值和阈值类型匹配
    try:
        # 对于数值比较，尝试将两者都转换为浮点数
        if condition.operator in ['eq', 'neq', 'gt', 'gte', 'lt', 'lte']:
            if not isinstance(actual_value, (int, float)) and actual_value is not None:
                try:
                    actual_value = float(actual_value)
                except (ValueError, TypeError):
                    # 不是数值，保持原样
                    pass
                    
            if not isinstance(threshold_value, (int, float)) and threshold_value is not None:
                try:
                    threshold_value = float(threshold_value)
                except (ValueError, TypeError):
                    # 不是数值，保持原样
                    pass
    except Exception as e:
        logger.error(f"转换值类型时出错: {str(e)}")
        # 继续处理，使用原始类型
    
    # 使用运算符比较实际值和阈值
    result = False
    
    try:
        if condition.operator == 'eq':  # 等于
            result = actual_value == threshold_value
        elif condition.operator == 'neq':  # 不等于
            result = actual_value != threshold_value
        elif condition.operator == 'gt':  # 大于
            result = actual_value > threshold_value
        elif condition.operator == 'gte':  # 大于等于
            result = actual_value >= threshold_value
        elif condition.operator == 'lt':  # 小于
            result = actual_value < threshold_value
        elif condition.operator == 'lte':  # 小于等于
            result = actual_value <= threshold_value
        elif condition.operator == 'contains':  # 包含
            result = str(threshold_value) in str(actual_value)
        elif condition.operator == 'not_contains':  # 不包含
            result = str(threshold_value) not in str(actual_value)
        elif condition.operator == 'starts_with':  # 以...开头
            result = str(actual_value).startswith(str(threshold_value))
        elif condition.operator == 'ends_with':  # 以...结尾
            result = str(actual_value).endswith(str(threshold_value))
        else:
            logger.warning(f"不支持的运算符: {condition.operator}")
            result = False
    except Exception as e:
        logger.error(f"比较值时出错: {str(e)}, 实际值: {actual_value}({type(actual_value)}), 阈值: {threshold_value}({type(threshold_value)})")
        result = False
    
    logger.debug(f"条件评估结果: {result}, 实际值: {actual_value}, 运算符: {condition.operator}, 阈值: {threshold_value}")
    return result


def evaluate_condition_group(condition_group: ConditionGroup, trigger_context: Dict[str, Any]) -> bool:
    """
    评估条件组是否满足
    
    Args:
        condition_group: 要评估的条件组对象
        trigger_context: 触发上下文，包含触发事件的相关数据
        
    Returns:
        bool: 条件组是否满足
    """
    logger.debug(f"评估条件组: {condition_group.id}, 逻辑运算符: {condition_group.logical_operator}")
    
    # 获取条件组中的所有条件
    conditions = condition_group.conditions.all()
    
    # 如果没有条件，默认为True
    if not conditions:
        logger.debug("条件组没有条件，默认结果为True")
        return True
    
    # 初始化结果（对于AND初始为True，对于OR初始为False）
    if condition_group.logical_operator == 'AND':
        result = True
    else:  # 'OR'
        result = False
    
    # 评估每个条件
    for condition in conditions:
        condition_result = evaluate_condition(condition, trigger_context)
        
        # 根据逻辑运算符组合结果
        if condition_group.logical_operator == 'AND':
            result = result and condition_result
            # 短路逻辑：如果已经为False，不需要继续评估
            if not result:
                logger.debug("AND逻辑中有条件不满足，短路返回False")
                return False
        else:  # 'OR'
            result = result or condition_result
            # 短路逻辑：如果已经为True，不需要继续评估
            if result:
                logger.debug("OR逻辑中有条件满足，短路返回True")
                return True
    
    logger.debug(f"条件组评估最终结果: {result}")
    return result


def check_strategy_conditions(strategy: Strategy, trigger_context: Dict[str, Any]) -> bool:
    """
    检查策略的所有条件组是否满足
    
    Args:
        strategy: 要检查的策略对象
        trigger_context: 触发上下文，包含触发事件的相关数据
        
    Returns:
        bool: 策略条件是否满足
    """
    logger.info(f"检查策略条件: 策略ID={strategy.id}, 名称='{strategy.name}'")
    
    # 获取策略的所有条件组，按执行顺序排序
    condition_groups = strategy.condition_groups.all().order_by('execution_order')
    
    # 如果没有条件组，默认为True
    if not condition_groups:
        logger.info("策略没有条件组，默认结果为True")
        return True
    
    # 评估每个条件组（目前假设所有条件组之间是AND关系）
    for condition_group in condition_groups:
        if not evaluate_condition_group(condition_group, trigger_context):
            logger.info(f"策略条件不满足: 条件组ID={condition_group.id}评估结果为False")
            return False
    
    logger.info("策略所有条件组都满足")
    return True


# ============= 动作执行函数 =============

# 占位函数，后续与TCP服务器集成
async def send_command_to_tcp_server(actuator_id: int, command_payload: dict) -> dict:
    """
    将命令发送到TCP服务器的占位函数
    
    Args:
        actuator_id: 执行器ID
        command_payload: 命令内容
        
    Returns:
        dict: 响应结果
    """
    logger.info(f"向TCP服务器发送命令: 执行器ID={actuator_id}, 命令={command_payload}")
    # TODO: 实现与TCP服务器的实际集成
    # 占位实现，假设成功
    return {"status": "success", "message": "命令已发送"}


def render_template(template_str: str, context: Dict[str, Any]) -> str:
    """
    使用上下文数据渲染模板字符串
    
    Args:
        template_str: 模板字符串
        context: 上下文数据
        
    Returns:
        str: 渲染后的字符串
    """
    if not template_str:
        return ""
        
    # 一个简单的模板渲染实现，替换{{变量}}
    result = template_str
    for key, value in context.items():
        placeholder = '{{' + key + '}}'
        result = result.replace(placeholder, str(value))
    
    return result


async def execute_strategy_actions(strategy: Strategy, trigger_context: Dict[str, Any], execution_log: ExecutionLog) -> None:
    """
    执行策略定义的所有动作
    
    Args:
        strategy: 策略对象
        trigger_context: 触发上下文
        execution_log: 执行日志记录
    """
    logger.info(f"执行策略动作: 策略ID={strategy.id}, 名称='{strategy.name}'")
    
    # 更新执行日志状态为处理中
    execution_log.status = 'processing'
    execution_log.save(update_fields=['status'])
    
    # 初始化动作结果列表
    action_results = []
    
    # 获取策略的所有动作，按执行顺序排序
    actions = strategy.actions.all().order_by('execution_order')
    
    # 标记是否有任何动作执行失败
    has_failures = False
    
    # 执行每个动作
    for action in actions:
        # 记录动作开始执行
        action_start_time = timezone.now()
        action_result = {
            "action_id": action.id,
            "action_type": action.action_type,
            "start_time": action_start_time.isoformat(),
            "status": "pending"
        }
        
        try:
            # 根据动作类型执行不同操作
            if action.action_type == 'control_actuator':
                # 控制执行器
                if not action.target_actuator_id:
                    raise ValueError("缺少目标执行器ID")
                
                # 获取执行器
                try:
                    actuator = Actuator.objects.get(id=action.target_actuator_id)
                except Actuator.DoesNotExist:
                    raise ValueError(f"找不到执行器: ID={action.target_actuator_id}")
                
                # 准备模板上下文，包含更多信息
                template_context = {**trigger_context}
                if 'sensor_id' in trigger_context:
                    try:
                        sensor = Sensor.objects.get(id=trigger_context['sensor_id'])
                        template_context['sensor'] = {
                            'id': sensor.id,
                            'name': sensor.name,
                            'type': sensor.sensor_type,
                            'value': trigger_context.get('value', None)
                        }
                    except Sensor.DoesNotExist:
                        pass
                
                # 添加策略信息
                template_context['strategy'] = {
                    'id': strategy.id,
                    'name': strategy.name
                }
                
                # 添加执行器信息
                template_context['actuator'] = {
                    'id': actuator.id,
                    'name': actuator.name,
                    'type': actuator.actuator_type
                }
                
                # 渲染命令模板
                try:
                    command_json_str = render_template(action.command_payload_template, template_context)
                    command_payload = json.loads(command_json_str)
                except json.JSONDecodeError:
                    raise ValueError(f"无效的命令JSON格式: {command_json_str}")
                
                # 创建执行器命令日志
                command_log = ActuatorCommandLog.objects.create(
                    actuator=actuator,
                    user=strategy.owner,  # 使用策略所有者作为用户
                    command_payload=command_payload,
                    status='pending',
                    source=f'strategy:{strategy.id}'
                )
                
                # 发送命令到TCP服务器
                response = await send_command_to_tcp_server(actuator.id, command_payload)
                
                # 更新命令日志
                command_log.status = 'sent' if response.get('status') == 'success' else 'failed'
                command_log.response_payload = response
                command_log.save(update_fields=['status', 'response_payload'])
                
                # 记录动作结果
                action_result.update({
                    "status": "success" if response.get('status') == 'success' else "failed",
                    "details": {
                        "actuator_id": actuator.id,
                        "actuator_name": actuator.name,
                        "command": command_payload,
                        "response": response,
                        "command_log_id": command_log.id
                    }
                })
                
            elif action.action_type == 'send_notification':
                # 发送通知
                recipient_type = action.notification_recipient_type
                recipient_value = action.notification_recipient_value
                
                if not recipient_value:
                    raise ValueError("缺少通知接收者")
                
                # 准备模板上下文，类似于控制执行器
                template_context = {**trigger_context}
                # 添加传感器、策略等信息，与控制执行器相同
                
                # 渲染通知内容
                message = render_template(action.notification_message_template, template_context)
                
                # 根据接收者类型发送通知
                if recipient_type == 'email':
                    # 发送邮件通知
                    logger.info(f"发送邮件通知: 接收者={recipient_value}, 内容={message}")
                    # TODO: 实现邮件发送逻辑
                    # 占位实现
                    # from django.core.mail import send_mail
                    # send_mail(
                    #     subject=f"NovaCloud策略通知: {strategy.name}",
                    #     message=message,
                    #     from_email="noreply@example.com",
                    #     recipient_list=[recipient_value],
                    #     fail_silently=False,
                    # )
                    
                    # 记录动作结果
                    action_result.update({
                        "status": "success",
                        "details": {
                            "recipient_type": recipient_type,
                            "recipient": recipient_value,
                            "message": message
                        }
                    })
                
                elif recipient_type == 'sms':
                    # 发送短信通知
                    logger.info(f"发送短信通知: 接收者={recipient_value}, 内容={message}")
                    # TODO: 实现短信发送逻辑
                    # 占位实现
                    
                    # 记录动作结果
                    action_result.update({
                        "status": "success",
                        "details": {
                            "recipient_type": recipient_type,
                            "recipient": recipient_value,
                            "message": message
                        }
                    })
                
                else:
                    raise ValueError(f"不支持的通知接收者类型: {recipient_type}")
            
            elif action.action_type == 'call_webhook':
                # 调用Webhook
                if not action.webhook_url:
                    raise ValueError("缺少Webhook URL")
                
                # 准备模板上下文，类似于其他动作
                template_context = {**trigger_context}
                # 添加传感器、策略等信息
                
                # 渲染URL、请求头和请求体
                url = render_template(action.webhook_url, template_context)
                method = action.webhook_method or 'POST'
                
                # 处理请求头
                headers = {}
                if action.webhook_headers_template:
                    try:
                        headers_json_str = render_template(action.webhook_headers_template, template_context)
                        headers = json.loads(headers_json_str)
                    except json.JSONDecodeError:
                        raise ValueError(f"无效的请求头JSON格式: {headers_json_str}")
                
                # 处理请求体
                payload = None
                if action.webhook_payload_template:
                    try:
                        payload_json_str = render_template(action.webhook_payload_template, template_context)
                        payload = json.loads(payload_json_str)
                    except json.JSONDecodeError:
                        raise ValueError(f"无效的请求体JSON格式: {payload_json_str}")
                
                # 发送HTTP请求
                logger.info(f"调用Webhook: URL={url}, 方法={method}")
                
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        if method.upper() == 'GET':
                            response = await client.get(url, headers=headers, params=payload or {})
                        elif method.upper() == 'POST':
                            response = await client.post(url, headers=headers, json=payload)
                        elif method.upper() == 'PUT':
                            response = await client.put(url, headers=headers, json=payload)
                        elif method.upper() == 'DELETE':
                            response = await client.delete(url, headers=headers, json=payload)
                        else:
                            raise ValueError(f"不支持的HTTP方法: {method}")
                        
                        # 检查响应
                        response.raise_for_status()
                        
                        # 记录动作结果
                        action_result.update({
                            "status": "success",
                            "details": {
                                "url": url,
                                "method": method,
                                "status_code": response.status_code,
                                "response": response.text[:1000]  # 限制响应长度
                            }
                        })
                except Exception as e:
                    raise ValueError(f"Webhook请求失败: {str(e)}")
            
            else:
                raise ValueError(f"不支持的动作类型: {action.action_type}")
                
        except Exception as e:
            # 记录失败的动作结果
            logger.error(f"执行动作失败: {str(e)}")
            action_result.update({
                "status": "failed",
                "error": str(e)
            })
            has_failures = True
        
        # 记录动作结束时间
        action_result["end_time"] = timezone.now().isoformat()
        
        # 添加到结果列表
        action_results.append(action_result)
    
    # 更新执行日志
    if not actions:
        # 没有动作，标记为成功
        execution_log.status = 'success'
    elif has_failures:
        # 有失败的动作
        if any(result["status"] == "success" for result in action_results):
            # 部分成功
            execution_log.status = 'partial_success'
        else:
            # 全部失败
            execution_log.status = 'failed'
    else:
        # 全部成功
        execution_log.status = 'success'
    
    # 保存动作结果
    execution_log.action_results = action_results
    execution_log.save(update_fields=['status', 'action_results'])
    
    logger.info(f"策略动作执行完成: 策略ID={strategy.id}, 状态={execution_log.status}")


# ============= 策略触发函数 =============

async def trigger_strategy_execution(strategy: Strategy, trigger_context: Dict[str, Any]) -> Optional[ExecutionLog]:
    """
    触发策略执行
    
    Args:
        strategy: 要执行的策略
        trigger_context: 触发上下文
        
    Returns:
        ExecutionLog: 创建的执行日志记录，如果条件不满足则返回None
    """
    logger.info(f"触发策略执行: 策略ID={strategy.id}, 名称='{strategy.name}'")
    
    # 首先检查策略是否启用
    if not strategy.is_enabled:
        logger.info(f"策略未启用，跳过执行: 策略ID={strategy.id}")
        return None
    
    # 检查策略条件
    if not check_strategy_conditions(strategy, trigger_context):
        logger.info(f"策略条件不满足，跳过执行: 策略ID={strategy.id}")
        return None
    
    # 创建执行日志
    execution_log = ExecutionLog.objects.create(
        strategy=strategy,
        triggered_at=timezone.now(),
        status='pending',
        trigger_details=trigger_context
    )
    
    # 异步执行策略动作
    # 注意：在Django环境中，可能需要调整异步执行方式
    asyncio.create_task(execute_strategy_actions(strategy, trigger_context, execution_log))
    
    return execution_log 