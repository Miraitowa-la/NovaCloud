# NovaCloud 项目重构设计文档 (FastAPI & TCP 增强版)

## 1. NovaCloud 项目重构概述

本文档旨在为 NovaCloud 物联网平台基于 FastAPI 和 Django 框架的重构项目提供全面的设计指导。重构的目标是构建一个功能强大、可扩展、易于维护且用户体验优秀的现代化物联网云平台。

### 1.1 项目目标

*   **现代化架构**：采用 FastAPI 构建高性能 API 服务，利用 Django 提供强大的后台管理、ORM 和用户认证系统，实现模块化、服务化的后端架构。
*   **功能完善**：全面覆盖现有功能，并优化用户体验，增强系统稳定性。
*   **高可扩展性**：设计灵活的系统架构，方便未来功能扩展和性能提升，支持多种通信协议接入。
*   **安全可靠**：遵循安全最佳实践，保障用户数据和设备通信安全。
*   **标准化开发**：建立统一的开发规范、API 规范 (基于 OpenAPI)，提升开发效率和代码质量。
*   **提升用户体验**：提供直观、易用、响应式的用户界面，支持**明暗主题切换**。

### 1.2 核心功能

*   用户认证与管理系统 (Django Auth)
*   邀请码系统与用户层级管理
*   物联网项目与设备管理 (增删改查)
*   传感器与执行器管理
*   设备通信 (TCP 为主，具备 MQTT, DDS 等协议的扩展能力)
*   实时数据监控与可视化
*   自动化策略引擎
*   全面的审计日志系统
*   统一的管理面板 (Django Admin)

### 1.3 技术选型

*   **API 框架**：FastAPI (最新稳定版) - 用于构建主要的业务 API 和数据处理接口。
*   **Web 框架 (辅助)**：Django (最新稳定版) - 用于 ORM、数据库迁移、管理后台、用户认证基础。
*   **数据库**：PostgreSQL (推荐生产环境), SQLite (开发环境)。
*   **数据校验与序列化**：Pydantic (FastAPI 内置)。
*   **前端**：HTML5, CSS3, JavaScript (原生为主，不依赖大型前端框架，确保轻量与可控)。
*   **设备通信协议**：TCP (主要，自定义应用层协议)，可扩展支持 MQTT, CoAP, DDS 等。
*   **TCP 服务器**：自定义实现 (如使用 `asyncio` 库)。
*   **消息队列**：RabbitMQ 或 Kafka (可选，用于策略引擎的异步任务、通知等)。
*   **缓存**：Redis (用于性能优化、存储临时状态如设备在线状态)。
*   **后台任务**：Celery (与 Django 集成，用于处理耗时任务，如邮件发送、复杂数据分析)。

## 2. 项目架构

### 2.1 整体架构

项目将结合 FastAPI 的高效 API 构建能力和 Django 的成熟生态系统。

*   **Web 服务器** (如 Uvicorn + Nginx)：处理 HTTP 请求，Uvicorn 作为 ASGI 服务器运行 FastAPI 和 Django (通过 ASGI 适配器)。
*   **FastAPI 应用层**：处理主要的 API 请求、业务逻辑、设备数据接入与处理、策略引擎的触发与执行。
*   **Django 应用层**：提供数据模型 (ORM)、数据库迁移、用户认证与会话管理、管理后台 (`admin.py`)。
*   **TCP 服务器**：独立的异步 TCP 服务，负责设备连接、认证、数据收发，并通过内部接口（如 Redis 或直接调用 FastAPI 服务）与 FastAPI 应用层交互。
*   **数据库层**：存储所有持久化数据。
*   **消息队列/后台任务**：处理异步、耗时操作。

### 2.2 后端模块设计

