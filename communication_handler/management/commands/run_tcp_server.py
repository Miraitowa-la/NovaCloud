import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

# 配置日志
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'NovaCloud TCP服务器 - 用于设备通信'

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--host', 
            type=str, 
            default=getattr(settings, 'NOVA_TCP_SERVER_HOST', '0.0.0.0'),
            help='TCP服务器监听地址 (默认: settings.NOVA_TCP_SERVER_HOST 或 0.0.0.0)'
        )
        parser.add_argument(
            '--port', 
            type=int, 
            default=getattr(settings, 'NOVA_TCP_SERVER_PORT', 8888),
            help='TCP服务器监听端口 (默认: settings.NOVA_TCP_SERVER_PORT 或 8888)'
        )

    async def handle_client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        self.stdout.write(self.style.HTTP_INFO(f"接受来自 {addr} 的连接"))
        
        # 在此阶段仅实现简单的回显功能
        try:
            while True:
                data = await reader.read(1024)  # 读取数据块
                if not data:  # 连接关闭
                    break
                
                message = data.decode('utf-8', errors='replace')  # 解码，容错处理
                self.stdout.write(f"收到来自 {addr!r} 的数据: {message!r}")

                # 回显数据（仅用于初步测试）
                writer.write(data)
                await writer.drain()
                self.stdout.write(f"已回显数据给 {addr!r}")
        
        except ConnectionResetError:
            self.stdout.write(self.style.WARNING(f"连接被重置: {addr}"))
        except asyncio.CancelledError:
            self.stdout.write(self.style.WARNING(f"连接处理被取消: {addr}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"处理客户端 {addr} 时出错: {e}"))
        finally:
            self.stdout.write(self.style.HTTP_INFO(f"关闭与 {addr} 的连接"))
            writer.close()
            await writer.wait_closed()

    async def handle_async(self, options):
        """异步处理入口"""
        host = options['host']
        port = options['port']
        
        self.stdout.write(self.style.SUCCESS(f'正在启动TCP服务器，监听地址: {host}:{port}...'))
        
        try:
            # 创建服务器
            server = await asyncio.start_server(
                self.handle_client_connection, 
                host, 
                port
            )
            
            # 输出服务器的地址信息
            for socket in server.sockets:
                addr = socket.getsockname()
                self.stdout.write(self.style.SUCCESS(f'服务器已启动 - 监听地址: {addr[0]}:{addr[1]}'))
            
            # 运行服务器，直到被中断
            self.stdout.write(self.style.SUCCESS('按Ctrl+C可停止服务器...'))
            async with server:
                await server.serve_forever()
                
        except OSError as e:
            self.stderr.write(self.style.ERROR(f'启动服务器时出错: {e}'))
            if e.errno == 98:  # 地址已被使用
                self.stderr.write(self.style.ERROR(f'端口 {port} 已被占用，请尝试其他端口'))
            raise

    def handle(self, *args, **options):
        """命令入口点"""
        try:
            # 运行异步服务器
            asyncio.run(self.handle_async(options))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nTCP服务器被用户停止'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'TCP服务器错误: {e}')) 