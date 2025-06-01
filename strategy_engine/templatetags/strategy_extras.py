from django import template
import json

register = template.Library()

@register.filter
def pprint_json(value):
    """
    将JSON数据美化输出，用于策略执行日志中的JSON字段显示
    
    示例用法：{{ log.trigger_details|pprint_json }}
    """
    try:
        # 如果value已经是字符串，尝试解析为JSON对象
        if isinstance(value, str):
            parsed = json.loads(value)
        else:
            parsed = value
        
        # 将JSON对象转换为格式化的字符串
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (ValueError, TypeError):
        # 如果无法解析为JSON，直接返回原始值
        return str(value) 