*   **`core` (Django App)**：项目全局配置、基础模型 (如时间戳基类)、共享工具函数。
*   **`accounts` (Django App)**：用户账户模型 (`User`, `UserProfile`)、认证逻辑、邀请码模型。Django Admin 用于用户管理。相关 API 可通过 FastAPI 暴露。
*   **`iot_devices` (Django App & FastAPI Routers)**：
    *   Django App: 定义项目 (Project)、设备 (Device)、传感器 (Sensor)、执行器 (Actuator) 的模型及其关系。
    *   FastAPI Routers: 提供这些资源 CRUD 操作的 API 接口。
*   **`tcp_server` (Python Module/Package)**：
    *   实现 TCP 服务器逻辑，包括设备连接管理、认证、心跳、数据包解析与封装。
    *   与 FastAPI 应用通过内部调用、Redis 消息或 HTTP API 通信，将设备数据推送到处理管道，或从 FastAPI 获取待下发命令。
*   **`strategy_engine` (Django App & FastAPI Routers)**：
    *   Django App: 定义策略 (Strategy)、条件 (Condition)、动作 (Action)、执行日志 (ExecutionLog) 模型。
    *   FastAPI Routers: 提供策略管理 API，策略引擎的触发逻辑可能部分在 FastAPI 或通过 Celery 任务实现。
*   **`admin_panel` (Django App)**：主要利用 Django Admin 自动生成强大的后台管理界面，用于管理用户、角色、设备元数据、审计日志等。可根据需要进行深度定制。
*   **FastAPI 主应用 (`main.py`)**：组织所有 FastAPI 路由、中间件、依赖项注入、启动配置。

### 2.3 API 与 URL 配置结构

*   **FastAPI**：使用 `APIRouter` 将不同功能的 API 接口模块化组织，然后在主应用中 `include_router`。自动生成 OpenAPI (Swagger UI, ReDoc) 文档。
*   **Django**：项目根 `urls.py` 主要包含 Django Admin 的路由、用户认证相关视图的路由 (如果不由 FastAPI 处理)，以及可能存在的少量传统 Django 视图路由。

### 2.4 配置文件

*   **环境变量 (`.env`)**：使用 `python-dotenv` 管理敏感配置 (数据库密码、`SECRET_KEY`、TCP 服务器端口、Redis 地址等)。
*   **FastAPI 配置**：通过 Pydantic `BaseSettings` 类加载配置。
*   **Django 配置 (`settings.py`)**：数据库连接、`INSTALLED_APPS` (注册 `core`, `accounts`, `iot_devices`, `strategy_engine`, `admin_panel` 等)、中间件、模板引擎等。确保 `SECRET_KEY` 等从环境变量加载。

## 3. 数据结构 (Django 模型)

模型定义将遵循 Django ORM 规范，作为系统的数据持久化核心。FastAPI 将通过 Pydantic 模型与 Django 模型交互 (例如，通过服务层转换)。

### 3.1 用户与权限模型

*   **`User` (Django 内置)**：存储用户的基本认证信息。
*   **`UserProfile` (`accounts` 应用)**：
    *   `user`: `OneToOneField` 关联到 `User` 模型。
    *   `role`: `ForeignKey` 关联到 `Role` 模型 (可选)。
    *   `parent_user`: `ForeignKey` 关联到 `User` 模型 (可选，`self`, `null=True`, `blank=True`, `on_delete=models.SET_NULL`, `related_name='child_profiles'`)，用于实现用户层级。
    *   其他用户扩展信息。
*   **`Role` (`admin_panel` 或 `accounts` 应用)**：
    *   `name`: `CharField` (角色名称，唯一)。
    *   `description`: `TextField` (可选)。
    *   `permissions`: `ManyToManyField` 关联到 Django 内置的 `Permission` 模型。
    *   建议在 `Role` 模型中添加一个 `codename` 字段，用于程序化引用。

### 3.2 物联网核心模型 (`iot_devices` 应用)

