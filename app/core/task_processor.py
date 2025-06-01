"""
标准化任务处理流水线
统一处理任务提交、执行、下载、AI总结等核心流程
"""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from app.core.logger import get_logger
from app.core.exceptions import AgentHubException, PlatformError
from app.core.platform_capabilities import PlatformCapabilities, CapabilityManager


class TaskStatus(Enum):
    """任务状态"""
    CREATED = "created"
    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStage(Enum):
    """处理阶段"""
    INITIALIZATION = "initialization"
    TASK_SUBMISSION = "task_submission"
    TASK_MONITORING = "task_monitoring"
    CONTENT_EXTRACTION = "content_extraction"
    FILE_DOWNLOAD = "file_download"
    AI_ANALYSIS = "ai_analysis"
    QUALITY_CONTROL = "quality_control"
    COMPLETION = "completion"


@dataclass
class ProcessingMetrics:
    """处理指标"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    stage_times: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    total_files: int = 0
    files_downloaded: int = 0
    ai_summary_generated: bool = False
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_time(self) -> float:
        """总处理时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def download_success_rate(self) -> float:
        """下载成功率"""
        if self.total_files == 0:
            return 0.0
        return self.files_downloaded / self.total_files


@dataclass
class TaskRequest:
    """任务请求"""
    platform: str
    topic: str
    title: Optional[str] = None
    download_dir: Optional[Path] = None
    enable_ai_summary: bool = True
    force_ai_regenerate: bool = False
    custom_options: Dict[str, Any] = field(default_factory=dict)
    
    # 处理配置
    timeout: int = 300  # 5分钟超时
    max_retries: int = 3
    retry_delay: int = 5
    
    def __post_init__(self):
        """后处理"""
        if self.download_dir:
            self.download_dir = Path(self.download_dir)


@dataclass
class TaskResult:
    """任务结果"""
    request: TaskRequest
    task_id: str
    status: TaskStatus
    platform: str
    
    # 结果数据
    content: str = ""
    files: List[Path] = field(default_factory=list)
    ai_summary: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 处理信息
    metrics: ProcessingMetrics = field(default_factory=ProcessingMetrics)
    current_stage: ProcessingStage = ProcessingStage.INITIALIZATION
    error_message: str = ""
    
    @property
    def success(self) -> bool:
        """是否成功"""
        return self.status == TaskStatus.COMPLETED
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "platform": self.platform,
            "status": self.status.value,
            "success": self.success,
            "content_length": len(self.content),
            "files_count": len(self.files),
            "ai_summary_available": self.ai_summary is not None,
            "total_time": self.metrics.total_time,
            "download_success_rate": self.metrics.download_success_rate,
            "current_stage": self.current_stage.value,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


