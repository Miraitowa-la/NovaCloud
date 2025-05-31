from django.apps import AppConfig


class StrategyEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'strategy_engine'

    def ready(self):
        """
        当应用准备好时，连接信号处理器
        """
        # 导入信号模块以注册信号处理器
        import strategy_engine.signals
