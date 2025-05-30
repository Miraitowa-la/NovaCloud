#!/usr/bin/env python
"""
NovaCloud 测试数据生成工具
用于创建测试用的项目和设备，以便测试TCP设备认证功能

使用方法:
python create_test_device.py [--username <用户名>]
"""

import os
import sys
import argparse
import django
from pathlib import Path

# 将当前目录添加到Python路径，以便导入Django项目
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NovaCloud.settings')
django.setup()

# 导入Django模型（在django.setup()之后）
from iot_devices.models import Device, Project, Sensor, Actuator
from django.contrib.auth.models import User
from django.db import transaction


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud 测试数据生成工具')
    parser.add_argument('--username', type=str, default=None,
                        help='指定用户名，未提供则使用第一个可用用户')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 获取用户
    if args.username:
        try:
            user = User.objects.get(username=args.username)
        except User.DoesNotExist:
            print(f"错误: 用户 '{args.username}' 不存在")
            return
    else:
        try:
            user = User.objects.first()
            if not user:
                print("错误: 系统中没有用户。请先创建用户，或使用--username参数指定现有用户")
                return
        except Exception as e:
            print(f"获取用户时出错: {e}")
            return
    
    print(f"使用用户: {user.username}")
    
    # 创建测试项目和设备
    with transaction.atomic():
        # 创建测试项目
        project_name = "TCP测试项目"
        project, created = Project.objects.get_or_create(
            name=project_name,
            owner=user,
            defaults={
                'description': '用于测试TCP设备通信的项目'
            }
        )
        
        if created:
            print(f"已创建新项目: {project.name} (ID: {project.project_id})")
        else:
            print(f"使用现有项目: {project.name} (ID: {project.project_id})")
        
        # 创建测试设备
        device_name = "TCP测试设备"
        device, created = Device.objects.get_or_create(
            name=device_name,
            project=project,
            defaults={
                'device_identifier': 'TEST_DEVICE_001',
                'status': 'unregistered'
            }
        )
        
        if created:
            print(f"已创建新设备: {device.name}")
            print(f"设备ID: {device.device_id}")
            print(f"设备密钥: {device.device_key}")
        else:
            print(f"使用现有设备: {device.name}")
            print(f"设备ID: {device.device_id}")
            print(f"设备密钥: {device.device_key}")
        
        # 创建测试传感器
        sensor_name = "温度传感器"
        sensor, created = Sensor.objects.get_or_create(
            name=sensor_name,
            device=device,
            defaults={
                'sensor_type': 'temperature',
                'unit': '°C',
                'value_key': 'temperature'
            }
        )
        
        if created:
            print(f"已创建新传感器: {sensor.name}")
        else:
            print(f"使用现有传感器: {sensor.name}")
        
        # 创建测试执行器
        actuator_name = "灯光开关"
        actuator, created = Actuator.objects.get_or_create(
            name=actuator_name,
            device=device,
            defaults={
                'actuator_type': 'switch',
                'command_key': 'light_switch',
                'current_state_payload': {'status': 'OFF'}
            }
        )
        
        if created:
            print(f"已创建新执行器: {actuator.name}")
        else:
            print(f"使用现有执行器: {actuator.name}")
    
    print("\n要使用此设备测试TCP认证，请运行:")
    print(f"python communication_handler/test_client.py --device_id {device.device_id} --device_key {device.device_key}")


if __name__ == "__main__":
    main() 