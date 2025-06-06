from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Strategy, ConditionGroup, Condition, Action, ExecutionLog
from .forms import StrategyForm, ConditionGroupFormSet, ActionFormSet

@login_required
def strategy_list_view(request):
    """
    显示当前用户创建的所有策略列表
    """
    strategies = Strategy.objects.filter(owner=request.user).order_by('-updated_at')
    return render(request, 'strategy_engine/strategy_list.html', {
        'strategies': strategies,
        'active_nav': 'strategies'  # 用于导航栏高亮
    })

@login_required
def strategy_create_view(request):
    """
    创建新策略
    """
    if request.method == 'POST':
        form = StrategyForm(request.POST, user=request.user)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.owner = request.user
            strategy.save()
            messages.success(request, f'策略 "{strategy.name}" 已成功创建！现在请为其添加条件和动作。')
            # 创建成功后重定向到策略配置页
            return redirect('strategy_engine:strategy_detail', strategy_id=strategy.id)
    else:
        form = StrategyForm(user=request.user)
    
    return render(request, 'strategy_engine/strategy_form.html', {
        'form': form
    })

@login_required
def strategy_update_view(request, strategy_id):
    """
    编辑策略基本信息
    """
    strategy = get_object_or_404(Strategy, pk=strategy_id, owner=request.user)
    
    if request.method == 'POST':
        form = StrategyForm(request.POST, instance=strategy, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'策略 "{strategy.name}" 的基本信息已成功更新！')
            # 更新成功后重定向到策略配置页
            return redirect('strategy_engine:strategy_detail', strategy_id=strategy.id)
    else:
        form = StrategyForm(instance=strategy, user=request.user)
    
    return render(request, 'strategy_engine/strategy_form.html', {
        'form': form,
        'strategy': strategy
    })

@login_required
def strategy_delete_view(request, strategy_id):
    """
    删除策略
    """
    strategy = get_object_or_404(Strategy, pk=strategy_id, owner=request.user)
    
    if request.method == 'POST':
        strategy_name = strategy.name
        strategy.delete()
        messages.success(request, f'策略 "{strategy_name}" 已成功删除。')
        return redirect('strategy_engine:strategy_list')
    
    return render(request, 'strategy_engine/strategy_confirm_delete.html', {
        'strategy': strategy
    })

