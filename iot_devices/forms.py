from django import forms
from .models import Project

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