from django import forms
from .models import Strategy
from iot_devices.models import Project

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