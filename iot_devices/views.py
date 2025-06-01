from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging
from .models import Project, Device, Sensor, Actuator, SensorData, ActuatorCommandLog
from .forms import ProjectForm, DeviceForm, SensorForm, ActuatorForm

# 创建logger
logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def project_list_view(request):
    """显示当前用户的所有项目列表"""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    
    # 为每个项目添加设备数量信息
    for project in projects:
        # 获取项目下的所有设备总数
        project.device_count = Device.objects.filter(project=project).count()
        
        # 获取项目下在线设备的数量
        project.online_device_count = Device.objects.filter(
            project=project, 
            status='online'
        ).count()
        
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
    
    # 为每个设备添加传感器和执行器数量信息
    for device in devices:
        device.sensor_count = Sensor.objects.filter(device=device).count()
        device.actuator_count = Actuator.objects.filter(device=device).count()
    
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
    sensors = device.sensors.all()
    actuators = device.actuators.all()
    
    # 为每个传感器获取最新的数据记录
    sensors_with_latest_data = []
    for sensor in device.sensors.all().order_by('name'):
        latest_data = SensorData.objects.filter(sensor=sensor).order_by('-timestamp').first()
        sensors_with_latest_data.append({
            'sensor_info': sensor,
            'latest_data_record': latest_data,
            'latest_value': latest_data.get_value() if latest_data else None
        })
    
    return render(request, 'iot_devices/device_detail.html', {
        'device': device, 
        'project': project,
        'sensors': sensors,
        'sensors_with_latest_data': sensors_with_latest_data,
        'actuators': actuators
    })

# 传感器管理视图

@login_required
def sensor_add_view(request, project_id, device_id):
    """在设备下添加新传感器"""
    device = get_object_or_404(Device, pk=device_id, project__pk=project_id, 
                               project__owner=request.user)
    project = device.project
    
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)
            name = form.cleaned_data.get('name')
            value_key = form.cleaned_data.get('value_key')
            
            # 检查name在该设备下的唯一性
            if Sensor.objects.filter(device=device, name=name).exists():
                form.add_error('name', '此传感器名称在该设备下已存在。')
                return render(request, 'iot_devices/sensor_form.html', 
                             {'form': form, 'device': device, 'project': project})
            
            # 检查value_key在该设备下的唯一性
            if Sensor.objects.filter(device=device, value_key=value_key).exists():
                form.add_error('value_key', '此数据键名在该设备下已存在。')
                return render(request, 'iot_devices/sensor_form.html', 
                             {'form': form, 'device': device, 'project': project})
            
            sensor.device = device
            sensor.save()
            messages.success(request, f'传感器 "{sensor.name}" 已成功添加到设备 "{device.name}"！')
            return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    else:
        form = SensorForm()
    
    return render(request, 'iot_devices/sensor_form.html', 
                 {'form': form, 'device': device, 'project': project})

@login_required
def sensor_update_view(request, project_id, device_id, sensor_id):
    """更新传感器信息"""
    sensor = get_object_or_404(Sensor, pk=sensor_id, device__pk=device_id,
                              device__project__pk=project_id, device__project__owner=request.user)
    device = sensor.device
    project = device.project
    
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            value_key = form.cleaned_data.get('value_key')
            
            # 检查name在该设备下的唯一性（排除当前传感器）
            if Sensor.objects.filter(device=device, name=name).exclude(pk=sensor_id).exists():
                form.add_error('name', '此传感器名称在该设备下已存在。')
                return render(request, 'iot_devices/sensor_form.html', 
                             {'form': form, 'device': device, 'project': project, 'sensor': sensor})
            
            # 检查value_key在该设备下的唯一性（排除当前传感器）
            if Sensor.objects.filter(device=device, value_key=value_key).exclude(pk=sensor_id).exists():
                form.add_error('value_key', '此数据键名在该设备下已存在。')
                return render(request, 'iot_devices/sensor_form.html', 
                             {'form': form, 'device': device, 'project': project, 'sensor': sensor})
            
            form.save()
            messages.success(request, f'传感器 "{sensor.name}" 已成功更新！')
            return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    else:
        form = SensorForm(instance=sensor)
    
    return render(request, 'iot_devices/sensor_form.html', 
                 {'form': form, 'device': device, 'project': project, 'sensor': sensor})

@login_required
def sensor_delete_view(request, project_id, device_id, sensor_id):
    """删除传感器"""
    sensor = get_object_or_404(Sensor, pk=sensor_id, device__pk=device_id,
                              device__project__pk=project_id, device__project__owner=request.user)
    device = sensor.device
    project = device.project
    
    if request.method == 'POST':
        sensor_name = sensor.name
        sensor.delete()
        messages.success(request, f'传感器 "{sensor_name}" 已成功删除。')
        return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    
    return render(request, 'iot_devices/sensor_confirm_delete.html', 
                 {'sensor': sensor, 'device': device, 'project': project})

# 执行器管理视图

@login_required
def actuator_add_view(request, project_id, device_id):
    """在设备下添加新执行器"""
    device = get_object_or_404(Device, pk=device_id, project__pk=project_id, 
                               project__owner=request.user)
    project = device.project
    
    if request.method == 'POST':
        form = ActuatorForm(request.POST)
        if form.is_valid():
            actuator = form.save(commit=False)
            name = form.cleaned_data.get('name')
            command_key = form.cleaned_data.get('command_key')
            
            # 检查name在该设备下的唯一性
            if Actuator.objects.filter(device=device, name=name).exists():
                form.add_error('name', '此执行器名称在该设备下已存在。')
                return render(request, 'iot_devices/actuator_form.html', 
                             {'form': form, 'device': device, 'project': project})
            
            # 检查command_key在该设备下的唯一性
            if Actuator.objects.filter(device=device, command_key=command_key).exists():
                form.add_error('command_key', '此命令键名在该设备下已存在。')
                return render(request, 'iot_devices/actuator_form.html', 
                             {'form': form, 'device': device, 'project': project})
            
            actuator.device = device
            actuator.save()
            messages.success(request, f'执行器 "{actuator.name}" 已成功添加到设备 "{device.name}"！')
            return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    else:
        form = ActuatorForm()
    
    return render(request, 'iot_devices/actuator_form.html', 
                 {'form': form, 'device': device, 'project': project})

