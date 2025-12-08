"""
Loguru配置模块 - 基于配置系统的日志管理
"""
import os
import sys
from pathlib import Path
from loguru import logger
from typing import Dict, Any

from config.loader import get_config
from config.models import LogLevel, ConsoleHandlerConfig, FileHandlerConfig


class LoguruConfigManager:
    """Loguru配置管理器 - 基于配置系统"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoguruConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config = get_config()
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """基于配置设置日志系统"""
        # 移除默认配置
        logger.remove()
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 获取日志配置
        logging_config = self.config.logging
        
        # 设置控制台处理器
        if hasattr(logging_config.handlers, 'console') and logging_config.handlers.console.enabled:
            console_config = logging_config.handlers.console
            self._add_console_handler(console_config)
        
        # 设置文件处理器
        if hasattr(logging_config.handlers, 'file') and logging_config.handlers.file.enabled:
            file_config = logging_config.handlers.file
            self._add_file_handlers(file_config)
        
        # 设置特定日志器的级别
        self._configure_loggers(logging_config.loggers)
    
    def _add_console_handler(self, config: ConsoleHandlerConfig):
        """添加控制台处理器"""
        format_template = self._get_format_template("development")
        
        logger.add(
            sink=sys.stderr,
            format=format_template,
            level=config.level.value,
            colorize=config.colorize,
            backtrace=True,
            diagnose=True
        )
    
    def _add_file_handlers(self, config: FileHandlerConfig):
        """添加文件处理器"""
        format_template = self._get_format_template("production")
        
        # 主应用日志
        logger.add(
            sink=config.path,
            format=format_template,
            level=config.level.value,
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            encoding="utf-8"
        )
        
        # 错误日志（仅错误级别）
        error_log_path = str(Path(config.path).parent / "error.log")
        logger.add(
            sink=error_log_path,
            format=format_template,
            level="ERROR",
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            encoding="utf-8"
        )
        

    
    def _get_format_template(self, format_type: str) -> str:
        """获取格式模板"""
        formats = self.config.logging.format
        
        if format_type in formats:
            return formats[format_type]
        
        # 默认格式
        default_formats = {
            "development": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "production": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        }
        
        return default_formats.get(format_type, default_formats["production"])
    
    def _configure_loggers(self, loggers_config: Dict[str, str]):
        """配置特定日志器的级别"""
        # Loguru默认使用全局配置，这里可以设置特定模块的日志级别
        # 通过过滤器实现不同模块的级别控制
        pass
    
    def reconfigure(self):
        """重新配置日志系统"""
        self._initialized = False
        self.__init__()


def setup_logging(level: str = "INFO"):
    """初始化日志配置"""
    LoguruConfigManager()


def get_logger(name: str = None):
    """获取日志记录器实例"""
    setup_logging()
    if name:
        return logger.bind(module=name)
    return logger


def reconfigure_logging():
    """重新配置日志系统"""
    manager = LoguruConfigManager()
    manager.reconfigure()


# 预配置日志系统
setup_logging()