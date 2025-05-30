import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
import logging
import json
from django.utils import timezone
from datetime import datetime
from iot_devices.models import Device, Sensor, SensorData
from asgiref.sync import sync_to_async

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
        
        authenticated_device_id = None  # 用于存储认证成功的设备ID

        try:
            # 1. 接收认证数据 (假设以换行符结束的JSON)
            auth_data_raw = await reader.readline()
            if not auth_data_raw:
                self.stdout.write(self.style.WARNING(f"未收到来自 {addr} 的认证数据，关闭连接"))
                return  # 结束协程

            auth_data_str = auth_data_raw.decode().strip()
            self.stdout.write(f"来自 {addr} 的认证尝试: {auth_data_str}")

            try:
                auth_payload = json.loads(auth_data_str)
                if auth_payload.get("type") != "auth":
                    raise ValueError("无效的认证类型")
                
                device_id_str = auth_payload.get("device_id")
                device_key_str = auth_payload.get("device_key")
                
                if not device_id_str or not device_key_str:
                    raise ValueError("认证信息缺少device_id或device_key")

            except (json.JSONDecodeError, ValueError) as e:
                self.stderr.write(self.style.ERROR(f"来自 {addr} 的认证信息无效: {e}，关闭连接"))
                await self.send_json_response(writer, {"status": "error", "message": "无效的认证信息格式"})
                return

            # 2. 验证凭据
            device_instance = await self.authenticate_device_orm(device_id_str, device_key_str)

            if device_instance:
                authenticated_device_id = device_id_str
                self.stdout.write(self.style.SUCCESS(f"设备 {device_id_str} 认证成功，来自 {addr}"))
                await self.send_json_response(writer, {"status": "ok", "message": "认证成功"})
                
                # 更新设备状态为'online'
                await self.update_device_status(authenticated_device_id, 'online')
                
                self.stdout.write(self.style.SUCCESS(f"设备 {authenticated_device_id} 已准备好接收数据"))
                
                # 进入数据接收循环
                while True:
                    try:
                        line_raw = await reader.readline()
                        if not line_raw:
                            self.stdout.write(self.style.WARNING(f"设备 {authenticated_device_id} 关闭了连接 (EOF)"))
                            break  # 连接已关闭

                        line_str = line_raw.decode().strip()
                        if not line_str:  # 空行忽略
                            continue

                        self.stdout.write(f"来自设备 {authenticated_device_id} 的数据: {line_str}")

                        try:
                            data_payload_json = json.loads(line_str)
                            if data_payload_json.get("type") != "data":
                                self.stderr.write(self.style.ERROR(f"来自设备 {authenticated_device_id} 的非数据载荷: {line_str}，已忽略"))
                                await self.send_json_response(writer, {"status": "error", "message": "预期'data'类型的载荷"})
                                continue
                            
                            sensor_readings = data_payload_json.get("payload", {})
                            device_timestamp_unix = data_payload_json.get("timestamp")

                            if not sensor_readings:
                                self.stdout.write(self.style.WARNING(f"来自设备 {authenticated_device_id} 的传感器读数为空，已忽略"))
                                continue

                            # 处理传感器数据并存储
                            data_count = await self.process_and_store_sensor_data(
                                authenticated_device_id,  # UUID string
                                device_instance,          # Device ORM 实例
                                sensor_readings,
                                device_timestamp_unix
                            )
                            
                            # 更新设备 last_seen (即使没有有效数据，收到消息也认为在线)
                            await self.update_device_status(authenticated_device_id, 'online')
                            
                            # 发送数据接收确认
                            await self.send_json_response(writer, {
                                "status": "ok", 
                                "message": f"数据已接收并存储，处理了{data_count}个传感器读数"
                            })

                        except json.JSONDecodeError:
                            self.stderr.write(self.style.ERROR(f"来自设备 {authenticated_device_id} 的JSON数据无效: {line_str}，已忽略"))
                            await self.send_json_response(writer, {"status": "error", "message": "无效的JSON数据格式"})
                        except Exception as e_proc:  # 捕获处理数据时的其他错误
                            self.stderr.write(self.style.ERROR(f"处理来自设备 {authenticated_device_id} 的数据时出错: {e_proc}"))
                            await self.send_json_response(writer, {"status": "error", "message": "处理数据时出错"})
                    
                    except asyncio.IncompleteReadError:
                        self.stdout.write(self.style.WARNING(f"从设备 {authenticated_device_id} 读取数据不完整，连接可能正在关闭"))
                        break
                    except ConnectionResetError:
                        self.stdout.write(self.style.WARNING(f"与设备 {authenticated_device_id} 的连接在数据阶段被重置"))
                        break
                    except Exception as e_loop:
                        self.stderr.write(self.style.ERROR(f"设备 {authenticated_device_id} 的数据循环中出错: {e_loop}"))
                        break  # 退出循环

            else:
                self.stderr.write(self.style.ERROR(f"设备 {device_id_str} 认证失败，来自 {addr}"))
                await self.send_json_response(writer, {"status": "error", "message": "认证失败，无效的凭据"})
                return  # 认证失败，关闭连接

        except ConnectionResetError:
            self.stdout.write(self.style.WARNING(f"连接被重置: {addr}"))
        except asyncio.IncompleteReadError:
            self.stdout.write(self.style.WARNING(f"读取不完整，来自 {addr}，连接可能已关闭"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"处理客户端 {addr} 时出错: {e}"))
        finally:
            if authenticated_device_id:
                # 设备断开连接，更新状态为'offline'
                await self.update_device_status(authenticated_device_id, 'offline')
                self.stdout.write(self.style.HTTP_INFO(f"设备 {authenticated_device_id} 已断开连接，来自 {addr}"))
            
            self.stdout.write(self.style.HTTP_INFO(f"关闭与 {addr} 的连接"))
            writer.close()
            await writer.wait_closed()

    @sync_to_async
    def authenticate_device_orm(self, device_id_str, device_key_str):
        """通过ORM验证设备凭据"""
        try:
            device = Device.objects.get(device_id=device_id_str, device_key=device_key_str)
            # 可选：这里可以检查device的其他状态，如device.status != 'disabled'
            return device  # 返回device实例
        except Device.DoesNotExist:
            return None
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"验证设备 {device_id_str} 时ORM错误: {e}"))
            return None
    
    async def authenticate_device(self, device_id_str, device_key_str):
        """异步验证设备凭据"""
        device_instance = await self.authenticate_device_orm(device_id_str, device_key_str)
        return device_instance is not None
    
    @sync_to_async
    def update_device_status_orm(self, device_id_str, status):
        """通过ORM更新设备状态"""
        try:
            device = Device.objects.get(device_id=device_id_str)
            device.status = status
            if status == 'online':
                device.last_seen = timezone.now()
                device.save(update_fields=['status', 'last_seen'])
            else:
                device.save(update_fields=['status'])
            return True
        except Device.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"更新状态时设备 {device_id_str} 不存在"))
            return False
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"更新设备 {device_id_str} 状态时ORM错误: {e}"))
            return False

    async def update_device_status(self, device_id_str, status):
        """异步更新设备状态"""
        return await self.update_device_status_orm(device_id_str, status)

    @sync_to_async
    def store_sensor_data_orm(self, device_id_str, device_obj, sensor_readings, device_timestamp_unix):
        """通过ORM存储传感器数据"""
        try:
            # 确定时间戳
            if device_timestamp_unix:
                try:
                    # 假设是秒级 Unix 时间戳
                    record_timestamp = datetime.fromtimestamp(int(device_timestamp_unix), tz=timezone.get_current_timezone())
                except ValueError:
                    self.stderr.write(self.style.ERROR(f"设备 {device_id_str} 提供的时间戳 {device_timestamp_unix} 无效，使用服务器时间"))
                    record_timestamp = timezone.now()
            else:
                record_timestamp = timezone.now()

            created_data_count = 0
            for value_key, value in sensor_readings.items():
                try:
                    sensor = Sensor.objects.get(device=device_obj, value_key=value_key)
                    
                    # 根据值的类型存入对应字段
                    data_entry = SensorData(sensor=sensor, timestamp=record_timestamp)
                    if isinstance(value, bool):
                        data_entry.value_boolean = value
                    elif isinstance(value, (int, float)):
                        data_entry.value_float = float(value)
                    elif isinstance(value, str):
                        data_entry.value_string = value
                    elif isinstance(value, dict) or isinstance(value, list):  # JSONField 可以存 dict 或 list
                        data_entry.value_json = value
                    else:
                        self.stderr.write(self.style.WARNING(f"设备 {device_id_str} 的 {value_key} 值类型不支持: {type(value)}，以字符串形式存储"))
                        data_entry.value_string = str(value)  # 降级为字符串存储
                    
                    data_entry.save()
                    created_data_count += 1
                    self.stdout.write(f"已存储设备 {device_id_str} 的 {sensor} 数据")

                except Sensor.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"设备 {device_id_str} 没有value_key为 '{value_key}' 的传感器，数据已忽略"))
                except Exception as e_save:
                    self.stderr.write(self.style.ERROR(f"保存设备 {device_id_str} 的 {value_key} 传感器数据时出错: {e_save}"))
            return created_data_count

        except Exception as e_orm:
            self.stderr.write(self.style.ERROR(f"处理设备 {device_id_str} 的传感器数据时ORM错误: {e_orm}"))
            return 0

    async def process_and_store_sensor_data(self, device_id_str, device_obj, sensor_readings, device_timestamp_unix):
        """异步处理和存储传感器数据"""
        return await self.store_sensor_data_orm(device_id_str, device_obj, sensor_readings, device_timestamp_unix)

    async def send_json_response(self, writer: asyncio.StreamWriter, data: dict):
        """发送JSON响应"""
        response_str = json.dumps(data) + '\n'  # 添加换行符作为消息结束标记
        writer.write(response_str.encode())
        await writer.drain()

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