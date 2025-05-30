#!/usr/bin/env python
"""
NovaCloud 设备信息查询工具
用于列出数据库中的设备ID和密钥，便于测试TCP设备认证功能

使用方法:
python list_devices.py [--project_id <项目ID>]
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
from iot_devices.models import Device, Project
from django.contrib.auth.models import User


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud 设备信息查询工具')
    parser.add_argument('--project_id', type=str, default=None,
                        help='项目ID (用于筛选特定项目的设备)')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 获取项目列表
    projects = Project.objects.all()
    print(f"系统中共有 {projects.count()} 个项目:")
    
    for project in projects:
        print(f"\n项目: {project.name} (ID: {project.project_id})")
        print(f"所有者: {project.owner.username}")
        
        # 获取项目下的设备
        if args.project_id and str(project.project_id) != args.project_id:
            # 如果指定了项目ID且不匹配，则跳过
            devices = []
            print("  (已跳过此项目的设备，因为指定了不同的项目ID)")
        else:
            devices = Device.objects.filter(project=project)
            print(f"  设备数量: {devices.count()}")
        
        # 打印设备详情
        for device in devices:
            print("\n  " + "-" * 60)
            print(f"  设备名称: {device.name}")
            print(f"  设备ID: {device.device_id}")
            print(f"  设备密钥: {device.device_key}")
            print(f"  设备状态: {device.status}")
            print(f"  上次在线: {device.last_seen or '从未在线'}")
            
            # 打印传感器数量
            sensors_count = device.sensors.count()
            print(f"  传感器数量: {sensors_count}")
            
            # 打印执行器数量
            actuators_count = device.actuators.count()
            print(f"  执行器数量: {actuators_count}")
    
    print("\n要使用设备ID和密钥测试TCP认证，请运行:")
    print("python communication_handler/test_client.py --device_id <设备ID> --device_key <设备密钥>")


if __name__ == "__main__":
    main() 