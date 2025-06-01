"""
配置模块测试
"""
import pytest
from pathlib import Path

from app.config.settings import get_settings


class TestSettings:
    """设置配置测试类"""
    
    def test_get_default_settings(self):
        """测试获取默认设置"""
        settings = get_settings()
        
        assert settings is not None
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'log_level')
    
    def test_settings_structure(self):
        """测试设置结构"""
        settings = get_settings()
        
        # 检查基本配置项存在
        expected_attrs = [
            'debug', 'log_level', 'app_name'
        ]
        
        for attr in expected_attrs:
            assert hasattr(settings, attr), f"Missing setting: {attr}" 