*   **`Project` (项目)**：
    *   `project_id`: `UUIDField` (项目唯一标识，`default=uuid.uuid4`, `editable=False`, `unique=True`)。
    *   `name`: `CharField`。
    *   `description`: `TextField` (可选)。
    *   `owner`: `ForeignKey` 关联到 `User`。
    *   `created_at`, `updated_at`: `DateTimeField` (自动管理)。
*   **`Device` (设备)**：
    *   `device_id`: `UUIDField` (设备唯一平台标识，`default=uuid.uuid4`, `editable=False`, `unique=True`)。
    *   `device_identifier`: `CharField` (设备物理标识，如 MAC 地址、IMEI，应在项目内或全局唯一，根据业务需求定)。
    *   `device_key`: `CharField` (设备认证密钥，自动生成，高强度)。
    *   `name`: `CharField`。
    *   `project`: `ForeignKey` 关联到 `Project`。
    *   `status`: `CharField` (设备状态，如: `online`, `offline`, `unregistered`, `error`, `disabled`)，建立索引。
    *   `last_seen`: `DateTimeField` (可选，`null=True`, `blank=True`)，建立索引。
    *   `created_at`, `updated_at`: `DateTimeField`。
*   **`Sensor` (传感器)**：
    *   `name`: `CharField`。
    *   `sensor_type`: `CharField` (如: `temperature`, `humidity`)。
    *   `unit`: `CharField` (如: `°C`, `%`, 可选)。
    *   `value_key`: `CharField` (用于从设备上报的 JSON 数据中提取该传感器值的键名)。
    *   `device`: `ForeignKey` 关联到 `Device`。
    *   `created_at`, `updated_at`: `DateTimeField`。
*   **`Actuator` (执行器)**：
    *   `name`: `CharField`。
    *   `actuator_type`: `CharField` (如: `switch`, `dimmer`)。
    *   `command_key`: `CharField` (用于平台下发控制命令时，在 JSON 数据中标识该执行器的键名)。
    *   `current_state_payload`: `JSONField` (执行器当前状态，由设备上报或平台记录，格式应与控制命令的值格式对应，可选)。
    *   `device`: `ForeignKey` 关联到 `Device`。
    *   `created_at`, `updated_at`: `DateTimeField`。

### 3.3 数据存储模型 (`iot_devices` 应用)

*   **`SensorData` (传感器数据记录)**：
    *   `sensor`: `ForeignKey` 关联到 `Sensor`。
    *   `timestamp`: `DateTimeField` (数据记录时间，`db_index=True`)。
    *   `value_float`: `FloatField` (可选)。
    *   `value_string`: `CharField` (可选)。
    *   `value_boolean`: `BooleanField` (可选)。
    *   `value_json`: `JSONField` (可选)。
    *   考虑使用 TimescaleDB (PostgreSQL 扩展) 或其他时序数据库优化存储和查询。
*   **`ActuatorCommandLog` (执行器命令及状态日志)**：
    *   `actuator`: `ForeignKey` 关联到 `Actuator`。
    *   `user`: `ForeignKey` 关联到 `User` (执行命令的用户，可选，系统触发则为空)。
    *   `command_payload`: `JSONField` (发送给设备的命令内容)。
    *   `status`: `CharField` (命令执行状态: `pending_send`, `sent`, `acknowledged`, `failed`, `timeout`)。
    *   `sent_at`: `DateTimeField` (命令发送时间)。
    *   `acknowledged_at`: `DateTimeField` (命令确认时间，可选，`null=True`)。
    *   `response_payload`: `JSONField` (设备返回的响应，可选)。
    *   `source`: `CharField` (命令来源：`user`, `api`, `strategy`)。

### 3.4 邀请码模型 (`accounts` 应用)

