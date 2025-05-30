# NovaCloud 通信工具使用指南

本文档详细介绍了NovaCloud项目中的TCP通信相关工具，包括设备模拟器、测试工具和TCP服务器实现。这些工具主要在`communication_handler`目录下。

## 1. TCP服务器 (run_tcp_server.py)

### 功能介绍

`run_tcp_server.py`是一个Django管理命令，用于启动NovaCloud的TCP服务器，处理物联网设备的连接认证、数据上报、状态更新和心跳保活。该服务器基于Python的`asyncio`库实现，支持异步并发处理多设备连接。

### 使用方法

```bash
# 基本用法
python manage.py run_tcp_server

# 自定义主机和端口
python manage.py run_tcp_server --host 192.168.1.100 --port 9999
```

### 参数说明

| 参数 | 类型 | 默认值                                     | 说明 |
|------|------|-----------------------------------------|------|
| `--host` | 字符串 | `0.0.0.0` 或配置文件中的`NOVA_TCP_SERVER_HOST` | TCP服务器监听地址 |
| `--port` | 整数 | `8100` 或配置文件中的`NOVA_TCP_SERVER_PORT`    | TCP服务器监听端口 |

### 功能特性

1. **设备认证**：验证设备的`device_id`和`device_key`，认证成功后建立持久连接。
2. **数据处理**：处理设备上报的传感器数据，并存储到数据库。
3. **状态管理**：实时更新设备的在线/离线状态，记录最后活动时间。
4. **心跳机制**：支持设备发送心跳包保持连接活跃。

### 协议规范

服务器使用基于JSON的协议，每条消息以换行符(`\n`)结束：

1. **认证消息**：
   ```json
   {"type": "auth", "device_id": "uuid-str", "device_key": "key-str"}
   ```

2. **数据上报**：
   ```json
   {"type": "data", "timestamp": 1234567890, "payload": {"sensor_key1": value1, "sensor_key2": value2}}
   ```

3. **心跳包**：
   ```json
   {"type": "heartbeat", "timestamp": 1234567890}
   ```

4. **状态上报**：
   ```json
   {"type": "status", "payload": {"battery": 80, "rssi": -75}}
   ```

### 注意事项

- 服务器需要在Django环境下运行，确保数据库已配置正确。
- 设备断开连接后，状态会自动更新为"offline"。
- 为提高安全性，生产环境建议配置TLS加密（当前版本未实现）。

## 2. 测试客户端 (test_client.py)

### 功能介绍

`test_client.py`是一个模拟物联网设备的测试客户端，用于测试TCP服务器的设备认证、数据通信和心跳机制功能。

### 使用方法

```bash
# 基本用法（需提供设备ID和密钥）
python communication_handler/test_client.py --device_id <设备UUID> --device_key <设备密钥>

# 使用自动数据生成模式
python communication_handler/test_client.py --device_id <设备UUID> --device_key <设备密钥> --auto

# 启用心跳机制
python communication_handler/test_client.py --device_id <设备UUID> --device_key <设备密钥> --heartbeat

# 完整示例
python communication_handler/test_client.py --device_id 550e8400-e29b-41d4-a716-446655440000 --device_key abcdef1234567890 --host 192.168.1.100 --port 9999 --auto --heartbeat --heartbeat-interval 20
```

### 参数说明

| 参数 | 类型 | 默认值         | 说明 |
|------|------|-------------|------|
| `--host` | 字符串 | `127.0.0.1` | TCP服务器地址 |
| `--port` | 整数 | `8100`      | TCP服务器端口 |
| `--device_id` | 字符串 | 必填          | 设备ID (UUID格式) |
| `--device_key` | 字符串 | 必填          | 设备密钥 (128位字符串) |
| `--auto` | 开关 | 禁用          | 自动生成并发送模拟传感器数据 |
| `--heartbeat` | 开关 | 禁用          | 启用心跳机制 |
| `--heartbeat-interval` | 整数 | `30`        | 心跳间隔，单位为秒 |

### 运行模式

1. **手动模式**（不使用`--auto`）：
   - 提供交互式菜单，用户可选择发送自定义消息、传感器数据、心跳包或状态信息。
   - 适合深入测试特定功能或调试通信问题。

2. **自动模式**（使用`--auto`）：
   - 每2秒自动生成随机传感器数据并发送。
   - 适合压力测试或模拟真实设备的持续数据上报。

### 示例：手动模式操作

启动客户端后，您将看到如下选项：
```
请选择操作:
1. 发送自定义消息
2. 发送传感器数据
3. 发送心跳包
4. 发送状态信息
5. 退出
```

- 选择选项1后，可以输入自定义消息。
- 选择选项2后，可以输入温度、湿度、光照和运动检测值。
- 选择选项3将发送心跳包。
- 选择选项4将发送设备状态信息。

### 注意事项

- 确保提供的设备ID和密钥存在于系统中，否则认证将失败。
- 心跳线程在主线程退出时会自动终止。
- 如果需要模拟设备长时间运行，建议使用`--auto`和`--heartbeat`选项。

## 3. 测试设备创建工具 (create_test_device.py)

### 功能介绍

`create_test_device.py`用于快速创建测试用的项目和设备，便于测试TCP通信功能。工具会创建一个项目、一个设备、一个传感器和一个执行器。

### 使用方法

```bash
# 使用系统中第一个用户创建测试设备
python communication_handler/create_test_device.py

# 指定用户创建测试设备
python communication_handler/create_test_device.py --username admin
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--username` | 字符串 | 系统中第一个用户 | 指定创建测试设备的用户 |

### 创建的测试数据