@login_required
def strategy_detail_view(request, strategy_id):
    """
    策略详情页，用于配置条件组和条件，以及执行动作
    """
    strategy = get_object_or_404(Strategy, pk=strategy_id, owner=request.user)
    
    if request.method == 'POST':
        # 记录原始POST数据的键，用于调试
        print(f"接收到的POST数据键: {list(request.POST.keys())}")
        
        # 实例化条件组表单集
        condition_group_formset = ConditionGroupFormSet(
            request.POST, 
            instance=strategy,
            prefix='conditiongroup_set'  # 确保与前端JavaScript使用的前缀一致
        )
        
        # 实例化动作表单集
        action_formset = ActionFormSet(
            request.POST,
            instance=strategy,
            prefix='action_set'  # 确保与前端JavaScript使用的前缀一致
        )
        
        # 记录表单验证和保存状态
        conditions_valid = False
        actions_valid = False
        
        # 检查条件组表单集是否有效
        if condition_group_formset.is_valid():
            try:
                # 打印临时引用信息，用于调试
                temp_refs = {}
                for key in request.POST:
                    if key.endswith('-temp_group_ref'):
                        temp_refs[key] = request.POST[key]
                
                if temp_refs:
                    print(f"发现临时组引用: {temp_refs}")
                    
                # 使用自定义的save_nested方法保存条件组及其嵌套的条件
                condition_groups = condition_group_formset.save_nested(commit=True)
                print(f"成功保存了{len(condition_groups)}个条件组")
                conditions_valid = True
            except Exception as e:
                # 如果有任何错误，保留表单数据，显示错误消息
                import traceback
                error_msg = f"保存条件失败: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)  # 在服务器控制台打印详细错误
                messages.error(request, f"保存条件失败: {str(e)}")
        else:
            # 显示条件组表单集的错误
            for form_idx, form in enumerate(condition_group_formset):
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"条件组 #{form_idx+1} 错误 ({field}): {error}")
                
                # 检查嵌套的条件表单集错误
                if hasattr(form, 'nested_condition_formset'):
                    for cond_idx, cond_form in enumerate(form.nested_condition_formset):
                        for field, errors in cond_form.errors.items():
                            for error in errors:
                                messages.error(request, f"条件组 #{form_idx+1} 的条件 #{cond_idx+1} 错误 ({field}): {error}")
            
            # 打印管理表单的错误
            if condition_group_formset.management_form.errors:
                print("条件组管理表单错误:", condition_group_formset.management_form.errors)
                messages.error(request, f"条件组表单管理错误: {condition_group_formset.management_form.errors}")
        
        # 检查动作表单集是否有效
        if action_formset.is_valid():
            try:
                # 保存动作
                actions = action_formset.save()
                print(f"成功保存了{len(actions)}个动作")
                actions_valid = True
            except Exception as e:
                import traceback
                error_msg = f"保存动作失败: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)  # 在服务器控制台打印详细错误
                messages.error(request, f"保存动作失败: {str(e)}")
        else:
            # 显示动作表单集的错误
            for form_idx, form in enumerate(action_formset):
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"动作 #{form_idx+1} 错误 ({field}): {error}")
            
            # 打印管理表单的错误
            if action_formset.management_form.errors:
                print("动作管理表单错误:", action_formset.management_form.errors)
                messages.error(request, f"动作表单管理错误: {action_formset.management_form.errors}")
        
        # 根据验证结果显示成功或错误消息
        if conditions_valid and actions_valid:
            messages.success(request, '策略条件和动作已成功保存！')
            # 刷新页面以获取最新数据，传递参数避免添加空表单
            return redirect('strategy_engine:strategy_detail', strategy_id=strategy.id)
        elif conditions_valid:
            messages.success(request, '策略条件已成功保存，但动作保存失败。')
        elif actions_valid:
            messages.success(request, '策略动作已成功保存，但条件保存失败。')
    else:
        # GET请求，判断是否有现有的条件组和动作
        has_condition_groups = ConditionGroup.objects.filter(strategy=strategy).exists()
        has_actions = Action.objects.filter(strategy=strategy).exists()
        
        # 初始化表单集，根据是否已有内容决定extra参数
        condition_group_formset = ConditionGroupFormSet(
            instance=strategy,
            prefix='conditiongroup_set',
        )
        
        action_formset = ActionFormSet(
            instance=strategy,
            prefix='action_set',
        )
        
        # 如果表单集没有表单，手动添加一个空表单
        if len(condition_group_formset.forms) == 0:
            condition_group_formset.extra = 1
        else:
            condition_group_formset.extra = 0
            
        if len(action_formset.forms) == 0:
            action_formset.extra = 1
        else:
            action_formset.extra = 0
    
    # 为所有嵌套表单集添加项目信息
    if hasattr(condition_group_formset, 'forms'):
        for form in condition_group_formset.forms:
            if hasattr(form, 'nested_condition_formset'):
                for condition_form in form.nested_condition_formset.forms:
                    condition_form.project = strategy.project
    
    return render(request, 'strategy_engine/strategy_detail.html', {
        'strategy': strategy,
        'condition_group_formset': condition_group_formset,
        'action_formset': action_formset,
    })

@login_required
def execution_log_list_view(request):
    """
    显示策略执行日志列表，支持按策略筛选和分页
    """
    # 获取筛选参数
    strategy_id = request.GET.get('strategy_id')
    
    # 基础查询：只查询用户自己的策略日志
    logs_query = ExecutionLog.objects.filter(
        strategy__owner=request.user
    ).select_related('strategy').order_by('-triggered_at')
    
    # 如果提供了策略ID，进一步筛选
    if strategy_id:
        try:
            # 确保该策略属于当前用户
            strategy = get_object_or_404(Strategy, id=strategy_id, owner=request.user)
            logs_query = logs_query.filter(strategy_id=strategy_id)
            selected_strategy_id = int(strategy_id)
        except (ValueError, Strategy.DoesNotExist):
            # 如果策略ID无效，忽略筛选
            selected_strategy_id = None
    else:
        selected_strategy_id = None
    
    # 获取用户的所有策略，用于筛选下拉框
    user_strategies = Strategy.objects.filter(owner=request.user).order_by('name')
    
    # 实现分页
    paginator = Paginator(logs_query, 10)  # 每页10条日志
    page = request.GET.get('page')
    
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，返回第一页
        logs = paginator.page(1)
    except EmptyPage:
        # 如果page超出范围，返回最后一页
        logs = paginator.page(paginator.num_pages)
    
    return render(request, 'strategy_engine/execution_log_list.html', {
        'logs': logs,
        'user_strategies': user_strategies,
        'selected_strategy_id': selected_strategy_id,
        'active_nav': 'strategy_logs'  # 用于导航栏高亮
    })
