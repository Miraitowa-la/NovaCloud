from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm

# Create your views here.

@login_required
def project_list_view(request):
    """显示当前用户的所有项目列表"""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'iot_devices/project_list.html', {'projects': projects})

@login_required
def project_create_view(request):
    """创建新项目"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'项目 "{project.name}" 已成功创建！')
            return redirect('iot_devices:project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'iot_devices/project_form.html', {'form': form})

@login_required
def project_update_view(request, project_id):
    """更新现有项目"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'项目 "{project.name}" 已成功更新！')
            return redirect('iot_devices:project_list')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'iot_devices/project_form.html', {'form': form})

@login_required
def project_delete_view(request, project_id):
    """删除项目"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'项目 "{project_name}" 已成功删除。')
        return redirect('iot_devices:project_list')
    
    return render(request, 'iot_devices/project_confirm_delete.html', {'project': project})
