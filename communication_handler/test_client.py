#!/usr/bin/env python
"""
NovaCloud TCP客户端测试脚本
用于测试TCP服务器的设备认证和数据通信功能

使用方法:
python test_client.py --device_id <设备UUID> --device_key <设备密钥> [--host HOST] [--port PORT]
"""

import socket
import argparse
import time
import sys
import json
import uuid

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud TCP客户端测试工具')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='TCP服务器地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888,
                        help='TCP服务器端口 (默认: 8888)')
    parser.add_argument('--device_id', type=str, default=None,
                        help='设备ID (UUID格式)')
    parser.add_argument('--device_key', type=str, default=None,
                        help='设备密钥 (128位字符串)')
    return parser.parse_args()

def format_json_message(data):
    """将数据格式化为JSON消息，添加换行符作为消息结束标记"""
    return json.dumps(data) + '\n'

def main():
    """主函数"""
    args = parse_args()
    
    # 验证设备ID格式（简单检查，非严格UUID验证）
    if args.device_id:
        try:
            # 尝试转换为UUID以验证格式
            uuid.UUID(args.device_id)
        except ValueError:
            print(f"错误: 设备ID {args.device_id} 不是有效的UUID格式")
            return
    
    # 如果未提供设备ID和设备密钥，提供模拟值或提示用户
    if not args.device_id or not args.device_key:
        print("警告: 未提供设备ID或设备密钥。")
        if not args.device_id:
            print("- 请使用 --device_id 参数提供一个有效的设备UUID。")
        if not args.device_key:
            print("- 请使用 --device_key 参数提供设备密钥。")
        print("\n您可以在设备详情页面获取这些信息。")
        print("或者使用以下命令查询数据库中的设备：")
        print("python manage.py shell")
        print(">>> from iot_devices.models import Device")
        print(">>> Device.objects.values_list('device_id', 'device_key')")
        return
    
    print(f"正在连接到TCP服务器 {args.host}:{args.port}...")
    
    try:
        # 创建TCP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 设置超时时间为5秒
        
        # 连接服务器
        sock.connect((args.host, args.port))
        print(f"已连接到服务器 {args.host}:{args.port}")
        
        # 发送认证帧
        auth_frame = {
            "type": "auth",
            "device_id": args.device_id,
            "device_key": args.device_key
        }
        
        auth_message = format_json_message(auth_frame)
        sock.sendall(auth_message.encode())
        print(f"已发送认证帧: {auth_frame}")
        
        # 接收认证响应
        response_raw = sock.recv(1024)
        response_str = response_raw.decode().strip()
        
        try:
            response = json.loads(response_str)
            print(f"收到认证响应: {response}")
            
            # 检查认证结果
            if response.get("status") == "ok":
                print("认证成功! 现在可以发送数据...")
                
                # 发送数据循环
                while True:
                    # 获取用户输入
                    message = input("请输入要发送的消息（输入'exit'退出）: ")
                    
                    if message.lower() == 'exit':
                        break
                    
                    # 发送数据帧
                    data_frame = {
                        "type": "data",
                        "timestamp": int(time.time()),
                        "payload": {
                            "message": message
                        }
                    }
                    
                    data_message = format_json_message(data_frame)
                    sock.sendall(data_message.encode())
                    print(f"已发送数据: {data_frame}")
                    
                    # 接收响应
                    response_raw = sock.recv(1024)
                    response_str = response_raw.decode().strip()
                    
                    try:
                        response = json.loads(response_str)
                        print(f"收到响应: {response}")
                    except json.JSONDecodeError:
                        print(f"收到非JSON响应: {response_str}")
            else:
                print(f"认证失败: {response.get('message', '未知错误')}")
                
        except json.JSONDecodeError:
            print(f"收到非JSON响应: {response_str}")
            
    except socket.timeout:
        print("连接超时，请确认服务器正在运行并检查主机和端口设置。")
    except ConnectionRefusedError:
        print("连接被拒绝，请确认服务器正在运行并检查主机和端口设置。")
    except KeyboardInterrupt:
        print("\n客户端被用户停止")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        try:
            sock.close()
        except:
            pass
        print("连接已关闭")

if __name__ == "__main__":
    main() 