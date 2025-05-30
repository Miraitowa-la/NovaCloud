#!/usr/bin/env python
"""
NovaCloud 传感器数据查询工具
用于查询数据库中已存储的传感器数据

使用方法:
python check_sensor_data.py [--device_id <设备ID>] [--limit <数量限制>]
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
from iot_devices.models import Device, Sensor, SensorData
from django.db.models import Count


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud 传感器数据查询工具')
    parser.add_argument('--device_id', type=str, default=None,
                        help='设备ID (UUID) 用于筛选特定设备的数据')
    parser.add_argument('--limit', type=int, default=10,
                        help='每个传感器显示的最大数据条数 (默认: 10)')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 获取设备列表
    if args.device_id:
        try:
            devices = Device.objects.filter(device_id=args.device_id)
            if not devices.exists():
                print(f"错误: 未找到ID为 {args.device_id} 的设备")
                return
        except Exception as e:
            print(f"查询设备时出错: {e}")
            return
    else:
        devices = Device.objects.all()
    
    print(f"系统中共有 {devices.count()} 个设备:")
    
    # 遍历设备
    for device in devices:
        print(f"\n设备: {device.name} (ID: {device.device_id})")
        print(f"所属项目: {device.project.name}")
        print(f"状态: {device.status}")
        print(f"上次在线: {device.last_seen or '从未在线'}")
        
        # 获取设备的传感器
        sensors = Sensor.objects.filter(device=device)
        print(f"传感器数量: {sensors.count()}")
        
        # 遍历传感器
        for sensor in sensors:
            # 获取传感器数据统计
            data_count = SensorData.objects.filter(sensor=sensor).count()
            print(f"\n  传感器: {sensor.name} (类型: {sensor.sensor_type}, 单位: {sensor.unit})")
            print(f"  数据键名: {sensor.value_key}")
            print(f"  数据记录数: {data_count}")
            
            # 获取最新的传感器数据
            if data_count > 0:
                print(f"\n  最新 {min(args.limit, data_count)} 条数据记录:")
                print("  " + "-" * 60)
                print("  {:^24} | {:^30}".format("时间戳", "值"))
                print("  " + "-" * 60)
                
                data_records = SensorData.objects.filter(sensor=sensor).order_by('-timestamp')[:args.limit]
                for record in data_records:
                    value = record.get_value()
                    timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    print("  {:^24} | {:<30}".format(timestamp, value))
            else:
                print("  尚无数据记录")


if __name__ == "__main__":
    main() 