@login_required
def actuator_update_view(request, project_id, device_id, actuator_id):
    """更新执行器信息"""
    actuator = get_object_or_404(Actuator, pk=actuator_id, device__pk=device_id,
                              device__project__pk=project_id, device__project__owner=request.user)
    device = actuator.device
    project = device.project
    
    if request.method == 'POST':
        form = ActuatorForm(request.POST, instance=actuator)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            command_key = form.cleaned_data.get('command_key')
            
            # 检查name在该设备下的唯一性（排除当前执行器）
            if Actuator.objects.filter(device=device, name=name).exclude(pk=actuator_id).exists():
                form.add_error('name', '此执行器名称在该设备下已存在。')
                return render(request, 'iot_devices/actuator_form.html', 
                             {'form': form, 'device': device, 'project': project, 'actuator': actuator})
            
            # 检查command_key在该设备下的唯一性（排除当前执行器）
            if Actuator.objects.filter(device=device, command_key=command_key).exclude(pk=actuator_id).exists():
                form.add_error('command_key', '此命令键名在该设备下已存在。')
                return render(request, 'iot_devices/actuator_form.html', 
                             {'form': form, 'device': device, 'project': project, 'actuator': actuator})
            
            form.save()
            messages.success(request, f'执行器 "{actuator.name}" 已成功更新！')
            return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    else:
        form = ActuatorForm(instance=actuator)
    
    return render(request, 'iot_devices/actuator_form.html', 
                 {'form': form, 'device': device, 'project': project, 'actuator': actuator})

@login_required
def actuator_delete_view(request, project_id, device_id, actuator_id):
    """删除执行器"""
    actuator = get_object_or_404(Actuator, pk=actuator_id, device__pk=device_id,
                              device__project__pk=project_id, device__project__owner=request.user)
    device = actuator.device
    project = device.project
    
    if request.method == 'POST':
        actuator_name = actuator.name
        actuator.delete()
        messages.success(request, f'执行器 "{actuator_name}" 已成功删除。')
        return redirect('iot_devices:device_detail', project_id=project_id, device_id=device_id)
    
    return render(request, 'iot_devices/actuator_confirm_delete.html', 
                 {'actuator': actuator, 'device': device, 'project': project})

def send_command_to_device_via_tcp(actuator_command):
    """
    向TCP服务器发送执行器命令
    
    Args:
        actuator_command: ActuatorCommandLog实例
    
    Returns:
        bool: 是否成功将命令发送到TCP服务器
    """
    # 当前仅打印日志，未来将实现与TCP服务器的实际通信
    logger.info(
        f"命令已准备发送 - ActuatorCommandLog ID: {actuator_command.id}, "
        f"设备: {actuator_command.actuator.device.name}, "
        f"执行器: {actuator_command.actuator.name}, "
        f"命令: {actuator_command.command_payload}"
    )
    
    # 模拟成功发送
    return True

@login_required
@require_POST
def actuator_command_api_view(request, project_id, device_id, actuator_id):
    """
    接收和处理执行器命令的API视图
    
    Args:
        request: HTTP请求
        project_id: 项目ID
        device_id: 设备ID
        actuator_id: 执行器ID
    
    Returns:
        JsonResponse: API响应
    """
    # 获取对象并验证权限
    try:
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        device = get_object_or_404(Device, pk=device_id, project=project)
        actuator = get_object_or_404(Actuator, pk=actuator_id, device=device)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"权限验证失败: {str(e)}"}, status=403)
    
    # 解析请求数据
    try:
        data = json.loads(request.body)
        command_value = data.get('value')
        
        # 验证命令值
        if command_value is None:
            return JsonResponse({"status": "error", "message": "命令值不能为空"}, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"请求解析错误: {str(e)}"}, status=400)
    
    # 构建命令载荷
    command_payload = {actuator.command_key: command_value}
    
    # 创建命令日志记录
    try:
        actuator_command = ActuatorCommandLog.objects.create(
            actuator=actuator,
            user=request.user,
            command_payload=command_payload,
            status='pending_send',
            source='user_ui'
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"创建命令记录失败: {str(e)}"}, status=500)
    
    # 尝试发送命令到TCP服务器
    try:
        send_success = send_command_to_device_via_tcp(actuator_command)
        
        # 根据发送结果更新状态
        if send_success:
            actuator_command.status = 'sent'
            actuator_command.save()
            return JsonResponse({
                "status": "success", 
                "message": "命令已发送处理", 
                "command_id": actuator_command.id
            })
        else:
            actuator_command.status = 'failed'
            actuator_command.save()
            return JsonResponse({
                "status": "error", 
                "message": "命令发送失败，请稍后重试", 
                "command_id": actuator_command.id
            }, status=500)
            
    except Exception as e:
        actuator_command.status = 'failed'
        actuator_command.save()
        return JsonResponse({
            "status": "error", 
            "message": f"命令处理过程中发生错误: {str(e)}", 
            "command_id": actuator_command.id
        }, status=500)
