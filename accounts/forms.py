from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    """
    用户注册表单
    扩展Django内置的UserCreationForm，添加邮箱字段并自定义样式
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入您的邮箱'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 为所有字段添加form-control类，并设置占位符
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '设置您的用户名'
        })
        
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': '设置您的密码'
            })
            # 保留部分有用的帮助文本
            self.fields['password1'].help_text = '您的密码不能与个人信息太相似，至少包含8个字符，不能是常用密码，且不能全为数字。'
        
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': '确认您的密码'
            })
            self.fields['password2'].help_text = '请再次输入相同的密码进行确认。'

    def clean_email(self):
        """验证邮箱是否已被注册"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("此邮箱已被注册，请使用其他邮箱。")
        return email


class UserLoginForm(AuthenticationForm):
    """
    用户登录表单
    扩展Django内置的AuthenticationForm，并自定义样式
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 自定义用户名字段
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '用户名或邮箱'
        })
        self.fields['username'].label = '用户名/邮箱'
        
        # 自定义密码字段
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入您的密码'
        }) 