# 用户相关操作
ACTION_USER_LOGIN = 'user_login'
ACTION_USER_LOGOUT = 'user_logout'
ACTION_USER_REGISTER = 'user_register'
ACTION_USER_UPDATE = 'user_update'
ACTION_USER_DELETE = 'user_delete'
ACTION_USER_PASSWORD_CHANGE = 'user_password_change'
ACTION_USER_PASSWORD_RESET = 'user_password_reset'

# 项目相关操作
ACTION_PROJECT_CREATE = 'project_create'
ACTION_PROJECT_UPDATE = 'project_update'
ACTION_PROJECT_DELETE = 'project_delete'

# 设备相关操作
ACTION_DEVICE_CREATE = 'device_create'
ACTION_DEVICE_UPDATE = 'device_update'
ACTION_DEVICE_DELETE = 'device_delete'
ACTION_DEVICE_ONLINE = 'device_online'
ACTION_DEVICE_OFFLINE = 'device_offline'

# 传感器/执行器相关操作
ACTION_SENSOR_CREATE = 'sensor_create'
ACTION_SENSOR_UPDATE = 'sensor_update'
ACTION_SENSOR_DELETE = 'sensor_delete'
ACTION_ACTUATOR_CREATE = 'actuator_create'
ACTION_ACTUATOR_UPDATE = 'actuator_update'
ACTION_ACTUATOR_DELETE = 'actuator_delete'
ACTION_ACTUATOR_COMMAND = 'actuator_command'

# 策略引擎相关操作
ACTION_STRATEGY_CREATE = 'strategy_create'
ACTION_STRATEGY_UPDATE = 'strategy_update'
ACTION_STRATEGY_DELETE = 'strategy_delete'
ACTION_STRATEGY_ENABLE = 'strategy_enable'
ACTION_STRATEGY_DISABLE = 'strategy_disable'
ACTION_STRATEGY_EXECUTION = 'strategy_execution'

# 邀请码相关操作
ACTION_INVITATION_CREATE = 'invitation_create'
ACTION_INVITATION_USE = 'invitation_use'

# 系统操作
ACTION_SYSTEM_STARTUP = 'system_startup'
ACTION_SYSTEM_SHUTDOWN = 'system_shutdown'
ACTION_SYSTEM_CONFIG_CHANGE = 'system_config_change'

# 审计日志操作类型选项
AUDIT_ACTION_CHOICES = [
    # 用户相关
    (ACTION_USER_LOGIN, '用户登录'),
    (ACTION_USER_LOGOUT, '用户登出'),
    (ACTION_USER_REGISTER, '用户注册'),
    (ACTION_USER_UPDATE, '用户信息更新'),
    (ACTION_USER_DELETE, '用户删除'),
    (ACTION_USER_PASSWORD_CHANGE, '用户密码修改'),
    (ACTION_USER_PASSWORD_RESET, '用户密码重置'),
    
    # 项目相关
    (ACTION_PROJECT_CREATE, '项目创建'),
    (ACTION_PROJECT_UPDATE, '项目更新'),
    (ACTION_PROJECT_DELETE, '项目删除'),
    
    # 设备相关
    (ACTION_DEVICE_CREATE, '设备创建'),
    (ACTION_DEVICE_UPDATE, '设备更新'),
    (ACTION_DEVICE_DELETE, '设备删除'),
    (ACTION_DEVICE_ONLINE, '设备上线'),
    (ACTION_DEVICE_OFFLINE, '设备离线'),
    
    # 传感器/执行器相关
    (ACTION_SENSOR_CREATE, '传感器创建'),
    (ACTION_SENSOR_UPDATE, '传感器更新'),
    (ACTION_SENSOR_DELETE, '传感器删除'),
    (ACTION_ACTUATOR_CREATE, '执行器创建'),
    (ACTION_ACTUATOR_UPDATE, '执行器更新'),
    (ACTION_ACTUATOR_DELETE, '执行器删除'),
    (ACTION_ACTUATOR_COMMAND, '执行器命令发送'),
    
    # 策略引擎相关
    (ACTION_STRATEGY_CREATE, '策略创建'),
    (ACTION_STRATEGY_UPDATE, '策略更新'),
    (ACTION_STRATEGY_DELETE, '策略删除'),
    (ACTION_STRATEGY_ENABLE, '策略启用'),
    (ACTION_STRATEGY_DISABLE, '策略禁用'),
    (ACTION_STRATEGY_EXECUTION, '策略执行'),
    
    # 邀请码相关
    (ACTION_INVITATION_CREATE, '邀请码创建'),
    (ACTION_INVITATION_USE, '邀请码使用'),
    
    # 系统操作
    (ACTION_SYSTEM_STARTUP, '系统启动'),
    (ACTION_SYSTEM_SHUTDOWN, '系统关闭'),
    (ACTION_SYSTEM_CONFIG_CHANGE, '系统配置变更'),
] 