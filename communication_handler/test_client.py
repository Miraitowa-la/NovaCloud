#!/usr/bin/env python
"""
NovaCloud TCP客户端测试脚本
用于测试TCP服务器的基本功能

使用方法:
python test_client.py [--host HOST] [--port PORT]
"""

import socket
import argparse
import time
import sys

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NovaCloud TCP客户端测试工具')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='TCP服务器地址 (默认: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888,
                        help='TCP服务器端口 (默认: 8888)')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    print(f"正在连接到TCP服务器 {args.host}:{args.port}...")
    
    try:
        # 创建TCP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 设置超时时间为5秒
        
        # 连接服务器
        sock.connect((args.host, args.port))
        print(f"已连接到服务器 {args.host}:{args.port}")
        
        while True:
            # 获取用户输入
            message = input("请输入要发送的消息（输入'exit'退出）: ")
            
            if message.lower() == 'exit':
                break
            
            # 发送消息
            sock.sendall(message.encode())
            print(f"已发送: {message}")
            
            # 接收回显
            response = sock.recv(1024)
            print(f"收到回显: {response.decode()}")
            
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