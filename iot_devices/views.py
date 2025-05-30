from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Project, Device
from .forms import ProjectForm, DeviceForm

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

# 设备管理视图

@login_required
def device_list_view(request, project_id):
    """显示项目下的所有设备"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    devices = Device.objects.filter(project=project).order_by('-created_at')
    return render(request, 'iot_devices/device_list.html', {'project': project, 'devices': devices})

@login_required
def device_create_view(request, project_id):
    """在项目下创建新设备"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device_identifier = form.cleaned_data.get('device_identifier')
            
            # 如果提供了device_identifier，检查项目内唯一性
            if device_identifier:
                if Device.objects.filter(project=project, device_identifier=device_identifier).exists():
                    form.add_error('device_identifier', '此设备物理ID在该项目下已存在。')
                    return render(request, 'iot_devices/device_form.html', {'form': form, 'project': project})
            
            device.project = project
            device.save()
            messages.success(request, f'设备 "{device.name}" 已成功添加到项目 "{project.name}"！')
            return redirect('iot_devices:device_list', project_id=project.pk)
    else:
        form = DeviceForm()
    
    return render(request, 'iot_devices/device_form.html', {'form': form, 'project': project})

@login_required
def device_update_view(request, project_id, device_id):
    """更新设备信息"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    device = get_object_or_404(Device, pk=device_id, project=project)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            device_identifier = form.cleaned_data.get('device_identifier')
            
            # 如果提供了device_identifier，检查项目内唯一性（排除当前设备）
            if device_identifier:
                if Device.objects.filter(
                    project=project, 
                    device_identifier=device_identifier
                ).exclude(pk=device_id).exists():
                    form.add_error('device_identifier', '此设备物理ID在该项目下已存在。')
                    return render(request, 'iot_devices/device_form.html', 
                                 {'form': form, 'project': project, 'device': device})
            
            form.save()
            messages.success(request, f'设备 "{device.name}" 已成功更新！')
            return redirect('iot_devices:device_list', project_id=project.pk)
    else:
        form = DeviceForm(instance=device)
    
    return render(request, 'iot_devices/device_form.html', 
                 {'form': form, 'project': project, 'device': device})

@login_required
def device_delete_view(request, project_id, device_id):
    """删除设备"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    device = get_object_or_404(Device, pk=device_id, project=project)
    
    if request.method == 'POST':
        device_name = device.name
        project_pk = device.project.pk
        device.delete()
        messages.success(request, f'设备 "{device_name}" 已成功删除。')
        return redirect('iot_devices:device_list', project_id=project_pk)
    
    return render(request, 'iot_devices/device_confirm_delete.html', 
                 {'device': device, 'project': project})

@login_required
def device_detail_view(request, project_id, device_id):
    """设备详情页"""
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    device = get_object_or_404(Device, pk=device_id, project=project)
    
    # 获取设备的传感器和执行器（为后续功能实现做准备）
    sensors = device.sensor_set.all()
    actuators = device.actuator_set.all()
    
    return render(request, 'iot_devices/device_detail.html', {
        'device': device, 
        'project': project,
        'sensors': sensors,
        'actuators': actuators
    })
