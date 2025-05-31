from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Strategy, ConditionGroup, Condition, Action
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
        # 实例化条件组表单集
        condition_group_formset = ConditionGroupFormSet(
            request.POST, 
            instance=strategy,
            prefix='conditiongroups'
        )
        
        # 实例化动作表单集
        action_formset = ActionFormSet(
            request.POST,
            instance=strategy,
            prefix='actions'
        )
        
        # 记录表单验证和保存状态
        conditions_valid = False
        actions_valid = False
        
        # 检查条件组表单集是否有效
        if condition_group_formset.is_valid():
            try:
                # 保存条件组
                condition_groups = condition_group_formset.save(commit=True)
                
                # 处理嵌套的条件表单集
                for form in condition_group_formset.forms:
                    # 如果表单未被删除且有附加的条件表单集
                    if not condition_group_formset._should_delete_form(form) and hasattr(form, 'nested_condition_formset'):
                        # 重新获取保存后的条件组实例
                        if form.instance.pk:
                            # 检查嵌套的条件表单集是否有效
                            if form.nested_condition_formset.is_valid():
                                # 保存条件
                                form.nested_condition_formset.save()
                            else:
                                # 如果条件表单集无效，添加错误并重新渲染
                                for condition_form in form.nested_condition_formset.forms:
                                    for field, errors in condition_form.errors.items():
                                        for error in errors:
                                            messages.error(request, f"条件错误 ({field}): {error}")
                                raise ValueError("条件表单验证失败")
                
                conditions_valid = True
            except ValueError as e:
                # 如果有任何错误，保留表单数据，显示错误消息
                messages.error(request, f"保存条件失败: {str(e)}")
        else:
            # 显示条件组表单集的错误
            for form in condition_group_formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"条件组错误 ({field}): {error}")
        
        # 检查动作表单集是否有效
        if action_formset.is_valid():
            try:
                # 保存动作
                action_formset.save()
                actions_valid = True
            except Exception as e:
                messages.error(request, f"保存动作失败: {str(e)}")
        else:
            # 显示动作表单集的错误
            for form in action_formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"动作错误 ({field}): {error}")
        
        # 根据验证结果显示成功或错误消息
        if conditions_valid and actions_valid:
            messages.success(request, '策略条件和动作已成功保存！')
            # 刷新页面以获取最新数据
            return redirect('strategy_engine:strategy_detail', strategy_id=strategy.id)
        elif conditions_valid:
            messages.success(request, '策略条件已成功保存，但动作保存失败。')
        elif actions_valid:
            messages.success(request, '策略动作已成功保存，但条件保存失败。')
    else:
        # GET请求，初始化表单集
        condition_group_formset = ConditionGroupFormSet(
            instance=strategy,
            prefix='conditiongroups'
        )
        
        action_formset = ActionFormSet(
            instance=strategy,
            prefix='actions'
        )
    
    return render(request, 'strategy_engine/strategy_detail.html', {
        'strategy': strategy,
        'condition_group_formset': condition_group_formset,
        'action_formset': action_formset,
    })
