"""
自定义异常类
定义项目中使用的各种异常类型
"""

from typing import Any, Dict, Optional


class AgentHubException(Exception):
    """项目基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class ConfigurationError(AgentHubException):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            details=details
        )


class PlatformError(AgentHubException):
    """平台相关错误"""
    
    def __init__(
        self,
        message: str,
        platform: str,
        platform_code: Optional[str] = None,
        http_status: Optional[int] = None
    ):
        details = {
            "platform": platform,
            "platform_code": platform_code,
            "http_status": http_status
        }
        super().__init__(
            message=message,
            code="PLATFORM_ERROR",
            details=details
        )


class PlatformConnectionError(PlatformError):
    """平台连接错误"""
    
    def __init__(self, platform: str, original_error: Optional[Exception] = None):
        message = f"无法连接到平台 {platform}"
        details = {
            "platform": platform,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            platform=platform
        )
        self.code = "PLATFORM_CONNECTION_ERROR"
        self.details.update(details)


class PlatformAuthError(PlatformError):
    """平台认证错误"""
    
    def __init__(self, platform: str, message: str = "认证失败"):
        super().__init__(
            message=f"{platform}: {message}",
            platform=platform
        )
        self.code = "PLATFORM_AUTH_ERROR"


class PlatformRateLimitError(PlatformError):
    """平台限流错误"""
    
    def __init__(
        self,
        platform: str,
        retry_after: Optional[int] = None,
        quota_reset: Optional[str] = None
    ):
        message = f"平台 {platform} 达到调用限制"
        details = {
            "platform": platform,
            "retry_after": retry_after,
            "quota_reset": quota_reset
        }
        super().__init__(
            message=message,
            platform=platform
        )
        self.code = "PLATFORM_RATE_LIMIT"
        self.details.update(details)


class TaskError(AgentHubException):
    """任务执行错误"""
    
    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        platform: Optional[str] = None
    ):
        details = {
            "task_id": task_id,
            "topic_id": topic_id,
            "platform": platform
        }
        super().__init__(
            message=message,
            code="TASK_ERROR",
            details=details
        )


class TaskTimeoutError(TaskError):
    """任务超时错误"""
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        timeout: Optional[int] = None,
        platform: Optional[str] = None
    ):
        message = f"任务执行超时"
        if timeout:
            message += f" (超时时间: {timeout}秒)"
        
        details = {
            "task_id": task_id,
            "timeout": timeout,
            "platform": platform
        }
        super().__init__(
            message=message,
            task_id=task_id,
            platform=platform
        )
        self.code = "TASK_TIMEOUT"
        self.details.update(details)


class TopicError(AgentHubException):
    """命题相关错误"""
    
    def __init__(
        self,
        message: str,
        topic_id: Optional[str] = None,
        generator: Optional[str] = None
    ):
        details = {
            "topic_id": topic_id,
            "generator": generator
        }
        super().__init__(
            message=message,
            code="TOPIC_ERROR",
            details=details
        )


class TopicGenerationError(TopicError):
    """命题生成错误"""
    
    def __init__(
        self,
        message: str = "命题生成失败",
        generator: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        details = {
            "generator": generator,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(
            message=message,
            generator=generator
        )
        self.code = "TOPIC_GENERATION_ERROR"
        self.details.update(details)


class StorageError(AgentHubException):
    """存储相关错误"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None
    ):
        details = {
            "operation": operation,
            "table": table
        }
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            details=details
        )


class DatabaseError(StorageError):
    """数据库错误"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        query: Optional[str] = None
    ):
        details = {
            "operation": operation,
            "table": table,
            "query": query
        }
        super().__init__(
            message=message,
            operation=operation,
            table=table
        )
        self.code = "DATABASE_ERROR"
        self.details.update(details)


class SchedulerError(AgentHubException):
    """调度器错误"""
    
    def __init__(
        self,
        message: str,
        job_id: Optional[str] = None,
        schedule: Optional[str] = None
    ):
        details = {
            "job_id": job_id,
            "schedule": schedule
        }
        super().__init__(
            message=message,
            code="SCHEDULER_ERROR",
            details=details
        )


class NotificationError(AgentHubException):
    """通知错误"""
    
    def __init__(
        self,
        message: str,
        notifier: Optional[str] = None,
        recipient: Optional[str] = None
    ):
        details = {
            "notifier": notifier,
            "recipient": recipient
        }
        super().__init__(
            message=message,
            code="NOTIFICATION_ERROR",
            details=details
        )


class ValidationError(AgentHubException):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_rule: Optional[str] = None
    ):
        details = {
            "field": field,
            "value": value,
            "validation_rule": validation_rule
        }
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class SecurityError(AgentHubException):
    """安全相关错误"""
    
    def __init__(
        self,
        message: str,
        security_type: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        details = {
            "security_type": security_type,
            "user_id": user_id
        }
        super().__init__(
            message=message,
            code="SECURITY_ERROR",
            details=details
        )


class EncryptionError(SecurityError):
    """加密错误"""
    
    def __init__(
        self,
        message: str = "加密/解密操作失败",
        operation: Optional[str] = None
    ):
        details = {
            "operation": operation
        }
        super().__init__(
            message=message,
            security_type="encryption"
        )
        self.code = "ENCRYPTION_ERROR"
        self.details.update(details) 