*   **`InvitationCode` (邀请码)**：
    *   `code`: `CharField` (邀请码字符串，唯一，自动生成，`db_index=True`)。
    *   `issuer`: `ForeignKey` 关联到 `User` (邀请码创建者)。
    *   `max_uses`: `PositiveIntegerField` (可选，null 表示无限制)。
    *   `times_used`: `PositiveIntegerField` (默认为 0)。
    *   `expires_at`: `DateTimeField` (可选，null 表示永不过期)。
    *   `is_active`: `BooleanField` (动态判断或手动设置，默认为 True)。
    *   `created_at`: `DateTimeField`。

### 3.5 策略引擎模型 (`strategy_engine` 应用)

*   **`Strategy` (策略)**：
    *   `name`: `CharField`。
    *   `description`: `TextField` (可选)。
    *   `owner`: `ForeignKey` 关联到 `User`。
    *   `project`: `ForeignKey` 关联到 `Project`。
    *   `is_enabled`: `BooleanField` (默认为 True)。
    *   `trigger_type`: `CharField` (如: `sensor_data`, `schedule`, `device_status`)。
    *   `created_at`, `updated_at`: `DateTimeField`。
*   **`ConditionGroup` (条件组)**：
    *   `strategy`: `ForeignKey` 关联到 `Strategy`。
    *   `logical_operator`: `CharField` (组内条件逻辑关系 `AND` / `OR`，默认为 `AND`)。
    *   `execution_order`: `PositiveIntegerField` (条件组执行顺序，用于复杂策略)。
*   **`Condition` (条件)**：
    *   `group`: `ForeignKey` 关联到 `ConditionGroup`。
    *   `data_source_type`: `CharField` (如 `sensor`, `device_attribute`, `time_of_day`)。
    *   `sensor`: `ForeignKey` 关联到 `Sensor` (如果数据源是传感器，可选)。
    *   `device_attribute`: `CharField` (如 `status`, `last_seen`，如果数据源是设备属性，可选)。
    *   `operator`: `CharField` (比较操作符，如: `>`, `<`, `=`, `!=`, `contains`)。
    *   `threshold_value_type`: `CharField` (阈值类型: `static`, `sensor_value`, `device_attribute_value`)。
    *   `threshold_value_static`: `CharField` (静态阈值)。
    *   `threshold_value_sensor`: `ForeignKey` 关联到 `Sensor` (动态阈值来源传感器，可选)。
    *   `threshold_value_device_attribute`: `CharField` (动态阈值来源设备属性，可选)。
*   **`Action` (动作)**：
    *   `strategy`: `ForeignKey` 关联到 `Strategy`。
    *   `action_type`: `CharField` (如: `control_actuator`, `send_notification`, `call_webhook`)。
    *   `execution_order`: `PositiveIntegerField` (同一策略内动作执行顺序)。
    *   `target_actuator`: `ForeignKey` 关联到 `Actuator` (可选)。
    *   `command_payload_template`: `JSONField` (控制执行器的命令内容模板，可使用变量)。
    *   `notification_recipient_type`: `CharField` (如 `user_email`, `custom_email`, `webhook`)
    *   `notification_recipient_value`: `CharField` (具体接收人或 URL)。
    *   `notification_message_template`: `TextField` (通知内容模板，可使用变量)。
    *   `webhook_method`: `CharField` (如 `GET`, `POST`, `PUT`)。
    *   `webhook_headers_template`: `JSONField` (可选)。
    *   `webhook_payload_template`: `JSONField` (可选)。
*   **`ExecutionLog` (策略执行日志)**：
    *   `strategy`: `ForeignKey` 关联到 `Strategy`。
    *   `triggered_at`: `DateTimeField`。
    *   `status`: `CharField` (执行状态: `success`, `failed`, `partial_success`, `pending`)。
    *   `trigger_details`: `JSONField` (触发时的上下文数据)。
    *   `action_results`: `JSONField` (每个动作的执行结果)。

### 3.6 审计日志模型 (`admin_panel` 或 `core` 应用)

