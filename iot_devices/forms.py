from django import forms
from .models import Project, Device

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为表单字段添加样式
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：智能家居监控'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '简单描述您的项目用途',
            'rows': '3'
        })

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ('name', 'device_identifier')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为表单字段添加样式
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：客厅温湿度计'
        })
        self.fields['device_identifier'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '设备的MAC地址或序列号 (可选)'
        })
        self.fields['device_identifier'].required = False 