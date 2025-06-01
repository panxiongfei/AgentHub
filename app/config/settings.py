"""
配置管理模块
使用 Pydantic Settings 进行配置管理，支持环境变量和配置文件
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str = "sqlite:///data/agenthub.db"
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="最大溢出连接数")


class SchedulerSettings(BaseSettings):
    """调度器配置"""
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    max_workers: int = Field(default=5, description="最大工作线程数")
    default_schedule: str = Field(default="0 9 * * *", description="默认调度表达式")
    job_defaults: Dict[str, Any] = Field(
        default={
            "coalesce": False,
            "max_instances": 3,
            "misfire_grace_time": 30
        },
        description="作业默认设置"
    )


class LoggingSettings(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    format: str = Field(default="json", description="日志格式")
    file: str = Field(default="logs/app.log", description="日志文件路径")
    max_bytes: int = Field(default=10 * 1024 * 1024, description="日志文件最大大小")
    backup_count: int = Field(default=5, description="日志文件备份数量")


class SecuritySettings(BaseSettings):
    """安全配置"""
    encryption_key: Optional[str] = Field(default=None, description="加密密钥")
    secret_key: str = Field(default="your-secret-key-here", description="应用密钥")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")


class NotificationSettings(BaseSettings):
    """通知配置"""
    smtp_server: Optional[str] = Field(default=None, description="SMTP服务器")
    smtp_port: int = Field(default=587, description="SMTP端口")
    smtp_username: Optional[str] = Field(default=None, description="SMTP用户名")
    smtp_password: Optional[str] = Field(default=None, description="SMTP密码")
    smtp_use_tls: bool = Field(default=True, description="是否使用TLS")
    
    # 默认通知接收者
    default_recipients: List[str] = Field(default=[], description="默认通知接收者")


class AppSettings(BaseSettings):
    """应用配置"""
    name: str = Field(default="AgentHub", description="应用名称")
    version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    api_prefix: str = Field(default="/api/v1", description="API前缀")
    
    # 跨域配置
    cors_origins: List[str] = Field(default=["*"], description="允许的跨域源")
    cors_allow_credentials: bool = Field(default=True, description="允许携带凭证")
    cors_allow_methods: List[str] = Field(default=["*"], description="允许的HTTP方法")
    cors_allow_headers: List[str] = Field(default=["*"], description="允许的HTTP头")


class PlatformSettings(BaseSettings):
    """平台配置"""
    enabled_platforms: List[str] = Field(default=[], description="启用的平台列表")
    default_timeout: int = Field(default=60, description="默认超时时间(秒)")
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_delay: int = Field(default=5, description="重试延迟(秒)")
    
    # 平台配置文件路径
    config_file: str = Field(default="configs/platforms.yaml", description="平台配置文件")


class ModelSettings(BaseSettings):
    """大模型配置"""
    
    # 默认模型提供商
    default_provider: str = "gemini"
    
    # Google Gemini 配置
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    gemini_base_url: str = "https://generativelanguage.googleapis.com"
    
    # DeepSeek 配置
    deepseek_api_key: str = ""
    default_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # OpenAI 配置 (备用)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Anthropic 配置 (备用)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # 通用配置
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    
    class Config:
        env_prefix = "MODEL_"


class Settings(BaseSettings):
    """全局配置"""
    
    app: AppSettings = Field(default_factory=AppSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    notification: NotificationSettings = Field(default_factory=NotificationSettings)
    platform: PlatformSettings = Field(default_factory=PlatformSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False
        extra = "ignore"
    
    @classmethod
    def load_from_yaml(cls, config_file: str) -> "Settings":
        """从 YAML 文件加载配置"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            # 如果配置文件不存在，返回默认配置
            return cls()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f) or {}
        
        # 合并环境变量
        return cls(**config_data)
    
    def save_to_yaml(self, config_file: str) -> None:
        """保存配置到 YAML 文件"""
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 转换为字典并保存
        config_data = self.dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, 
                     allow_unicode=True, indent=2)


@lru_cache()
def get_settings(config_file: str = "configs/settings.yaml") -> Settings:
    """获取配置实例（缓存）"""
    return Settings.load_from_yaml(config_file)


def get_platform_configs(config_file: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """获取平台配置"""
    if config_file is None:
        settings = get_settings()
        config_file = settings.platform.config_file
    
    config_path = Path(config_file)
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        platform_configs = yaml.safe_load(f) or {}
    
    return platform_configs.get('platforms', {})


def create_default_configs() -> None:
    """创建默认配置文件"""
    
    # 创建主配置文件
    settings = Settings()
    settings.save_to_yaml("configs/settings.yaml")
    
    # 创建平台配置文件
    platform_config = {
        "platforms": {
            "manus": {
                "enabled": True,
                "api_key": "${MANUS_API_KEY}",
                "base_url": "https://api.manus.com",
                "timeout": 60,
                "max_retries": 3
            },
            "skywork": {
                "enabled": True,
                "api_key": "${SKYWORK_API_KEY}",
                "base_url": "https://api.skywork.com",
                "timeout": 60,
                "max_retries": 3
            },
            "chatgpt_deepsearch": {
                "enabled": True,
                "api_key": "${OPENAI_API_KEY}",
                "base_url": "https://api.openai.com",
                "timeout": 60,
                "max_retries": 3
            },
            "kouzi": {
                "enabled": True,
                "api_key": "${KOUZI_API_KEY}",
                "base_url": "https://api.kouzi.com",
                "timeout": 60,
                "max_retries": 3
            }
        }
    }
    
    config_path = Path("configs/platforms.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(platform_config, f, default_flow_style=False,
                 allow_unicode=True, indent=2)
    
    # 创建示例 .env 文件
    env_content = """# 平台 API 密钥
MANUS_API_KEY=your_manus_api_key_here
SKYWORK_API_KEY=your_skywork_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
KOUZI_API_KEY=your_kouzi_api_key_here

# 通知配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# 安全配置
ENCRYPTION_KEY=your_encryption_key_here
SECRET_KEY=your_secret_key_here

# 应用配置
APP__DEBUG=false
LOGGING__LEVEL=INFO
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)


if __name__ == "__main__":
    # 创建默认配置
    create_default_configs()
    print("默认配置文件已创建") 