*   **`AuditLog` (审计日志)**：
    *   `user`: `ForeignKey` 关联到 `User` (可选，系统操作则为空)。
    *   `action_type`: `CharField` (操作类型，使用预定义常量)。
    *   `target_content_type`: `ForeignKey` 关联到 `ContentType`。
    *   `target_object_id`: `PositiveIntegerField`。
    *   `target_object_repr`: `CharField` (操作对象的字符串表示，方便快速预览)。
    *   `target`: `GenericForeignKey` (`target_content_type`, `target_object_id`)。
    *   `details`: `JSONField` (操作详情，如修改前后的数据对比)。
    *   `ip_address`: `GenericIPAddressField` (可选)。
    *   `timestamp`: `DateTimeField` (自动记录，`db_index=True`)。

## 4. 核心功能详解

### 4.1 用户认证系统 (Django Auth + FastAPI)

*   **注册、登录、登出**：
    *   可使用 Django 内置的认证视图和表单，或通过 FastAPI 暴露相应 API 接口。
    *   FastAPI 接口通常使用 OAuth2 (密码流/令牌流) 或 JWT 进行认证。
    *   密码安全哈希存储 (Django 自动处理)。
    *   登录支持 "用户名或邮箱"。
*   **密码管理**：密码重置 (邮箱验证)、修改密码。API 接口由 FastAPI 提供。
*   **会话/令牌管理**：
    *   Django 部分可使用 session。
    *   FastAPI API 使用 Token (如 JWT)，Token 可存储在 Redis 中进行吊销管理。
*   **访问控制**：
    *   Django 视图使用 `@login_required` 或 `LoginRequiredMixin`。
    *   FastAPI 接口使用 `Depends` 和安全模式 (如 `OAuth2PasswordBearer`) 进行权限校验。

### 4.2 用户管理 (Django Admin)

*   通过 Django Admin 实现用户列表、创建、编辑、删除、角色分配、用户层级管理等。
*   管理员 (非超级管理员) 默认只能管理其 `child_profiles` 对应的用户，这需要在 Django Admin 的 `queryset` 方法中实现。

### 4.3 邀请码系统

*   **创建邀请码**：通过 FastAPI 接口，用户可以创建邀请码，设置使用次数和过期时间。
*   **使用邀请码**：注册时或用户中心，通过 FastAPI 接口提交邀请码。后端验证有效性，并将使用者的 `parent_user` 设置为邀请码的 `issuer`。
*   **查询与管理**：用户通过 FastAPI 接口查看自己创建的邀请码。
*   **审计**：记录到 `AuditLog`。

### 4.4 物联网设备管理 (FastAPI + Django Admin)

*   **项目管理 (CRUD)**：通过 FastAPI 接口。
*   **设备管理 (CRUD)**：通过 FastAPI 接口。自动生成 `device_id` 和 `device_key`。
*   **传感器/执行器管理 (CRUD)**：通过 FastAPI 接口。
*   **权限控制**：FastAPI 接口会校验用户是否有权操作相应资源 (基于项目所有者)。
*   Django Admin 提供后台管理视角。

### 4.5 设备通信 (TCP为主，可扩展)

