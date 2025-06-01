"""
平台工厂模块
支持创建各平台的实例
"""

from typing import List, Dict, Any
from app.core.logger import get_logger
from app.core.exceptions import PlatformError
from app.config.settings import get_platform_configs
from app.platforms.base_platform import BasePlatform


class MockPlatform:
    """模拟平台类（用于未实现的平台）"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"platform.{name}")
    
    async def test_connection(self) -> bool:
        """测试连接"""
        self.logger.info(f"测试 {self.name} 平台连接（模拟）")
        return True


class PlatformFactory:
    """平台工厂"""
    
    def __init__(self):
        self.logger = get_logger("platform_factory")
        self.available_platforms = [
            "manus",
            "skywork", 
            "chatgpt_deepsearch",
            "coze_space",
            "kouzi"
        ]
        self._platform_configs = None
    
    def get_available_platforms(self) -> List[str]:
        """获取可用平台列表"""
        return self.available_platforms.copy()
    
    def _get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """获取平台配置"""
        if self._platform_configs is None:
            self._platform_configs = get_platform_configs()
        
        return self._platform_configs.get(platform_name, {})
    
    async def create_platform(self, platform_name: str) -> BasePlatform:
        """创建平台实例"""
        if platform_name not in self.available_platforms:
            raise PlatformError(f"不支持的平台: {platform_name}", platform=platform_name)
        
        config = self._get_platform_config(platform_name)
        
        # 根据平台名称创建对应的实例
        if platform_name == "manus":
            from app.platforms.manus_platform import ManusPlatform
            platform = ManusPlatform(config)
            self.logger.info(f"创建 Manus 平台实例")
            return platform
        
        elif platform_name == "skywork":
            from app.platforms.skywork_platform import SkyworkPlatform
            platform = SkyworkPlatform(config)
            self.logger.info(f"创建 Skywork 平台实例")
            return platform
        
        elif platform_name == "chatgpt_deepsearch":
            from app.platforms.chatgpt_platform import ChatGPTPlatform
            platform = ChatGPTPlatform(config)
            self.logger.info(f"创建 ChatGPT DeepSearch 平台实例")
            return platform
        
        elif platform_name == "coze_space":
            from app.platforms.coze_space_platform import CozeSpacePlatform
            platform = CozeSpacePlatform(config)
            self.logger.info(f"创建扣子空间平台实例")
            return platform
        
        elif platform_name == "kouzi":
            # TODO: 实现扣子平台（其他版本）
            self.logger.warning(f"扣子平台（其他版本）尚未实现，使用模拟实例")
            return MockPlatform(platform_name)
        
        else:
            raise PlatformError(f"未知平台: {platform_name}", platform=platform_name) 