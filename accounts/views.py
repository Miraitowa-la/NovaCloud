from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User

from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm, InvitationCodeCreateForm
from .models import UserProfile, InvitationCode, Role
from core.constants import AuditActionType
from core.utils import log_audit_event

def index(request):
    """
    网站主页视图
    展示欢迎信息和平台介绍
    """
    return render(request, 'accounts/index.html')


def register_view(request):
    """
    用户注册视图
    处理用户注册表单的提交和验证
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # 保存用户信息
            new_user = form.save()
            
            # 检查是否是第一个用户
            if User.objects.all().count() == 1:
                # 这是系统中的第一个用户，设置为超级管理员
                new_user.is_staff = True
                new_user.is_superuser = True
                new_user.save(update_fields=['is_staff', 'is_superuser'])
                messages.info(request, '恭喜您！作为系统的第一位用户，您已被自动设为超级管理员。')
            
            # 创建用户配置文件
            user_profile = UserProfile.objects.create(user=new_user)
            
            # 根据用户类型分配角色
            try:
                if new_user.is_staff and new_user.is_superuser:
                    # 为超级管理员分配"超级管理员"角色
                    admin_role = Role.objects.get(codename='super_admin')
                    user_profile.role = admin_role
                else:
                    # 为普通用户分配"普通用户"角色
                    normal_role = Role.objects.get(codename='normal_user')
                    user_profile.role = normal_role
                
                user_profile.save(update_fields=['role'])
            except Role.DoesNotExist:
                # 如果角色不存在，记录一条警告消息
                messages.warning(request, '系统角色配置不完整，请联系管理员。')
            
            # 处理邀请码
            code_str = form.cleaned_data.get('invitation_code')
            if code_str:
                try:
                    invitation = InvitationCode.objects.get(code=code_str)
                    
                    # 检查是否是用户自己创建的邀请码
                    if invitation.issuer == new_user:
                        messages.warning(request, '您不能使用自己创建的邀请码。')
                    # 显式检查邀请码是否有效
                    elif not invitation.is_currently_valid:
                        messages.warning(request, '此邀请码已无效、已过期或已达使用上限。')
                    else:
                        # 设置上级用户关系
                        user_profile.parent_user = invitation.issuer
                        user_profile.save()
                        
                        # 更新邀请码使用次数
                        invitation.times_used += 1
                        
                        # 如果达到最大使用次数，设为非激活
                        if invitation.max_uses is not None and invitation.times_used >= invitation.max_uses:
                            invitation.is_active = False
                            
                        invitation.save()
                        messages.info(request, f'已成功使用邀请码 "{invitation.code}"。')
                except InvitationCode.DoesNotExist:
                    # 这种情况应该在表单验证中已经处理过，但为保险起见再检查一次
                    messages.error(request, '邀请码不存在。')
            
            # 记录审计日志
            log_audit_event(
                request=request,
                action_type=AuditActionType.USER_REGISTER,
                target_object=new_user,
                details=f"用户 {new_user.username} 注册成功"
            )
            
            # 添加成功消息
            messages.success(request, '恭喜您，注册成功！现在您可以登录了。')
            
            # 重定向到登录页面
            return redirect('accounts:login')
        else:
            # 添加错误消息
            messages.error(request, '注册失败，请检查您输入的信息。')
    else:
        # GET请求，显示空表单
        form = UserRegistrationForm()
    
    # 渲染注册模板
    return render(request, 'accounts/register.html', {
        'form': form,
        'page_title': '用户注册'
    })


def login_view(request):
    """
    用户登录视图
    处理用户登录表单的提交和验证
    """
    # 获取用户可能要登录后重定向的URL
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            # 获取认证通过的用户
            user = form.get_user()
            
            # 检查用户是否有效
            if user is not None and user.is_active:
                # 登录用户
                login(request, user)
                
                # 记录审计日志
                log_audit_event(
                    request=request,
                    action_type=AuditActionType.USER_LOGIN,
                    target_object=user,
                    details=f"用户 {user.username} 登录成功"
                )
                
                # 添加成功消息
                messages.success(request, f'欢迎回来，{user.username}！')
                
                # 根据next参数决定重定向URL
                if 'next' in request.POST and request.POST.get('next'):
                    return redirect(request.POST.get('next'))
                else:
                    return redirect('accounts:index')  # 默认重定向到首页
            else:
                # 用户无效或未激活
                messages.error(request, '登录失败：账户未激活或已被禁用。')
        else:
            # 表单验证失败
            messages.error(request, '登录失败：请输入有效的用户名/邮箱和密码。')
    else:
        # GET请求，显示空表单
        form = UserLoginForm()
    
    # 渲染登录模板
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'page_title': '用户登录'
    })


@login_required
def logout_view(request):
    """
    用户登出视图
    清除用户会话并重定向
    """
    # 记录审计日志
    log_audit_event(
        request=request,
        action_type=AuditActionType.USER_LOGOUT,
        target_object=request.user,
        details=f"用户 {request.user.username} 登出系统"
    )
    
    # 登出用户
    logout(request)
    
    # 添加成功消息
    messages.info(request, '您已成功登出。')
    
    # 重定向到首页
    return redirect('accounts:index')


@login_required
def profile_view(request):
    """
    用户个人资料查看视图
    显示当前登录用户的个人资料
    """
    # 获取当前用户的个人资料
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # 如果个人资料不存在，创建一个
        user_profile = UserProfile.objects.create(user=request.user)
    
    # 渲染个人资料模板
    return render(request, 'accounts/profile.html', {
        'profile': user_profile,
        'page_title': '个人资料'
    })


@login_required
def profile_edit_view(request):
    """
    用户个人资料编辑视图
    处理用户个人资料编辑表单的提交和验证
    """
    # 获取当前用户的个人资料
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # 如果个人资料不存在，创建一个
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=user_profile)
        if form.is_valid():
            # 保存个人资料
            form.save()
            
            # 添加成功消息
            messages.success(request, '个人资料已成功更新。')
            
            # 重定向到个人资料查看页面
            return redirect('accounts:profile')
        else:
            # 添加错误消息
            messages.error(request, '个人资料更新失败，请检查您输入的信息。')
    else:
        # GET请求，显示当前个人资料
        form = UserProfileEditForm(instance=user_profile)
    
    # 渲染个人资料编辑模板
    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': user_profile,
        'page_title': '编辑个人资料'
    })


@login_required
def create_invitation_view(request):
    """
    创建邀请码视图
    处理用户创建邀请码表单的提交和验证
    """
    if request.method == 'POST':
        form = InvitationCodeCreateForm(request.POST)
        if form.is_valid():
            # 创建邀请码实例但不立即保存
            invitation = form.save(commit=False)
            # 设置当前用户为发行者
            invitation.issuer = request.user
            # 保存到数据库（此时会自动生成邀请码）
            invitation.save()
            
            # 将邀请码存入会话，以便在列表页面显示
            request.session['new_invitation_code'] = invitation.code
            
            # 添加成功消息
            messages.success(request, f'邀请码 "{invitation.code}" 已成功创建！')
            
            # 重定向到邀请码列表页面
            return redirect('accounts:invitation_list')
        else:
            # 添加错误消息
            messages.error(request, '创建邀请码失败，请检查您输入的信息。')
    else:
        # GET请求，显示空表单
        form = InvitationCodeCreateForm()
    
    # 渲染创建邀请码模板
    return render(request, 'accounts/create_invitation.html', {
        'form': form,
        'page_title': '创建邀请码'
    })


@login_required
def invitation_list_view(request):
    """
    邀请码列表视图
    显示用户创建的所有邀请码，分为有效和无效两类
    """
    # 获取当前登录用户创建的所有邀请码
    invitations = InvitationCode.objects.filter(issuer=request.user).order_by('-created_at')
    
    # 分离有效和无效的邀请码
    valid_invitations = []
    invalid_invitations = []
    
    for invitation in invitations:
        if invitation.is_currently_valid:
            valid_invitations.append(invitation)
        else:
            invalid_invitations.append(invitation)
    
    # 获取当前会话中可能存在的新创建的邀请码（新创建提示后会删除）
    new_code = request.session.get('new_invitation_code', '')
    if 'new_invitation_code' in request.session:
        del request.session['new_invitation_code']
    
    # 获取当前时间，用于模板中判断邀请码是否过期
    now = timezone.now()
    
    # 渲染邀请码列表模板
    return render(request, 'accounts/invitation_list.html', {
        'invitations': invitations,
        'valid_invitations': valid_invitations,
        'invalid_invitations': invalid_invitations,
        'valid_invitations_count': len(valid_invitations),
        'invalid_invitations_count': len(invalid_invitations),
        'new_code': new_code,
        'now': now,
        'page_title': '我的邀请码'
    })


@login_required
def delete_invitation_view(request, invitation_id):
    """
    删除邀请码视图
    处理用户删除邀请码的请求
    """
    try:
        # 查找指定ID的邀请码，并确认是当前用户创建的
        invitation = InvitationCode.objects.get(id=invitation_id, issuer=request.user)
        code = invitation.code  # 保存邀请码以在消息中使用
        
        # 删除邀请码
        invitation.delete()
        
        # 添加成功消息
        messages.success(request, f'邀请码 "{code}" 已成功删除。')
    except InvitationCode.DoesNotExist:
        # 添加错误消息
        messages.error(request, '邀请码不存在或您无权删除。')
    
    # 重定向回邀请码列表页面
    return redirect('accounts:invitation_list')


@login_required
def toggle_invitation_status_view(request, invitation_id):
    """
    切换邀请码状态视图
    处理启用/禁用邀请码的请求
    """
    try:
        # 查找指定ID的邀请码，并确认是当前用户创建的
        invitation = InvitationCode.objects.get(id=invitation_id, issuer=request.user)
        
        # 切换状态
        invitation.is_active = not invitation.is_active
        invitation.save()
        
        # 添加成功消息
        if invitation.is_active:
            messages.success(request, f'邀请码 "{invitation.code}" 已启用。')
        else:
            messages.success(request, f'邀请码 "{invitation.code}" 已禁用。')
    except InvitationCode.DoesNotExist:
        # 添加错误消息
        messages.error(request, '邀请码不存在或您无权操作。')
    
    # 重定向回邀请码列表页面
    return redirect('accounts:invitation_list')
