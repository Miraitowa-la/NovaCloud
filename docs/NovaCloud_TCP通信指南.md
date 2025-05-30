# NovaCloud TCP通信指南

## 目录
- [1. 概述](#1-概述)
- [2. 通信基础](#2-通信基础)
  - [2.1 连接信息](#21-连接信息)
  - [2.2 消息格式](#22-消息格式)
- [3. 设备认证](#3-设备认证)
  - [3.1 认证流程](#31-认证流程)
  - [3.2 认证消息格式](#32-认证消息格式)
  - [3.3 认证响应](#33-认证响应)
  - [3.4 认证示例](#34-认证示例)
- [4. 数据上报](#4-数据上报)
  - [4.1 传感器数据上报](#41-传感器数据上报)
  - [4.2 数据类型支持](#42-数据类型支持)
  - [4.3 数据上报示例](#43-数据上报示例)
- [5. 心跳机制](#5-心跳机制)
  - [5.1 心跳消息格式](#51-心跳消息格式)
  - [5.2 心跳频率](#52-心跳频率)
  - [5.3 心跳示例](#53-心跳示例)
- [6. 设备状态上报](#6-设备状态上报)
  - [6.1 状态消息格式](#61-状态消息格式)
  - [6.2 状态类型](#62-状态类型)
  - [6.3 状态上报示例](#63-状态上报示例)
- [7. 命令接收与响应](#7-命令接收与响应)
  - [7.1 命令消息格式](#71-命令消息格式)
  - [7.2 命令响应格式](#72-命令响应格式)
  - [7.3 命令示例](#73-命令示例)
- [8. 代码示例](#8-代码示例)
  - [8.1 Python示例客户端](#81-python示例客户端)
  - [8.2 错误处理](#82-错误处理)
- [9. 最佳实践与注意事项](#9-最佳实践与注意事项)

## 1. 概述

NovaCloud TCP通信服务允许IoT设备通过TCP协议与NovaCloud平台进行双向通信。本文档详细介绍了通信的各个方面，包括设备认证、数据上报、心跳机制、状态上报和命令响应等。

设备需要先连接到NovaCloud TCP服务器，进行认证后才能进行后续的通信。认证成功后，设备可以上报传感器数据、设备状态，接收平台下发的控制命令，并定期发送心跳包以维持连接。

## 2. 通信基础

### 2.1 连接信息

- **服务器地址**：由NovaCloud平台管理员提供
- **端口**：默认为8100（可能根据部署环境而变化）
- **协议**：TCP
- **通信格式**：文本格式的JSON，每条消息以换行符`\n`结束
- **编码**：UTF-8

### 2.2 消息格式

所有消息都使用JSON格式，基本结构如下：

```json
{
  "type": "消息类型",
  "payload": {
    // 消息内容，根据type不同而变化
  }
}
```

消息类型(`type`)包括：
- `auth`：设备认证
- `data`：传感器数据上报
- `status`：设备状态上报
- `heartbeat`：心跳包
- `command`：平台下发的命令
- `command_response`：设备对命令的响应

每条JSON消息必须以换行符(`\n`)结束，以便服务器识别消息边界。

## 3. 设备认证

### 3.1 认证流程

1. 设备连接到NovaCloud TCP服务器
2. 连接建立后，设备立即发送认证消息
3. 服务器验证设备ID和密钥
4. 服务器返回认证结果
5. 认证成功后，设备可以进行后续通信；认证失败，服务器将关闭连接

### 3.2 认证消息格式

```json
{
  "type": "auth",
  "payload": {
    "device_id": "设备UUID",
    "device_key": "设备密钥"
  }
}
```

- `device_id`：在NovaCloud平台创建设备时生成的UUID
- `device_key`：在NovaCloud平台创建设备时生成的128位认证密钥

### 3.3 认证响应

认证成功：

```json
{
  "type": "auth_response",
  "payload": {
    "status": "success",
    "message": "认证成功"
  }
}
```

认证失败：

```json
{
  "type": "auth_response",
  "payload": {
    "status": "error",
    "message": "认证失败原因"
  }
}
```

### 3.4 认证示例

```python
import socket
import json
import time

# 创建TCP套接字并连接到服务器
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('nova-cloud-server.example.com', 8100))

# 准备认证消息
auth_message = {
    "type": "auth",
    "payload": {
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "device_key": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    }
}

# 发送认证消息(确保添加换行符)
client.send((json.dumps(auth_message) + '\n').encode('utf-8'))

# 接收认证响应
response = client.recv(1024).decode('utf-8')
response_data = json.loads(response)

if response_data.get('type') == 'auth_response' and response_data.get('payload', {}).get('status') == 'success':
    print("认证成功，可以开始通信")
else:
    print(f"认证失败: {response_data.get('payload', {}).get('message', '未知错误')}")
    client.close()
```

## 4. 数据上报

### 4.1 传感器数据上报

设备可以定期或根据触发条件上报传感器数据。数据消息格式如下：

```json
{
  "type": "data",
  "timestamp": 1678886400,
  "payload": {
    "temperature": 25.5,
    "humidity": 65,
    "pressure": 101.3
  }
}
```

- `timestamp`：数据生成的UNIX时间戳（秒），可选。如果不提供，服务器会使用接收时间
- `payload`：包含传感器数据的键值对，键名必须与NovaCloud平台上配置的Sensor的`value_key`匹配

### 4.2 数据类型支持

传感器值支持多种数据类型：

- 数值型（整数、浮点数）：适用于温度、湿度、压力等
- 字符串：适用于文本信息、状态描述等
- 布尔值：适用于开关状态、触发器状态等
- JSON对象/数组：适用于复杂的数据结构

### 4.3 数据上报示例

```python
# 上报多种类型的传感器数据
sensor_data = {
    "type": "data",
    "timestamp": int(time.time()),
    "payload": {
        "temperature": 25.5,
        "humidity": 65,
        "is_window_open": False,
        "status_message": "正常运行",
        "location": {"lat": 39.9042, "lng": 116.4074},
        "history": [24.5, 25.0, 25.5]
    }
}

client.send((json.dumps(sensor_data) + '\n').encode('utf-8'))
```

## 5. 心跳机制

### 5.1 心跳消息格式

心跳包是一种简单的消息，用于保持设备与服务器的连接，并表明设备处于活跃状态。

```json
{
  "type": "heartbeat"
}
```

心跳包不需要服务器响应。服务器会根据最近收到的心跳包更新设备的`last_seen`时间和在线状态。

### 5.2 心跳频率

建议的心跳频率范围：

- **标准频率**：60秒一次
- **最小频率**：30秒一次（更频繁可能被视为滥用）
- **最大频率**：180秒一次（超过此时间可能被视为断线）

具体频率可以根据设备类型和网络条件调整。请咨询NovaCloud平台管理员获取推荐的心跳频率。

### 5.3 心跳示例

```python
# 定期发送心跳包
import threading

def send_heartbeat():
    while True:
        try:
            heartbeat = {"type": "heartbeat"}
            client.send((json.dumps(heartbeat) + '\n').encode('utf-8'))
            time.sleep(60)  # 60秒一次心跳
        except Exception as e:
            print(f"心跳发送失败: {e}")
            break

# 启动心跳线程
heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
heartbeat_thread.start()
```

## 6. 设备状态上报

### 6.1 状态消息格式

设备可以定期上报自身状态，如电池电量、信号强度等。

```json
{
  "type": "status",
  "payload": {
    "battery": 85,
    "signal": -65,
    "memory": 75,
    "uptime": 3600
  }
}
```

### 6.2 状态类型

常见状态类型包括但不限于：

- `battery`：电池电量百分比（0-100）
- `signal`：信号强度（dBm，例如WiFi RSSI值）
- `memory`：内存使用率百分比
- `cpu`：CPU使用率百分比
- `uptime`：设备运行时间（秒）
- `firmware_version`：固件版本
- `errors`：错误计数或错误状态对象

### 6.3 状态上报示例

```python
# 上报设备状态
device_status = {
    "type": "status",
    "payload": {
        "battery": 85,
        "signal": -65,
        "memory": 75,
        "uptime": 3600,
        "firmware_version": "1.2.3",
        "errors": {
            "connection_failures": 2,
            "sensor_errors": 0
        }
    }
}

client.send((json.dumps(device_status) + '\n').encode('utf-8'))
```

## 7. 命令接收与响应

### 7.1 命令消息格式

平台会向设备发送命令消息，通常用于控制设备的执行器：

```json
{
  "type": "command",
  "command_id": "cmd_uuid_123",
  "payload": {
    "light_switch": "ON",
    "fan_speed": 3,
    "set_temperature": 23
  }
}
```

- `command_id`：命令的唯一标识符，用于关联命令与响应
- `payload`：包含执行器控制指令的键值对，键名必须与NovaCloud平台上配置的Actuator的`command_key`匹配

### 7.2 命令响应格式

设备执行命令后，应回复命令响应：

```json
{
  "type": "command_response",
  "command_id": "cmd_uuid_123",
  "status": "success",
  "payload": {
    "current_state": "ON",
    "execution_time": 0.5
  }
}
```

- `command_id`：对应收到的命令ID
- `status`：`success`表示成功，`error`表示失败，`pending`表示处理中
- `payload`：可以包含命令执行的结果、当前状态或错误信息

### 7.3 命令示例

```python
# 处理接收到的命令
def handle_command(command_data):
    try:
        command_id = command_data.get('command_id')
        payload = command_data.get('payload', {})
        
        # 处理命令
        result = {}
        for key, value in payload.items():
            # 这里应该包含实际执行命令的逻辑
            print(f"执行命令: {key} = {value}")
            result[key] = value
        
        # 发送成功响应
        response = {
            "type": "command_response",
            "command_id": command_id,
            "status": "success",
            "payload": {
                "current_state": result,
                "execution_time": 0.5
            }
        }
        
        client.send((json.dumps(response) + '\n').encode('utf-8'))
    except Exception as e:
        # 发送错误响应
        error_response = {
            "type": "command_response",
            "command_id": command_data.get('command_id', ''),
            "status": "error",
            "payload": {
                "error": str(e)
            }
        }
        client.send((json.dumps(error_response) + '\n').encode('utf-8'))

# 监听和处理入站消息
def listen_for_messages():
    buffer = ""
    while True:
        try:
            data = client.recv(1024).decode('utf-8')
            if not data:
                print("连接已关闭")
                break
                
            buffer += data
            
            # 处理完整的JSON消息
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                message = json.loads(line)
                
                if message.get('type') == 'command':
                    handle_command(message)
                
        except Exception as e:
            print(f"消息处理错误: {e}")
            break

# 启动消息监听线程
listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
listen_thread.start()
```

## 8. 代码示例

### 8.1 Python示例客户端

下面是一个完整的Python示例客户端，包含认证、数据上报、心跳和命令处理：

```python
import socket
import json
import time
import threading
import random

class NovaCloudTcpClient:
    def __init__(self, host, port, device_id, device_key):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.device_key = device_key
        self.client = None
        self.connected = False
        self.buffer = ""
        
    def connect(self):
        """连接到服务器并进行认证"""
        try:
            # 创建TCP套接字并连接
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            
            # 发送认证消息
            auth_message = {
                "type": "auth",
                "payload": {
                    "device_id": self.device_id,
                    "device_key": self.device_key
                }
            }
            self.send_message(auth_message)
            
            # 接收认证响应
            response = self.client.recv(1024).decode('utf-8')
            response_data = json.loads(response)
            
            if response_data.get('type') == 'auth_response' and response_data.get('payload', {}).get('status') == 'success':
                print("认证成功")
                self.connected = True
                
                # 启动心跳线程
                self.start_heartbeat()
                
                # 启动消息监听线程
                self.start_message_listener()
                
                return True
            else:
                print(f"认证失败: {response_data.get('payload', {}).get('message', '未知错误')}")
                self.client.close()
                return False
                
        except Exception as e:
            print(f"连接错误: {e}")
            if self.client:
                self.client.close()
            return False
    
    def send_message(self, message):
        """发送消息到服务器"""
        if not self.client or not self.connected:
            print("未连接，无法发送消息")
            return False
            
        try:
            self.client.send((json.dumps(message) + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            self.connected = False
            return False
    
    def send_sensor_data(self, data_dict, timestamp=None):
        """发送传感器数据"""
        if timestamp is None:
            timestamp = int(time.time())
            
        message = {
            "type": "data",
            "timestamp": timestamp,
            "payload": data_dict
        }
        
        return self.send_message(message)
    
    def send_device_status(self, status_dict):
        """发送设备状态"""
        message = {
            "type": "status",
            "payload": status_dict
        }
        
        return self.send_message(message)
    
    def start_heartbeat(self, interval=60):
        """启动心跳线程"""
        def send_heartbeat():
            while self.connected:
                try:
                    heartbeat = {"type": "heartbeat"}
                    if not self.send_message(heartbeat):
                        break
                    time.sleep(interval)
                except Exception as e:
                    print(f"心跳发送失败: {e}")
                    self.connected = False
                    break
        
        heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
        heartbeat_thread.start()
        
    def handle_command(self, command_data):
        """处理接收到的命令"""
        try:
            command_id = command_data.get('command_id')
            payload = command_data.get('payload', {})
            
            print(f"收到命令: {payload}")
            
            # 这里应该包含实际处理命令的逻辑
            # 此处仅作为示例，简单地将命令值作为当前状态返回
            
            # 发送成功响应
            response = {
                "type": "command_response",
                "command_id": command_id,
                "status": "success",
                "payload": {
                    "current_state": payload,
                    "execution_time": 0.5
                }
            }
            
            self.send_message(response)
            
        except Exception as e:
            print(f"命令处理错误: {e}")
            # 发送错误响应
            error_response = {
                "type": "command_response",
                "command_id": command_data.get('command_id', ''),
                "status": "error",
                "payload": {
                    "error": str(e)
                }
            }
            self.send_message(error_response)
    
    def start_message_listener(self):
        """启动消息监听线程"""
        def listen_for_messages():
            self.buffer = ""
            while self.connected:
                try:
                    data = self.client.recv(1024).decode('utf-8')
                    if not data:
                        print("连接已关闭")
                        self.connected = False
                        break
                        
                    self.buffer += data
                    
                    # 处理完整的JSON消息
                    while '\n' in self.buffer:
                        line, self.buffer = self.buffer.split('\n', 1)
                        if line.strip():  # 确保不是空行
                            try:
                                message = json.loads(line)
                                
                                if message.get('type') == 'command':
                                    self.handle_command(message)
                                # 处理其他类型的消息
                                
                            except json.JSONDecodeError as e:
                                print(f"JSON解析错误: {e}, 原始数据: {line}")
                    
                except Exception as e:
                    print(f"消息监听错误: {e}")
                    self.connected = False
                    break
        
        listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
        listen_thread.start()
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.client:
            try:
                self.client.close()
            except:
                pass
        print("已断开连接")

# 使用示例
if __name__ == "__main__":
    # 替换为实际的服务器地址和设备信息
    client = NovaCloudTcpClient(
        host="nova-cloud-server.example.com",
        port=8100,
        device_id="550e8400-e29b-41d4-a716-446655440000",
        device_key="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    )
    
    if client.connect():
        try:
            # 模拟传感器数据上报
            for i in range(10):
                # 上报温湿度数据
                client.send_sensor_data({
                    "temperature": 20 + random.uniform(0, 10),
                    "humidity": 50 + random.uniform(0, 30),
                    "light": random.randint(0, 1000)
                })
                
                # 每隔几次上报一次设备状态
                if i % 3 == 0:
                    client.send_device_status({
                        "battery": 100 - i,
                        "signal": -50 - random.randint(0, 20),
                        "uptime": i * 60
                    })
                
                time.sleep(5)
                
            # 主线程等待
            print("客户端运行中，按Ctrl+C退出...")
            while client.connected:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("用户中断，正在退出...")
        finally:
            client.disconnect()
```

### 8.2 错误处理

良好的错误处理是稳定通信的关键。以下是一些常见错误处理策略：

1. **连接错误**：
   - 在连接失败时实现指数退避重连
   - 记录失败原因
   
2. **认证错误**：
   - 检查device_id和device_key是否正确
   - 确认设备在平台上是否处于激活状态
   
3. **发送失败**：
   - 实现消息重试机制
   - 断线重连后重新认证
   
4. **命令执行错误**：
   - 返回明确的错误信息
   - 实现部分成功的处理机制

错误处理示例：

```python
def connect_with_retry(client, max_retries=5):
    """带重试的连接方法"""
    retries = 0
    delay = 1  # 起始延迟1秒
    
    while retries < max_retries:
        try:
            print(f"尝试连接 (第{retries+1}次)...")
            if client.connect():
                return True
            
            retries += 1
            if retries < max_retries:
                print(f"连接失败，{delay}秒后重试...")
                time.sleep(delay)
                delay = min(delay * 2, 60)  # 指数退避，最大间隔60秒
        except Exception as e:
            print(f"连接异常: {e}")
            retries += 1
            if retries < max_retries:
                time.sleep(delay)
                delay = min(delay * 2, 60)
    
    print(f"达到最大重试次数({max_retries})，连接失败")
    return False
```

## 9. 最佳实践与注意事项

1. **连接管理**
   - 实现自动重连机制，使用指数退避策略
   - 避免频繁的连接和断开，这会增加服务器负载
   - 心跳超时后，主动断开并重新连接

2. **数据上报**
   - 合理安排数据上报频率，避免发送过于频繁的小数据包
   - 当有多个传感器数据时，尽量在一个消息中批量发送
   - 考虑数据压缩或聚合，减少流量消耗

3. **心跳机制**
   - 保持稳定的心跳频率，不要频繁变化
   - 如果连接不稳定，可适当增加心跳频率
   - 避免过于频繁的心跳（<30秒），以免增加服务器负担

4. **命令处理**
   - 始终响应接收到的命令，即使执行失败也要发送错误响应
   - 对于长时间执行的命令，可先发送"pending"状态，完成后再发送最终结果
   - 确保command_id在响应中正确返回，以便平台关联命令和响应

5. **安全与稳定性**
   - 不要在代码中硬编码设备密钥，应使用配置文件或环境变量
   - 实现消息队列机制，防止网络波动导致数据丢失
   - 使用TLS/SSL加密通信（如果平台支持）
   - 实现watchdog机制，在客户端程序异常时能够重启

6. **调试与日志**
   - 保留详细的通信日志，便于问题排查
   - 实现可调节的日志级别，生产环境中减少日志输出
   - 考虑实现远程日志收集机制

7. **资源使用**
   - 对于资源受限的设备，注意控制内存使用
   - 长时间运行时，注意处理潜在的内存泄漏问题
   - 优化JSON解析和生成，减少CPU和内存占用

8. **特殊情况处理**
   - 处理服务器返回的特殊指令（如果有），例如配置更新、固件升级提示等
   - 实现优雅关闭，确保在程序退出前关闭TCP连接
   - 考虑断网情况下的数据本地缓存和恢复上传机制 