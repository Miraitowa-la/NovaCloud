from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import UserProfile, InvitationCode


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

    invitation_code = forms.CharField(
        max_length=32,
        required=False,
        label="邀请码 (可选)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '如果您有邀请码，请在此输入'
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
    
    def clean_invitation_code(self):
        """验证邀请码是否有效"""
        code = self.cleaned_data.get('invitation_code')
        if not code:
            # 邀请码是可选的
            return code
        
        try:
            # 尝试查询邀请码
            invitation = InvitationCode.objects.get(code=code)
            
            # 检查邀请码是否有效
            if not invitation.is_currently_valid:
                raise forms.ValidationError("此邀请码无效、已过期或已达使用上限。")
                
            return code
        except InvitationCode.DoesNotExist:
            raise forms.ValidationError("邀请码不存在。")


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


class UserProfileEditForm(forms.ModelForm):
    """
    用户个人资料编辑表单
    用于编辑UserProfile中的字段
    """
    # 使用URLField替代ImageField，因为我们现在只处理头像URL
    avatar_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入头像URL'
        })
    )
    
    # 添加姓和名字段，从User模型
    first_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入您的名字'
        })
    )
    
    last_name = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入您的姓氏'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ('phone_number',)  # 不直接包含avatar，因为我们用avatar_url代替
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '请输入您的电话号码'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = False
        
        # 如果实例存在且有avatar，将其URL放入avatar_url字段
        if self.instance and self.instance.avatar:
            self.fields['avatar_url'].initial = self.instance.avatar
            
        # 初始化姓名字段
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        # 暂不保存到数据库
        profile = super().save(commit=False)
        
        # 处理avatar_url
        avatar_url = self.cleaned_data.get('avatar_url')
        if avatar_url:
            # 直接将URL保存到avatar字段
            profile.avatar = avatar_url
            
        # 保存姓名到User模型
        if commit and profile.user:
            profile.user.first_name = self.cleaned_data.get('first_name', '')
            profile.user.last_name = self.cleaned_data.get('last_name', '')
            profile.user.save(update_fields=['first_name', 'last_name'])
        
        if commit:
            profile.save()
        
        return profile 


class InvitationCodeCreateForm(forms.ModelForm):
    """
    邀请码创建表单
    用于创建新的邀请码
    """
    class Meta:
        model = InvitationCode
        fields = ('max_uses', 'expires_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 设置最大使用次数字段
        self.fields['max_uses'].required = False
        self.fields['max_uses'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '留空表示无限制',
            'min': '1'  # 最小值限制
        })
        self.fields['max_uses'].help_text = '设置此邀请码可使用的最大次数，留空表示无限制。'
        
        # 设置过期时间字段
        self.fields['expires_at'].required = False
        self.fields['expires_at'].widget = forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'placeholder': '留空表示永不过期'
        })
        self.fields['expires_at'].help_text = '设置此邀请码的过期时间，留空表示永不过期。' 