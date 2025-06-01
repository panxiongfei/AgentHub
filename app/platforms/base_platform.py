"""
平台基类
定义所有平台实现需要遵循的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.core.logger import get_logger


class TaskResult:
    """任务结果数据类"""
    
    def __init__(
        self,
        platform: str,
        task_id: str,
        success: bool,
        result: str,
        files: Optional[List[Path]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.platform = platform
        self.task_id = task_id
        self.success = success
        self.result = result
        self.files = files or []
        self.metadata = metadata or {}


class BasePlatform(ABC):
    """平台基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = get_logger(f"platform.{name}")
        
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试平台连接"""
        pass
    
    @abstractmethod
    async def submit_task(
        self,
        topic: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        提交任务
        
        Args:
            topic: 命题内容
            title: 任务标题
            **kwargs: 其他参数
            
        Returns:
            任务ID
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> str:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态 (pending/running/completed/failed)
        """
        pass
    
    @abstractmethod
    async def get_task_result(self, task_id: str) -> TaskResult:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        pass
    
    @abstractmethod
    async def download_files(self, task_id: str, download_dir: Path) -> List[Path]:
        """
        下载任务文件
        
        Args:
            task_id: 任务ID
            download_dir: 下载目录
            
        Returns:
            下载的文件路径列表
        """
        pass
    
    async def execute_full_task(
        self,
        topic: str,
        title: Optional[str] = None,
        download_dir: Optional[Path] = None,
        **kwargs
    ) -> TaskResult:
        """
        执行完整任务流程：提交->监控->获取结果->下载文件
        
        Args:
            topic: 命题内容
            title: 任务标题
            download_dir: 下载目录
            **kwargs: 其他参数
            
        Returns:
            任务结果
        """
        # 提交任务
        task_id = await self.submit_task(topic, title, **kwargs)
        self.logger.info(f"任务已提交: {task_id}")
        
        # 监控任务状态
        import asyncio
        while True:
            status = await self.get_task_status(task_id)
            self.logger.info(f"任务状态: {status}")
            
            if status in ["completed", "failed"]:
                break
            elif status in ["pending", "running"]:
                await asyncio.sleep(10)  # 等待10秒后再检查
            else:
                self.logger.warning(f"未知任务状态: {status}")
                await asyncio.sleep(10)
        
        # 获取任务结果
        result = await self.get_task_result(task_id)
        
        # 下载文件
        if download_dir and result.success:
            try:
                downloaded_files = await self.download_files(task_id, download_dir)
                result.files = downloaded_files
                self.logger.info(f"已下载 {len(downloaded_files)} 个文件")
            except Exception as e:
                self.logger.error(f"文件下载失败: {e}")
        
        return result 