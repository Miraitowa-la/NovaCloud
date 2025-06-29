#!/usr/bin/env python
"""
NovaCloud TCP客户端测试脚本
用于测试TCP服务器的设备认证和数据通信功能

使用方法:
python test_client.py --device_id <设备UUID> --device_key <设备密钥> [--host HOST] [--port PORT] [--auto] [--heartbeat]
"""

import socket
import argparse
import time
import sys
import json
import uuid
import random
import threading

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud TCP客户端测试工具')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='TCP服务器地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8100,
                        help='TCP服务器端口 (默认: 8100)')
    parser.add_argument('--device_id', type=str, default=None,
                        help='设备ID (UUID格式)')
    parser.add_argument('--device_key', type=str, default=None,
                        help='设备密钥 (128位字符串)')
    parser.add_argument('--auto', action='store_true',
                        help='自动生成并发送模拟传感器数据')
    parser.add_argument('--heartbeat', action='store_true',
                        help='启用心跳机制 (每30秒发送一次心跳)')
    parser.add_argument('--heartbeat-interval', type=int, default=30,
                        help='心跳间隔，单位为秒 (默认: 30)')
    return parser.parse_args()

def format_json_message(data):
    """将数据格式化为JSON消息，添加换行符作为消息结束标记"""
    return json.dumps(data) + '\n'

def generate_mock_sensor_data():
    """生成模拟传感器数据"""
    return {
        "type": "data",
        "timestamp": int(time.time()),
        "payload": {
            "temperature": round(random.uniform(18.0, 28.0), 1),  # 模拟温度 18-28°C
            "humidity": round(random.uniform(30.0, 70.0), 1),     # 模拟湿度 30-70%
            "light_level": random.randint(0, 1000),               # 模拟光照级别 0-1000
            "motion_detected": random.choice([True, False])       # 模拟运动检测
        }
    }

def generate_status_data():
    """生成设备状态数据"""
    return {
        "type": "status",
        "timestamp": int(time.time()),
        "payload": {
            "battery": random.randint(0, 100),       # 电池电量 0-100%
            "rssi": random.randint(-100, -30),       # 信号强度 -100 to -30 dBm
            "uptime": random.randint(1, 1000000),    # 运行时间（秒）
            "version": "1.0.0"                       # 设备固件版本
        }
    }

def generate_heartbeat():
    """生成心跳包"""
    return {
        "type": "heartbeat",
        "timestamp": int(time.time())
    }

def heartbeat_thread(sock, interval):
    """心跳线程函数"""
    print(f"\n心跳线程已启动，间隔: {interval}秒")
    try:
        while True:
            # 生成并发送心跳包
            heartbeat = generate_heartbeat()
            heartbeat_message = format_json_message(heartbeat)
            sock.sendall(heartbeat_message.encode())
            print(f"\n已发送心跳: {heartbeat}")
            
            # 接收响应
            try:
                sock.settimeout(5)  # 设置5秒超时
                response_raw = sock.recv(1024)
                response_str = response_raw.decode().strip()
                
                try:
                    response = json.loads(response_str)
                    print(f"收到心跳响应: {response}")
                except json.JSONDecodeError:
                    print(f"收到非JSON心跳响应: {response_str}")
            except socket.timeout:
                print("心跳响应超时")
            except Exception as e:
                print(f"接收心跳响应时出错: {e}")
                break
            
            # 等待下一次心跳
            time.sleep(interval)
    except Exception as e:
        print(f"心跳线程异常: {e}")
    finally:
        print("心跳线程已停止")

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
        print("python communication_handler/list_devices.py")
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
                
                # 如果启用了心跳，启动心跳线程
                heartbeat_thread_instance = None
                if args.heartbeat:
                    # 创建并启动心跳线程
                    heartbeat_thread_instance = threading.Thread(
                        target=heartbeat_thread,
                        args=(sock, args.heartbeat_interval),
                        daemon=True  # 设为守护线程，主线程结束时自动结束
                    )
                    heartbeat_thread_instance.start()
                
                # 自动模式下，生成并发送模拟数据
                if args.auto:
                    try:
                        print("\n===== 自动数据生成模式 =====")
                        print("将每2秒发送一次随机生成的传感器数据")
                        print("按Ctrl+C可停止发送并退出")
                        print("===========================\n")
                        
                        while True:
                            # 生成随机传感器数据
                            data_frame = generate_mock_sensor_data()
                            
                            # 发送数据
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
                            
                            # 等待2秒
                            time.sleep(2)
                    except KeyboardInterrupt:
                        print("\n自动数据生成已停止")
                
                # 手动输入模式
                else:
                    # 发送数据循环
                    while True:
                        print("\n请选择操作:")
                        print("1. 发送自定义消息")
                        print("2. 发送传感器数据")
                        print("3. 发送心跳包")
                        print("4. 发送状态信息")
                        print("5. 退出")
                        choice = input("请输入选项 (1-5): ")
                        
                        if choice == '5':
                            break
                        
                        if choice == '1':
                            # 获取用户输入
                            message = input("请输入要发送的消息: ")
                            
                            # 发送简单消息
                            data_frame = {
                                "type": "data",
                                "timestamp": int(time.time()),
                                "payload": {
                                    "message": message
                                }
                            }
                        elif choice == '2':
                            # 发送传感器数据
                            temperature = input("请输入温度值 (按Enter跳过): ")
                            humidity = input("请输入湿度值 (按Enter跳过): ")
                            light = input("请输入光照值 (按Enter跳过): ")
                            motion = input("请输入运动检测 (true/false, 按Enter跳过): ")
                            
                            # 构建传感器数据
                            sensor_payload = {}
                            if temperature:
                                try:
                                    sensor_payload["temperature"] = float(temperature)
                                except ValueError:
                                    print("温度值必须是数字，已忽略")
                            if humidity:
                                try:
                                    sensor_payload["humidity"] = float(humidity)
                                except ValueError:
                                    print("湿度值必须是数字，已忽略")
                            if light:
                                try:
                                    sensor_payload["light_level"] = int(light)
                                except ValueError:
                                    print("光照值必须是整数，已忽略")
                            if motion and motion.lower() in ['true', 'false']:
                                sensor_payload["motion_detected"] = motion.lower() == 'true'
                            
                            # 如果没有任何有效数据，跳过发送
                            if not sensor_payload:
                                print("没有提供任何有效的传感器数据，已跳过发送")
                                continue
                            
                            # 构建数据帧
                            data_frame = {
                                "type": "data",
                                "timestamp": int(time.time()),
                                "payload": sensor_payload
                            }
                        elif choice == '3':
                            # 发送心跳包
                            data_frame = generate_heartbeat()
                        elif choice == '4':
                            # 发送状态信息
                            data_frame = generate_status_data()
                        else:
                            print("无效选项，请重试")
                            continue
                        
                        # 发送数据
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