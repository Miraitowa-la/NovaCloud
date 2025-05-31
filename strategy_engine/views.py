from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Strategy
from .forms import StrategyForm

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
            # 创建成功后重定向到策略详情页，后续将实现该页面
            # 暂时重定向到策略列表页
            return redirect('strategy_engine:strategy_list')
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
            # 更新成功后重定向到策略详情页，后续将实现该页面
            # 暂时重定向到策略列表页
            return redirect('strategy_engine:strategy_list')
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

# 后续步骤将实现 strategy_detail_view 用于配置条件和动作
