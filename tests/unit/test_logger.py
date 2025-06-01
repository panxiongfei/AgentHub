"""
日志模块测试
"""
import pytest
import logging

from app.core.logger import get_logger, setup_logging


class TestLogger:
    """日志系统测试类"""
    
    def test_get_logger(self):
        """测试获取日志器"""
        logger = get_logger("test")
        
        assert logger is not None
        assert logger.name == "test"
    
    def test_setup_logging(self):
        """测试日志设置"""
        # 测试不抛出异常
        setup_logging(debug=False)
        setup_logging(debug=True)
        
        # 验证日志器创建正常
        logger = get_logger("test_setup")
        assert logger is not None
    
    def test_logger_methods(self):
        """测试日志方法"""
        logger = get_logger("test_methods")
        
        # 测试日志方法存在且不抛出异常
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        logger.debug("Test debug message") 