from django import forms
from .models import Strategy
from iot_devices.models import Project, Sensor, Actuator

class StrategyForm(forms.ModelForm):
    """
    策略表单，用于创建和编辑策略
    """
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 确保用户只能选择自己的项目
        if user:
            self.fields['project'].queryset = Project.objects.filter(owner=user)
        
        # 为所有字段添加样式类和占位符
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：客厅温度过高时自动开空调'
        })
        
        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '详细描述此策略的功能和目的'
        })
        
        self.fields['project'].widget.attrs.update({
            'class': 'form-control'
        })
        
        self.fields['trigger_type'].widget = forms.Select(
            choices=Strategy.TRIGGER_TYPE_CHOICES,
            attrs={'class': 'form-control'}
        )
        
        self.fields['is_enabled'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
    
    class Meta:
        model = Strategy
        fields = ('name', 'description', 'project', 'trigger_type', 'is_enabled')
        # owner 字段将在视图中设置

# 新增表单类和表单集

from .models import ConditionGroup, Condition, Action
from django.forms.models import BaseInlineFormSet, inlineformset_factory

class ConditionGroupForm(forms.ModelForm):
    """条件组表单，用于创建和管理条件组"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 添加样式
        self.fields['logical_operator'].widget.attrs.update({
            'class': 'form-control'
        })
        
        self.fields['execution_order'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number',
            'min': '1',
            'step': '1'
        })
    
    class Meta:
        model = ConditionGroup
        fields = ('logical_operator', 'execution_order')
        # strategy 字段将通过表单集或视图设置


class ConditionForm(forms.ModelForm):
    """条件表单，用于创建和管理单个条件"""
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)  # 可选的项目参数，用于过滤传感器
        super().__init__(*args, **kwargs)
        
        # 尝试从实例获取所属项目
        try:
            if self.instance and self.instance.pk and self.instance.group and self.instance.group.strategy:
                self.project = self.instance.group.strategy.project
        except (AttributeError, ValueError):
            pass
        
        # 添加样式
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.TextInput, forms.NumberInput)):
                field.widget.attrs.update({'class': 'form-control'})
        
        # 根据项目过滤传感器选择
        if self.project:
            # 获取项目下所有设备的所有传感器
            self.fields['sensor'].queryset = Sensor.objects.filter(
                device__project=self.project
            )
            self.fields['threshold_value_sensor'].queryset = Sensor.objects.filter(
                device__project=self.project
            )

    class Meta:
        model = Condition
        fields = ('data_source_type', 'sensor', 'device_attribute', 'operator', 
                 'threshold_value_type', 'threshold_value_static', 
                 'threshold_value_sensor', 'threshold_value_device_attribute')
        # group 字段将通过表单集或视图设置


# 新增动作表单类
class ActionForm(forms.ModelForm):
    """动作表单，用于创建和管理执行动作"""
    
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)  # 可选的项目参数，用于过滤执行器
        super().__init__(*args, **kwargs)
        
        # 尝试从实例获取所属项目
        try:
            if self.instance and self.instance.pk and self.instance.strategy:
                self.project = self.instance.strategy.project
        except (AttributeError, ValueError):
            pass
        
        # 添加样式
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.TextInput, forms.NumberInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 3
                })
        
        # 为命令模板等添加占位符和说明
        self.fields['command_payload_template'].widget.attrs.update({
            'placeholder': '{"command": "on", "value": 100}',
            'class': 'form-control code-editor'
        })
        
        self.fields['notification_message_template'].widget.attrs.update({
            'placeholder': '传感器 {{ sensor.name }} 的值为 {{ sensor.value }}，已触发策略 {{ strategy.name }}',
            'class': 'form-control'
        })
        
        self.fields['webhook_headers_template'].widget.attrs.update({
            'placeholder': '{"Content-Type": "application/json", "Authorization": "Bearer xxx"}',
            'class': 'form-control code-editor'
        })
        
        self.fields['webhook_payload_template'].widget.attrs.update({
            'placeholder': '{"event": "strategy_triggered", "strategy_id": "{{ strategy.id }}", "data": {"sensor": "{{ sensor.name }}", "value": {{ sensor.value }}}}',
            'class': 'form-control code-editor'
        })
        
        # 执行顺序
        self.fields['execution_order'].widget.attrs.update({
            'type': 'number',
            'min': '1',
            'step': '1'
        })
        
        # 根据项目过滤执行器选择
        if self.project:
            # 获取项目下所有设备的所有执行器
            self.fields['target_actuator'].queryset = Actuator.objects.filter(
                device__project=self.project
            )
    
    class Meta:
        model = Action
        fields = ('action_type', 'execution_order', 'target_actuator', 
                 'command_payload_template', 'notification_recipient_type', 
                 'notification_recipient_value', 'notification_message_template',
                 'webhook_url', 'webhook_method', 'webhook_headers_template', 
                 'webhook_payload_template')
        # strategy 字段将通过表单集或视图设置


# 定义条件的内联表单集
ConditionFormSet = inlineformset_factory(
    ConditionGroup,  # 父模型
    Condition,       # 子模型
    form=ConditionForm,
    extra=1,         # 额外显示的空表单数量
    can_delete=True, # 允许删除
)

# 定义处理嵌套表单集的基类
class BaseConditionGroupFormSet(BaseInlineFormSet):
    """用于处理嵌套表单集的基类"""
    
    def add_fields(self, form, index):
        """为每个条件组表单添加嵌套的条件表单集"""
        super().add_fields(form, index)
        
        # 获取策略所属项目（用于过滤传感器）
        project = None
        if self.instance and self.instance.pk:
            project = self.instance.project
        
        # 为表单添加嵌套的条件表单集
        form.nested_condition_formset = ConditionFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f'{form.prefix}-conditions',  # 确保嵌套表单集有唯一前缀
        )
        
        # 为嵌套表单集中的每个条件表单设置项目
        if project:
            for condition_form in form.nested_condition_formset.forms:
                condition_form.project = project
    
    def save_nested(self, commit=True):
        """保存嵌套的条件表单集"""
        result = self.save(commit=commit)
        
        for form in self.forms:
            if hasattr(form, 'nested_condition_formset'):
                if not self._should_delete_form(form):
                    form.nested_condition_formset.save(commit=commit)
        
        return result

# 定义条件组的内联表单集
ConditionGroupFormSet = inlineformset_factory(
    Strategy,         # 父模型
    ConditionGroup,   # 子模型
    form=ConditionGroupForm,
    formset=BaseConditionGroupFormSet,  # 使用自定义的基类
    extra=1,          # 额外显示的空表单数量
    can_delete=True,  # 允许删除
)

# 定义动作的内联表单集
ActionFormSet = inlineformset_factory(
    Strategy,         # 父模型
    Action,           # 子模型
    form=ActionForm,
    extra=1,          # 额外显示的空表单数量
    can_delete=True,  # 允许删除
    fk_name='strategy'
) 