1. **项目**：名为"TCP测试项目"，描述为"用于测试TCP设备通信的项目"。
2. **设备**：名为"TCP测试设备"，物理标识为"TEST_DEVICE_001"，状态为"unregistered"。
3. **传感器**：名为"温度传感器"，类型为"temperature"，单位为"°C"，数据键名为"temperature"。
4. **执行器**：名为"灯光开关"，类型为"switch"，命令键名为"light_switch"，初始状态为"OFF"。

### 输出信息

工具会输出创建的设备ID和设备密钥，可以直接用于测试客户端：

```
已创建新设备: TCP测试设备
设备ID: 550e8400-e29b-41d4-a716-446655440000
设备密钥: abcdef1234567890abcdef1234567890

要使用此设备测试TCP认证，请运行:
python communication_handler/test_client.py --device_id 550e8400-e29b-41d4-a716-446655440000 --device_key abcdef1234567890abcdef1234567890
```

### 注意事项

- 如果同名项目或设备已存在，工具会使用现有实例而不是创建新的。
- 该工具需要在Django环境下运行，确保数据库已配置正确。

## 4. 设备列表查询工具 (list_devices.py)

### 功能介绍

`list_devices.py`用于列出系统中所有项目和设备的信息，包括设备ID和密钥，便于选择设备进行TCP通信测试。

### 使用方法

```bash
# 列出所有项目和设备
python communication_handler/list_devices.py

# 只列出特定项目的设备
python communication_handler/list_devices.py --project_id <项目UUID>
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--project_id` | 字符串 | 无 | 项目ID，用于筛选特定项目的设备 |

### 输出信息

工具会输出系统中所有项目及其下的设备详情：

```
系统中共有 2 个项目:

项目: 智能家居 (ID: 123e4567-e89b-12d3-a456-426614174000)
所有者: admin
  设备数量: 1

  ------------------------------------------------------------
  设备名称: 客厅温控器
  设备ID: 550e8400-e29b-41d4-a716-446655440000
  设备密钥: abcdef1234567890abcdef1234567890
  设备状态: online
  上次在线: 2023-10-25 14:30:45
  传感器数量: 2
  执行器数量: 1
```

### 注意事项

- 该工具会显示设备密钥，注意信息安全。
- 输出最后会提示如何使用显示的设备ID和密钥来测试TCP通信。

## 5. 传感器数据查询工具 (check_sensor_data.py)

### 功能介绍

`check_sensor_data.py`用于查询数据库中已存储的传感器数据，可以按设备筛选，便于验证数据上报功能是否正常工作。

### 使用方法

```bash
# 查询所有设备的传感器数据（每个传感器显示最新10条）
python communication_handler/check_sensor_data.py

# 查询特定设备的传感器数据
python communication_handler/check_sensor_data.py --device_id <设备UUID>

# 指定每个传感器显示的数据条数
python communication_handler/check_sensor_data.py --device_id <设备UUID> --limit 20
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--device_id` | 字符串 | 无 | 设备ID，用于筛选特定设备的数据 |
| `--limit` | 整数 | `10` | 每个传感器显示的最大数据条数 |

### 输出格式

工具会输出设备信息和每个传感器的数据：

```
设备: TCP测试设备 (ID: 550e8400-e29b-41d4-a716-446655440000)
所属项目: TCP测试项目
状态: online
上次在线: 2023-10-25 15:45:20
传感器数量: 1

  传感器: 温度传感器 (类型: temperature, 单位: °C)
  数据键名: temperature
  数据记录数: 120

  最新 10 条数据记录:
  ------------------------------------------------------------
         时间戳          |             值               
  ------------------------------------------------------------
   2023-10-25 15:45:18   | 24.5                       
   2023-10-25 15:45:16   | 24.3                       
   ...
```

### 注意事项

- 该工具需要在Django环境下运行，确保数据库已配置正确。
- 如果指定的设备ID不存在，工具会报错并退出。
- 如果传感器没有数据，会显示"尚无数据记录"。

## 常见问题与解决方案

### 1. 无法连接到TCP服务器

**问题**：测试客户端无法连接到TCP服务器。
**解决方案**：
- 确认TCP服务器已启动 (`python manage.py run_tcp_server`)。
- 检查主机和端口设置是否正确。
- 检查防火墙设置，确保端口已开放。

### 2. 设备认证失败

**问题**：测试客户端连接成功但认证失败。
**解决方案**：
- 使用 `list_devices.py` 确认设备ID和密钥是否正确。
- 检查设备是否在数据库中存在。
- 如果设备不存在，使用 `create_test_device.py` 创建测试设备。

### 3. 传感器数据未存储

**问题**：发送了传感器数据，但在数据库中找不到。
**解决方案**：
- 检查发送的数据格式是否正确。
- 确认传感器的 `value_key` 与发送的数据键名匹配。
- 使用 `check_sensor_data.py` 验证数据是否成功存储。

## 最佳实践

1. **开发测试流程**：
   - 使用 `create_test_device.py` 创建测试设备。
   - 启动TCP服务器 (`python manage.py run_tcp_server`)。
   - 使用测试客户端发送模拟数据。
   - 使用 `check_sensor_data.py` 验证数据存储。

2. **服务器启动**：
   - 在开发环境，使用 `python manage.py run_tcp_server` 单独启动。
   - 在生产环境，考虑使用 systemd 服务或 Supervisor 确保服务自启动和故障重启。

3. **设备认证安全**：
   - 避免在代码和版本控制中硬编码设备密钥。
   - 定期更新设备密钥以提高安全性。

4. **故障排查**：
   - 使用 `--auto` 和 `--heartbeat` 选项进行长时间测试，验证服务稳定性。
   - 观察服务器日志，识别可能的异常情况。 