class QualityController:
    """质量控制器"""
    
    def __init__(self):
        self.logger = get_logger("quality_controller")
        
        # 质量标准
        self.min_content_length = 100
        self.min_download_rate = 0.5
        self.max_error_rate = 0.3
    
    def validate_task_result(self, result: TaskResult) -> Dict[str, Any]:
        """验证任务结果质量"""
        validation = {
            "passed": True,
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        total_checks = 0
        passed_checks = 0
        
        # 检查内容质量
        total_checks += 1
        if len(result.content) >= self.min_content_length:
            passed_checks += 1
        else:
            validation["issues"].append(f"内容长度不足: {len(result.content)} < {self.min_content_length}")
            validation["recommendations"].append("检查内容提取流程")
        
        # 检查文件下载质量
        if result.files:
            total_checks += 1
            if result.metrics.download_success_rate >= self.min_download_rate:
                passed_checks += 1
            else:
                validation["issues"].append(f"文件下载成功率不足: {result.metrics.download_success_rate:.1%}")
                validation["recommendations"].append("优化文件下载策略")
        
        # 检查错误率
        total_checks += 1
        error_rate = len(result.metrics.errors) / max(1, total_checks)
        if error_rate <= self.max_error_rate:
            passed_checks += 1
        else:
            validation["issues"].append(f"错误率过高: {error_rate:.1%}")
            validation["recommendations"].append("改进错误处理机制")
        
        # 检查AI总结
        if result.request.enable_ai_summary:
            total_checks += 1
            if result.ai_summary:
                passed_checks += 1
            else:
                validation["issues"].append("AI总结生成失败")
                validation["recommendations"].append("检查AI服务配置")
        
        # 计算质量分数
        validation["score"] = passed_checks / total_checks if total_checks > 0 else 0.0
        validation["passed"] = validation["score"] >= 0.7  # 70%通过率
        
        return validation


class TaskProcessor:
    """标准化任务处理器"""
    
    def __init__(self):
        self.logger = get_logger("task_processor")
        self.capability_manager = CapabilityManager()
        self.quality_controller = QualityController()
        
        # 处理状态
        self.active_tasks: Dict[str, TaskResult] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
        # 统计信息
        self.total_tasks_processed = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
    
    async def process_task(self, request: TaskRequest) -> TaskResult:
        """处理单个任务"""
        task_id = f"{request.platform}_{int(time.time())}"
        
        result = TaskResult(
            request=request,
            task_id=task_id,
            status=TaskStatus.CREATED,
            platform=request.platform
        )
        
        self.active_tasks[task_id] = result
        
        try:
            # 阶段1: 初始化
            await self._stage_initialization(result)
            
            # 阶段2: 任务提交
            await self._stage_task_submission(result)
            
            # 阶段3: 任务监控
            await self._stage_task_monitoring(result)
            
            # 阶段4: 内容提取
            await self._stage_content_extraction(result)
            
            # 阶段5: 文件下载
            if request.download_dir:
                await self._stage_file_download(result)
            
            # 阶段6: AI分析
            if request.enable_ai_summary:
                await self._stage_ai_analysis(result)
            
            # 阶段7: 质量控制
            await self._stage_quality_control(result)
            
            # 阶段8: 完成
            await self._stage_completion(result)
            
        except Exception as e:
            await self._handle_task_error(result, e)
        
        finally:
            # 移动到已完成任务
            self.active_tasks.pop(task_id, None)
            self.completed_tasks[task_id] = result
            
            # 更新统计
            self.total_tasks_processed += 1
            if result.success:
                self.successful_tasks += 1
            else:
                self.failed_tasks += 1
        
        return result
    
    async def _stage_initialization(self, result: TaskResult):
        """初始化阶段"""
        result.current_stage = ProcessingStage.INITIALIZATION
        stage_start = time.time()
        
        self.logger.info(f"初始化任务处理: {result.task_id}")
        
        # 验证平台能力
        platform_config = await self._get_platform_config(result.platform)
        capabilities = self.capability_manager.register_platform_capabilities(
            result.platform, platform_config
        )
        
        # 检查必需能力
        if not capabilities.task_submission.is_available():
            raise PlatformError(f"平台 {result.platform} 不支持任务提交", platform=result.platform)
        
        result.metrics.stage_times["initialization"] = time.time() - stage_start
        self.logger.info(f"初始化完成: {result.task_id}")
    
    async def _stage_task_submission(self, result: TaskResult):
        """任务提交阶段"""
        result.current_stage = ProcessingStage.TASK_SUBMISSION
        stage_start = time.time()
        
        self.logger.info(f"提交任务: {result.task_id}")
        
        # 获取平台实例
        platform_instance = await self._get_platform_instance(result.platform)
        
        # 提交任务
        submitted_task_id = await platform_instance.submit_task(
            result.request.topic,
            result.request.title,
            **result.request.custom_options
        )
        
        # 更新任务状态
        result.status = TaskStatus.SUBMITTED
        result.metadata["platform_task_id"] = submitted_task_id
        
        result.metrics.stage_times["task_submission"] = time.time() - stage_start
        self.logger.info(f"任务提交完成: {result.task_id}")
    
    async def _stage_task_monitoring(self, result: TaskResult):
        """任务监控阶段"""
        result.current_stage = ProcessingStage.TASK_MONITORING
        stage_start = time.time()
        
        self.logger.info(f"监控任务状态: {result.task_id}")
        
        platform_instance = await self._get_platform_instance(result.platform)
        platform_task_id = result.metadata.get("platform_task_id", result.task_id)
        
        timeout = result.request.timeout
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务超时: {timeout}秒")
            
            # 获取任务状态
            status = await platform_instance.get_task_status(platform_task_id)
            
            if status == "completed":
                result.status = TaskStatus.COMPLETED
                break
            elif status == "failed":
                result.status = TaskStatus.FAILED
                raise PlatformError(f"平台任务执行失败", platform=result.platform)
            elif status in ["pending", "running"]:
                result.status = TaskStatus.RUNNING
                await asyncio.sleep(10)  # 等待10秒后再检查
            else:
                self.logger.warning(f"未知任务状态: {status}")
                await asyncio.sleep(5)
        
        result.metrics.stage_times["task_monitoring"] = time.time() - stage_start
        self.logger.info(f"任务监控完成: {result.task_id}")
    
    async def _stage_content_extraction(self, result: TaskResult):
        """内容提取阶段"""
        result.current_stage = ProcessingStage.CONTENT_EXTRACTION
        stage_start = time.time()
        
        self.logger.info(f"提取任务内容: {result.task_id}")
        
        platform_instance = await self._get_platform_instance(result.platform)
        platform_task_id = result.metadata.get("platform_task_id", result.task_id)
        
        # 获取任务结果
        task_result = await platform_instance.get_task_result(platform_task_id)
        
        result.content = task_result.result
        result.metadata.update(task_result.metadata or {})
        
        result.metrics.stage_times["content_extraction"] = time.time() - stage_start
        self.logger.info(f"内容提取完成: {result.task_id}, 长度: {len(result.content)}")
    
    async def _stage_file_download(self, result: TaskResult):
        """文件下载阶段"""
        result.current_stage = ProcessingStage.FILE_DOWNLOAD
        stage_start = time.time()
        
        self.logger.info(f"下载任务文件: {result.task_id}")
        
        platform_instance = await self._get_platform_instance(result.platform)
        platform_task_id = result.metadata.get("platform_task_id", result.task_id)
        
        try:
            downloaded_files = await platform_instance.download_files(
                platform_task_id, 
                result.request.download_dir
            )
            
            result.files = downloaded_files
            result.metrics.total_files = len(downloaded_files)
            result.metrics.files_downloaded = len(downloaded_files)
            
            self.logger.info(f"文件下载完成: {result.task_id}, {len(downloaded_files)} 个文件")
            
        except Exception as e:
            self.logger.warning(f"文件下载失败: {result.task_id}, {e}")
            result.metrics.errors.append(f"文件下载失败: {e}")
        
        result.metrics.stage_times["file_download"] = time.time() - stage_start
    
    async def _stage_ai_analysis(self, result: TaskResult):
        """AI分析阶段"""
        result.current_stage = ProcessingStage.AI_ANALYSIS
        stage_start = time.time()
        
        self.logger.info(f"生成AI总结: {result.task_id}")
        
        try:
            # 检查是否有下载目录和文件
            if result.request.download_dir and result.files:
                from app.core.task_summary_generator import generate_task_summary
                
                summary_result = await generate_task_summary(
                    result.request.download_dir,
                    result.request.title or result.request.topic[:50],
                    force=result.request.force_ai_regenerate
                )
                
                if summary_result["success"]:
                    result.ai_summary = summary_result["summary"]
                    result.metrics.ai_summary_generated = True
                    self.logger.info(f"AI总结生成成功: {result.task_id}")
                else:
                    error_msg = f"AI总结生成失败: {summary_result.get('error', 'Unknown error')}"
                    result.metrics.errors.append(error_msg)
                    self.logger.warning(error_msg)
            else:
                result.metrics.errors.append("无法生成AI总结: 缺少下载目录或文件")
                
        except Exception as e:
            error_msg = f"AI分析阶段失败: {e}"
            result.metrics.errors.append(error_msg)
            self.logger.error(error_msg)
        
        result.metrics.stage_times["ai_analysis"] = time.time() - stage_start
    
    async def _stage_quality_control(self, result: TaskResult):
        """质量控制阶段"""
        result.current_stage = ProcessingStage.QUALITY_CONTROL
        stage_start = time.time()
        
        self.logger.info(f"质量控制检查: {result.task_id}")
        
        # 执行质量验证
        validation = self.quality_controller.validate_task_result(result)
        result.metadata["quality_validation"] = validation
        
        if not validation["passed"]:
            self.logger.warning(
                f"质量检查未通过: {result.task_id}, 分数: {validation['score']:.1%}, "
                f"问题: {validation['issues']}"
            )
        else:
            self.logger.info(f"质量检查通过: {result.task_id}, 分数: {validation['score']:.1%}")
        
        result.metrics.stage_times["quality_control"] = time.time() - stage_start
    
    async def _stage_completion(self, result: TaskResult):
        """完成阶段"""
        result.current_stage = ProcessingStage.COMPLETION
        stage_start = time.time()
        
        # 设置结束时间
        result.metrics.end_time = time.time()
        
        # 计算最终成功率
        total_errors = len(result.metrics.errors)
        total_stages = len(ProcessingStage)
        result.metrics.success_rate = max(0.0, 1.0 - (total_errors / total_stages))
        
        # 确定最终状态
        if result.status != TaskStatus.FAILED and result.metrics.success_rate >= 0.5:
            result.status = TaskStatus.COMPLETED
        else:
            result.status = TaskStatus.FAILED
        
        result.metrics.stage_times["completion"] = time.time() - stage_start
        
        self.logger.info(
            f"任务处理完成: {result.task_id}, 状态: {result.status.value}, "
            f"成功率: {result.metrics.success_rate:.1%}, 总时间: {result.metrics.total_time:.1f}秒"
        )
    
    async def _handle_task_error(self, result: TaskResult, error: Exception):
        """处理任务错误"""
        result.status = TaskStatus.FAILED
        result.error_message = str(error)
        result.metrics.errors.append(str(error))
        result.metrics.end_time = time.time()
        
        self.logger.error(f"任务处理失败: {result.task_id}, 错误: {error}")
    
    async def _get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """获取平台配置"""
        from app.config.settings import get_platform_configs
        
        configs = get_platform_configs()
        return configs.get(platform_name, {})
    
    async def _get_platform_instance(self, platform_name: str):
        """获取平台实例"""
        from app.platforms.platform_factory import PlatformFactory
        
        factory = PlatformFactory()
        return await factory.create_platform(platform_name)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        success_rate = (
            self.successful_tasks / self.total_tasks_processed 
            if self.total_tasks_processed > 0 else 0.0
        )
        
        return {
            "total_processed": self.total_tasks_processed,
            "successful": self.successful_tasks,
            "failed": self.failed_tasks,
            "success_rate": success_rate,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks)
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 先在活跃任务中查找
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # 再在已完成任务中查找
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        
        return None 