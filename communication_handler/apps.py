from django.apps import AppConfig
from django.conf import settings
import threading
import subprocess
import os
import sys


class CommunicationHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communication_handler'

    def ready(self):
        """
        当Django应用准备就绪时执行
        如果设置了NOVA_TCP_SERVER_AUTOSTART=True，则自动启动TCP服务器
        注意：Django开发服务器会调用ready()两次，一次是检查模型，一次是实际启动
        所以需要检查是否是主进程
        """
        # 检查是否是Django的主进程
        if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
            return

        # 检查配置是否启用了自动启动
        if getattr(settings, 'NOVA_TCP_SERVER_AUTOSTART', False):
            self.start_tcp_server()

    def start_tcp_server(self):
        """
        在单独的线程中启动TCP服务器
        """
        # 获取TCP服务器配置
        host = getattr(settings, 'NOVA_TCP_SERVER_HOST', '0.0.0.0')
        port = getattr(settings, 'NOVA_TCP_SERVER_PORT', 8100)

        # 定义启动函数
        def run_server():
            try:
                # 使用Python子进程启动TCP服务器
                cmd = [sys.executable, 'manage.py', 'run_tcp_server', 
                      f'--host={host}', f'--port={port}']
                
                # 设置环境变量，确保Python使用UTF-8编码
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                # 启动进程
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',  # 明确指定使用UTF-8编码
                    env=env  # 传递修改后的环境变量
                )
                
                # 输出服务器日志
                print(f"[自动启动] TCP服务器已在 {host}:{port} 启动 (PID: {process.pid})")
                
                # 监控输出
                for line in process.stdout:
                    print(f"[TCP服务器] {line.strip()}")
                
                # 等待进程结束
                process.wait()
                print("[自动启动] TCP服务器已停止")
                
            except Exception as e:
                print(f"[自动启动] TCP服务器启动失败: {e}")

        # 在后台线程中启动TCP服务器
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        print(f"[自动启动] TCP服务器线程已启动")
