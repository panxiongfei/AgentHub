"""
日志系统模块
使用 structlog 进行结构化日志记录
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor


def setup_logging(
    debug: bool = False,
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    log_format: str = "json"
) -> None:
    """
    设置日志系统
    
    Args:
        debug: 是否启用调试模式
        log_file: 日志文件路径
        log_level: 日志级别
        log_format: 日志格式 (json/text)
    """
    
    # 设置日志级别
    level = logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建日志目录
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置处理器
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # 根据格式选择渲染器
    if log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
    
    # 配置 structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 配置标准库日志
    handlers = []
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    handlers.append(console_handler)
    
    # 文件处理器
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        handlers.append(file_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers
    )
    
    # 配置第三方库的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    return structlog.get_logger(name)


class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    def log_request(
        self,
        method: str,
        url: str,
        status_code: int,
        duration: float,
        request_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录请求日志"""
        log_data = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": request_id,
        }
        
        if extra:
            log_data.update(extra)
        
        if status_code >= 400:
            self.logger.error("HTTP request failed", **log_data)
        else:
            self.logger.info("HTTP request completed", **log_data)


class TaskLogger:
    """任务日志记录器"""
    
    def __init__(self):
        self.logger = get_logger("task")
    
    def log_task_start(
        self,
        task_id: str,
        platform: str,
        topic_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录任务开始"""
        log_data = {
            "task_id": task_id,
            "platform": platform,
            "topic_id": topic_id,
            "event": "task_start"
        }
        
        if extra:
            log_data.update(extra)
        
        self.logger.info("Task started", **log_data)
    
    def log_task_success(
        self,
        task_id: str,
        platform: str,
        duration: float,
        result_length: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录任务成功"""
        log_data = {
            "task_id": task_id,
            "platform": platform,
            "duration_ms": round(duration * 1000, 2),
            "result_length": result_length,
            "event": "task_success"
        }
        
        if extra:
            log_data.update(extra)
        
        self.logger.info("Task completed successfully", **log_data)
    
    def log_task_failure(
        self,
        task_id: str,
        platform: str,
        error: str,
        duration: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """记录任务失败"""
        log_data = {
            "task_id": task_id,
            "platform": platform,
            "error": error,
            "event": "task_failure"
        }
        
        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if extra:
            log_data.update(extra)
        
        self.logger.error("Task failed", **log_data)


# 全局日志记录器实例
request_logger = RequestLogger()
task_logger = TaskLogger() 