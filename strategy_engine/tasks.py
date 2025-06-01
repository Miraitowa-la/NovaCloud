"""
策略引擎Celery任务模块 - 用于处理基于时间的策略触发
"""

import logging
import asyncio
from celery import shared_task
from django.utils import timezone
from asgiref.sync import sync_to_async

from .models import Strategy, ExecutionLog
from .execution import trigger_strategy_execution

# 配置日志记录器
logger = logging.getLogger(__name__)

@shared_task
def check_scheduled_strategies():
    """
    检查所有基于时间触发的策略
    
    这个任务应该被设置为定期运行，如每分钟运行一次
    """
    logger.info("开始检查定时触发策略")
    
    # 使用asyncio.run运行异步主函数
    asyncio.run(_check_scheduled_strategies_async())
    
    logger.info("定时触发策略检查完成")

async def _check_scheduled_strategies_async():
    """
    异步版本的定时策略检查函数
    """
    now = timezone.localtime()
    current_time_str = f"{now.hour:02d}:{now.minute:02d}"
    current_day_of_week = now.weekday()  # 0-6表示周一到周日
    
    # 获取所有启用的、触发类型为'schedule'的策略
    strategies = await sync_to_async(list, thread_sensitive=False)(Strategy.objects.filter(
        is_enabled=True,
        trigger_type='schedule'
    ))
    
    if not strategies:
        logger.debug("没有找到定时触发策略")
        return
    
    logger.info(f"找到 {len(strategies)} 个定时触发策略")
    
    # 准备触发上下文
    trigger_context = {
        'current_time': current_time_str,
        'current_hour': now.hour,
        'current_minute': now.minute,
        'current_second': now.second,
        'current_day_of_week': current_day_of_week,
        'current_day': now.day,
        'current_month': now.month,
        'current_year': now.year,
        'timestamp': now.isoformat()
    }
    
    # 检查每个策略
    for strategy in strategies:
        try:
            # 异步触发策略执行
            await trigger_strategy_execution(strategy, trigger_context)
        except Exception as e:
            logger.error(f"检查定时策略时出错: 策略ID={strategy.id}, 错误={str(e)}")


@shared_task
def cleanup_old_execution_logs(days=30):
    """
    清理过旧的执行日志记录
    
    Args:
        days: 保留日志的天数，默认30天
    """
    try:
        # 计算截止时间
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # 删除旧的日志
        old_logs = ExecutionLog.objects.filter(triggered_at__lt=cutoff_date)
        count = old_logs.count()
        
        if count > 0:
            old_logs.delete()
            logger.info(f"已清理 {count} 条超过 {days} 天的执行日志")
        
    except Exception as e:
        logger.error(f"清理旧执行日志时出错: {str(e)}") 