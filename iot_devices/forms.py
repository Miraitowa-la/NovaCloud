from django import forms
from .models import Project, Device, Sensor, Actuator

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

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ('name', 'sensor_type', 'unit', 'value_key')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为表单字段添加样式和占位符
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：室内温度'
        })
        self.fields['sensor_type'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：温度、湿度、光照、运动等'
        })
        self.fields['unit'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：°C、%、lux等'
        })
        self.fields['value_key'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '上报JSON中的数据键名，例如：temperature'
        })

class ActuatorForm(forms.ModelForm):
    class Meta:
        model = Actuator
        fields = ('name', 'actuator_type', 'command_key')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为表单字段添加样式和占位符
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：客厅灯'
        })
        self.fields['actuator_type'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '例如：开关、调光器、风扇、电机等'
        })
        self.fields['command_key'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '用于控制的JSON键名，例如：switch_state'
        }) 