*   **主要协议：TCP**
    *   **自定义 TCP 服务器 (`tcp_server` 模块)**：
        *   使用 `asyncio` 构建高性能异步 TCP 服务器。
        *   监听指定端口，处理设备连接请求。
    *   **连接与认证**：
        *   设备发起 TCP 连接后，发送认证包 (如：JSON 格式 `{ "type": "auth", "payload": { "device_id": "xxx", "device_key": "yyy" } }`)。
        *   TCP 服务器接收到认证包后，查询数据库 (或通过 FastAPI 接口) 验证 `device_id` 和 `device_key` 的有效性。
        *   认证成功后，服务器记录设备连接状态 (如在 Redis 中标记设备在线，并保存连接对象或其标识符)，并向设备回应认证成功。
        *   认证失败则关闭连接。
    *   **数据帧格式 (应用层协议)**：
        *   建议使用基于文本的 JSON 格式，每条消息以特定分隔符 (如 `\n`) 结束，或使用 Length-Prefix 方式。
        *   示例 JSON 消息结构：
            ```json
            // 设备上报数据
            { "type": "data", "timestamp": 1678886400, "payload": { "temp": 25.5, "hum": 60 } }
            // 设备上报状态
            { "type": "status", "payload": { "battery": 80, "rssi": -75 } }
            // 设备心跳
            { "type": "heartbeat" }
            // 服务器下发命令
            { "type": "command", "command_id": "cmd123", "payload": { "led_control": "ON" } }
            // 设备响应命令
            { "type": "command_response", "command_id": "cmd123", "status": "success", "payload": { "current_state": "ON" } }
            ```
    *   **数据处理流程**：
        *   TCP 服务器接收到设备数据帧，解析 JSON。
        *   根据 `type` 字段进行分发处理：
            *   `data`: 将 `payload` 推送到数据处理管道 (如 Celery 任务或直接调用 FastAPI 服务接口)，用于存储到 `SensorData`，更新设备 `last_seen`。
            *   `status`: 更新设备状态信息。
            *   `heartbeat`: 更新设备 `last_seen`，维持在线状态。
            *   `command_response`: 更新 `ActuatorCommandLog` 中的命令状态。
        *   设备下线 (连接断开或心跳超时) 时，更新设备状态为 `offline`。
    *   **命令下发流程**：
        *   用户通过 UI/API 触发命令，FastAPI 接口创建 `ActuatorCommandLog` 记录，状态为 `pending_send`。
        *   FastAPI 将命令 (包含目标 `device_id` 和命令内容) 推送到 TCP 服务器 (例如通过 Redis Pub/Sub 或内部任务队列)。
        *   TCP 服务器找到对应 `device_id` 的活动连接，将命令封装成 JSON 帧发送给设备。更新 `ActuatorCommandLog` 状态为 `sent`。
    *   **安全性**：必须使用 TLS 对 TCP 通信进行加密。
*   **协议可扩展性**：
    *   **MQTT**：未来可引入 MQTT Broker (如 EMQ X, Mosquitto)。FastAPI 应用可以作为 MQTT 客户端订阅和发布消息。设备使用 `device_id` 和 `device_key` 作为 MQTT 用户名密码。
    *   **DDS, CoAP 等**：根据需求，可以开发相应的适配器或网关服务，将这些协议的数据转换为内部标准格式，再送入 FastAPI 处理。
    *   设计统一的内部数据消息总线或服务接口，供不同协议接入模块调用。

### 4.6 数据可视化

*   前端通过调用 FastAPI 提供的 API 接口获取传感器历史数据、设备状态、执行器状态等。
*   使用 Chart.js 或类似库在前端展示时序图表、状态指示灯等。

### 4.7 策略引擎

*   **策略定义与管理**：通过 FastAPI 接口实现策略、条件、动作的 CRUD。
*   **策略触发与执行**：
    *   **数据驱动**：设备数据通过 TCP 服务器进入 FastAPI 后，在数据处理链路中，异步检查是否有策略的条件被满足。
    *   **时间驱动**：使用 Celery Beat 定期执行任务，检查基于时间计划的策略。
    *   **状态驱动**：设备状态变更 (online/offline) 时，触发检查相关策略。
    *   条件满足时，策略引擎 (可作为 FastAPI 内的服务或 Celery 任务) 按顺序执行策略中定义的动作 (如调用内部服务发送命令给 TCP 服务器，发送通知等)。
*   **策略日志**：执行过程和结果记录到 `ExecutionLog`。

### 4.8 审计日志系统

*   **记录范围**：通过 FastAPI 中间件、Django signals 或在关键业务逻辑中显式调用，记录用户操作、系统事件等。
*   **记录内容**：操作用户、时间、类型、对象、详情、IP。
*   **查询与筛选**：通过 Django Admin 查看和筛选审计日志。可开发专门的 FastAPI 接口供高级查询。

