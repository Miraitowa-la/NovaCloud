from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    获取字典中的项目，用于在模板中访问字典值
    用法：{{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key) 