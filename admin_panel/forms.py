from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Permission
from accounts.models import UserProfile, Role

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
    
    def save(self, commit=True):
        user = super().save(commit=True)
        
        # 创建或更新UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if self.cleaned_data.get('role'):
            profile.role = self.cleaned_data.get('role')
        
        if self.cleaned_data.get('parent_user'):
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