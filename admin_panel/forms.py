from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Permission
from accounts.models import UserProfile, Role
from core.constants import AUDIT_ACTION_CHOICES

class AdminUserCreationForm(UserCreationForm):
    """
    管理员创建用户的表单
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'})
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    parent_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="上级用户",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'parent_user')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=True)  # 先保存User对象以获取user_id
        
        # 创建或更新UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if self.cleaned_data.get('role'):
            profile.role = self.cleaned_data.get('role')
        
        if self.cleaned_data.get('parent_user'):
            profile.parent_user = self.cleaned_data.get('parent_user')
        
        if commit:
            profile.save()
            
        return user

class AdminUserChangeForm(UserChangeForm):
    """
    管理员编辑用户的表单
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'})
    )
    
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    parent_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="上级用户",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        label="账户有效",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_staff = forms.BooleanField(
        required=False,
        label="管理员权限",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff', 'role', 'parent_user')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 移除密码字段，密码修改应在另一个视图处理
        self.fields.pop('password', None)
        
        # 如果用户有profile，初始化role和parent_user字段
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['role'].initial = self.instance.profile.role
            self.fields['parent_user'].initial = self.instance.profile.parent_user
            
            # 避免将用户自己设为自己的上级
            self.fields['parent_user'].queryset = User.objects.exclude(pk=self.instance.pk)
            
            # 如果用户是超级管理员(is_staff=True)，禁用父级用户字段
            if self.instance.is_staff:
                self.fields['parent_user'].disabled = True
                self.fields['parent_user'].help_text = "超级管理员不能设置上级用户"
                self.fields['parent_user'].required = False
                self.fields['parent_user'].initial = None
                
    def clean(self):
        cleaned_data = super().clean()
        is_staff = cleaned_data.get('is_staff')
        parent_user = cleaned_data.get('parent_user')
        
        # 如果用户是超级管理员且设置了上级用户，清除上级用户
        if is_staff and parent_user:
            cleaned_data['parent_user'] = None
            self.add_warning = "超级管理员不能设置上级用户，上级用户设置已被清除"
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=True)
        
        # 创建或更新UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if self.cleaned_data.get('role'):
            profile.role = self.cleaned_data.get('role')
        
        # 如果用户是超级管理员，确保没有上级用户
        if user.is_staff:
            profile.parent_user = None
        else:
            profile.parent_user = self.cleaned_data.get('parent_user')
        
        if commit:
            profile.save()
            
        return user

class RoleForm(forms.ModelForm):
    """
    角色管理表单
    """
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入角色名称'})
    )
    
    codename = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入角色代码'})
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': '请输入角色描述', 'rows': 3})
    )
    
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox'}),
        help_text="选择该角色拥有的权限"
    )
    
    class Meta:
        model = Role
        fields = ('name', 'codename', 'description', 'permissions')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 按内容类型和模型名排序权限，使其更有组织性
        self.fields['permissions'].queryset = Permission.objects.all().order_by(
            'content_type__app_label', 
            'content_type__model', 
            'name'
        ) 

class AuditLogFilterForm(forms.Form):
    """
    审计日志筛选表单
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="所有用户",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    action_type = forms.ChoiceField(
        choices=[('', '所有操作类型')] + list(AUDIT_ACTION_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': '开始日期'
        }),
        label="开始日期"
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': '结束日期'
        }),
        label="结束日期"
    )
    
    ip_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索IP地址'
        }),
        label="IP地址"
    )
    
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索目标对象或详情'
        }),
        label="搜索内容"
    ) 