## 5. UI/UX 设计关注点 (非样式细节)

*   **明暗主题切换**：
    *   主要通过 CSS 变量实现。在 `:root` 中定义浅色主题变量，在 `body.dark-mode` (或类似选择器) 下覆盖这些变量为深色主题值。
    *   使用 JavaScript 提供切换按钮，点击时切换 `<body>` 的类名。
    *   用户的主题偏好应存储在 `localStorage` 中，以便下次访问时恢复。
    *   可考虑检测操作系统偏好 (`prefers-color-scheme`) 作为首次访问的默认主题。
*   **响应式设计**：确保在桌面、平板、移动设备上均有良好体验。
*   **可访问性 (A11y)**：遵循 WCAG 标准，确保应用对残障用户友好。

## 6. 设备、传感器、执行器数据构造 (JSON 消息体)

以下为设备与平台间通过 TCP (或其他协议) 传输的 JSON 消息体内容的通用定义。

### 6.1 设备 (`Device`) 元数据

*   `device_id`: 字符串 (UUID)。平台分配。
*   `device_identifier`: 字符串。设备物理ID。
*   `device_key`: 字符串。平台分配，用于认证。
*   `name`: 字符串。用户定义。
*   `status`: 字符串 (`online`, `offline`, `disabled`等)。

### 6.2 传感器 (`Sensor`) 元数据

*   `name`: 字符串。
*   `sensor_type`: 字符串枚举 (如 `temperature`, `humidity`, `gps_location`)。
*   `unit`: 字符串 (如 `°C`, `%`)。
*   `value_key`: 字符串 (用于解析上报数据包中的传感器值)。

### 6.3 执行器 (`Actuator`) 元数据

*   `name`: 字符串。
*   `actuator_type`: 字符串枚举 (如 `switch`, `dimmer`, `rgb_light`)。
*   `command_key`: 字符串 (用于构造下发命令包中的执行器标识)。
*   `current_state_payload`: JSON 对象 (表示当前状态)。

### 6.4 数据上报与命令下发格式 (应用层 JSON 示例)

此部分内容已在 "4.5 设备通信" 的 "数据帧格式" 中通过 `type` 字段区分并举例说明。关键在于定义清晰的 `type` 和 `payload` 结构。

*   **设备数据上报 (`type: "data"`)**:
    ```json
    {
        "type": "data",
        "timestamp": 1678886400, // Unix timestamp, 设备本地时间
        "payload": {
            "temperature_living_room": 22.5, // value_key: "temperature_living_room"
            "humidity_living_room": 45.2,
            "main_door_status": "closed",
            "gps_coordinates": { "latitude": 34.0522, "longitude": -118.2437 }
        }
    }
    ```
*   **设备状态上报 (`type: "status"`)**:
    ```json
    {
        "type": "status",
        "payload": {
            "battery_level": 85,
            "signal_strength": -75,
            "firmware_version": "1.2.3"
        }
    }
    ```
*   **平台命令下发 (`type: "command"`)**:
    ```json
    {
        "type": "command",
        "command_id": "cmd_uuid_123abc", // 用于追踪响应
        "payload": {
            "living_room_light": "ON", // command_key: "living_room_light"
            "ac_temperature_setpoint": 24,
            "rgb_strip_1": { // command_key: "rgb_strip_1"
                "color": {"r": 255, "g": 0, "b": 0},
                "brightness": 80
            }
        }
    }
    ```
*   **设备命令响应 (`type: "command_response"`)**:
    ```json
    {
        "type": "command_response",
        "command_id": "cmd_uuid_123abc",
        "status": "success", // "success", "failed", "invalid_command"
        "message": "Light turned on successfully", // 可选
        "payload": { // 可选，返回执行后的状态
            "living_room_light": "ON"
        }
    }
    ```

## 7. 开发规范与最佳实践

### 7.1 Python 代码规范

*   严格遵循 **PEP 8**。使用 Black, Flake8, isort 自动化格式化和检查。
*   清晰的注释和 Docstrings (Google 风格或 reStructuredText)。
*   类型提示 (Type Hinting) 全面覆盖。

### 7.2 FastAPI 最佳实践

*   **Pydantic 模型**：用于请求/响应体定义、数据校验和序列化。
*   **依赖注入 (`Depends`)**：管理依赖项、共享逻辑 (如获取当前用户、数据库会话)。
*   **异步优先 (`async/await`)**：对所有 I/O 密集型操作使用异步，充分发挥 FastAPI 性能。
*   **路由器 (`APIRouter`)**：按功能模块组织 API 接口。
*   **后台任务 (`BackgroundTasks`)**：处理请求后需要执行的非阻塞轻量级任务。
*   **错误处理**：使用自定义异常处理器和 FastAPI 的 `HTTPException`。
*   **Testing**：使用 `TestClient` 编写单元测试和集成测试。

### 7.3 Django 最佳实践 (用于 ORM 和 Admin)

*   **模型 (Models)**：保持精简，复杂查询逻辑封装在自定义 Manager 或 QuerySet 方法中。`__str__` 方法必不可少。
*   **Admin 定制**：充分利用 Django Admin 的可定制性，提供高效的管理后台。
*   **数据库迁移**：熟练使用 `makemigrations` 和 `migrate`。
*   **Service 层 (可选)**：可在 FastAPI 和 Django 之间引入一个 Service 层，封装复杂的业务逻辑和与 ORM 的交互，使 API 视图更轻量。

### 7.4 前端规范 (原生 JS/HTML/CSS)

*   语义化 HTML，模块化 CSS (如 BEM)，避免全局 JS 变量。
*   代码风格统一，使用 ESLint/Prettier。

### 7.5 安全规范

*   **认证与授权**：FastAPI 的 OAuth2/JWT，Django 的 Session/Permission 体系。
*   **输入验证**：Pydantic 严格验证所有输入。
*   **输出编码**：Django 模板自动处理，API 返回 JSON 时注意内容安全。
*   **API 安全**：HTTPS，速率限制 (如使用 `slowapi`)，CORS 配置。
*   **TCP 通信安全**：强制 TLS 加密。
*   **依赖管理**：使用 `pip-tools` 或 Poetry 管理依赖，定期更新。

### 7.6 版本控制 (Git)

*   遵循 Git Flow 或 GitHub Flow。Commit Message 规范化。Code Review。

### 7.7 测试策略

*   **单元测试**：FastAPI 接口 (`TestClient`)，Django 模型/工具函数。
*   **集成测试**：测试 FastAPI 与 Django ORM、TCP 服务器与后端服务的交互。
*   **TCP 服务器测试**：模拟设备连接和数据交换进行测试。
*   **测试覆盖率**：使用 `coverage.py`。
*   **CI/CD**：GitHub Actions, GitLab CI 等。

## 8. 注意事项

*   **安全性**：贯穿始终，包括传输安全、数据安全、认证授权。
*   **可扩展性**：架构设计应易于横向扩展 FastAPI 应用实例和 TCP 服务器实例。
*   **性能**：关注数据库查询优化 (Django ORM `select_related`, `prefetch_related`)，异步处理，缓存策略 (Redis)。
*   **数据一致性**：在分布式操作或异步任务中，考虑使用事务、幂等性设计。
*   **错误处理与日志**：结构化日志 (如 JSON 格式)，统一的错误码。
*   **文档**：FastAPI 自动生成 API 文档，补充架构文档、部署文档。
*   **监控与告警**：集成 Prometheus, Grafana 等进行系统监控和告警。
*   **混合架构管理**：明确 FastAPI 和 Django 的职责边界，避免混乱。