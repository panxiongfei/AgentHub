"""
平台能力模型
定义平台功能标准和能力评估机制
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import time
from pathlib import Path

from app.core.logger import get_logger


class CapabilityLevel(Enum):
    """能力等级"""
    NOT_SUPPORTED = "not_supported"
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PerformanceLevel(Enum):
    """性能等级"""
    POOR = "poor"          # < 60%
    FAIR = "fair"          # 60-80%
    GOOD = "good"          # 80-90%
    EXCELLENT = "excellent" # > 90%


@dataclass
class CapabilityMetrics:
    """能力指标"""
    success_rate: float = 0.0
    average_time: float = 0.0
    error_count: int = 0
    total_attempts: int = 0
    last_updated: float = field(default_factory=time.time)
    
    def update(self, success: bool, elapsed_time: float):
        """更新指标"""
        self.total_attempts += 1
        if success:
            # 更新成功率
            current_successes = self.success_rate * (self.total_attempts - 1)
            self.success_rate = (current_successes + 1) / self.total_attempts
            
            # 更新平均时间
            current_total_time = self.average_time * (self.total_attempts - 1)
            self.average_time = (current_total_time + elapsed_time) / self.total_attempts
        else:
            self.error_count += 1
            # 重新计算成功率
            current_successes = self.success_rate * (self.total_attempts - 1)
            self.success_rate = current_successes / self.total_attempts
        
        self.last_updated = time.time()
    
    @property
    def performance_level(self) -> PerformanceLevel:
        """获取性能等级"""
        if self.success_rate >= 0.90:
            return PerformanceLevel.EXCELLENT
        elif self.success_rate >= 0.80:
            return PerformanceLevel.GOOD
        elif self.success_rate >= 0.60:
            return PerformanceLevel.FAIR
        else:
            return PerformanceLevel.POOR


@dataclass
class PlatformCapability:
    """单项平台能力"""
    name: str
    level: CapabilityLevel
    enabled: bool = True
    metrics: CapabilityMetrics = field(default_factory=CapabilityMetrics)
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    
    def is_available(self) -> bool:
        """检查能力是否可用"""
        return self.enabled and self.level != CapabilityLevel.NOT_SUPPORTED


@dataclass
class PlatformCapabilities:
    """平台能力集合"""
    platform_name: str
    
    # 核心能力
    task_submission: PlatformCapability = field(default_factory=lambda: PlatformCapability("task_submission", CapabilityLevel.NOT_SUPPORTED))
    history_download: PlatformCapability = field(default_factory=lambda: PlatformCapability("history_download", CapabilityLevel.NOT_SUPPORTED))
    file_management: PlatformCapability = field(default_factory=lambda: PlatformCapability("file_management", CapabilityLevel.NOT_SUPPORTED))
    content_extraction: PlatformCapability = field(default_factory=lambda: PlatformCapability("content_extraction", CapabilityLevel.NOT_SUPPORTED))
    
    # 高级能力
    ai_analysis: PlatformCapability = field(default_factory=lambda: PlatformCapability("ai_analysis", CapabilityLevel.NOT_SUPPORTED))
    multi_modal: PlatformCapability = field(default_factory=lambda: PlatformCapability("multi_modal", CapabilityLevel.NOT_SUPPORTED))
    real_time_processing: PlatformCapability = field(default_factory=lambda: PlatformCapability("real_time_processing", CapabilityLevel.NOT_SUPPORTED))
    
    # 特殊能力
    web_search: PlatformCapability = field(default_factory=lambda: PlatformCapability("web_search", CapabilityLevel.NOT_SUPPORTED))
    voice_interaction: PlatformCapability = field(default_factory=lambda: PlatformCapability("voice_interaction", CapabilityLevel.NOT_SUPPORTED))
    collaborative_editing: PlatformCapability = field(default_factory=lambda: PlatformCapability("collaborative_editing", CapabilityLevel.NOT_SUPPORTED))
    
    # 元数据
    last_assessment: float = field(default_factory=time.time)
    assessment_count: int = 0
    
    @classmethod
    def from_config(cls, platform_name: str, config: Dict[str, Any]) -> 'PlatformCapabilities':
        """从配置创建能力模型"""
        capabilities = cls(platform_name=platform_name)
        
        capability_config = config.get("capabilities", {})
        
        # 映射配置到能力对象
        capability_mapping = {
            "task_submission": capabilities.task_submission,
            "history_download": capabilities.history_download,
            "file_management": capabilities.file_management,
            "content_extraction": capabilities.content_extraction,
            "ai_analysis": capabilities.ai_analysis,
            "multi_modal": capabilities.multi_modal,
            "real_time_processing": capabilities.real_time_processing,
            "web_search": capabilities.web_search,
            "voice_interaction": capabilities.voice_interaction,
            "collaborative_editing": capabilities.collaborative_editing,
        }
        
        for cap_name, cap_obj in capability_mapping.items():
            if cap_name in capability_config:
                enabled = capability_config[cap_name]
                if isinstance(enabled, bool):
                    cap_obj.enabled = enabled
                    cap_obj.level = CapabilityLevel.BASIC if enabled else CapabilityLevel.NOT_SUPPORTED
                elif isinstance(enabled, str):
                    cap_obj.enabled = True
                    try:
                        cap_obj.level = CapabilityLevel(enabled.lower())
                    except ValueError:
                        cap_obj.level = CapabilityLevel.BASIC
        
        return capabilities
    
    def get_capability(self, name: str) -> Optional[PlatformCapability]:
        """获取指定能力"""
        return getattr(self, name, None)
    
    def get_available_capabilities(self) -> List[PlatformCapability]:
        """获取所有可用能力"""
        return [
            cap for cap in [
                self.task_submission, self.history_download, self.file_management,
                self.content_extraction, self.ai_analysis, self.multi_modal,
                self.real_time_processing, self.web_search, self.voice_interaction,
                self.collaborative_editing
            ]
            if cap.is_available()
        ]
    
    def get_core_capabilities_status(self) -> Dict[str, bool]:
        """获取核心能力状态"""
        return {
            "task_submission": self.task_submission.is_available(),
            "history_download": self.history_download.is_available(),
            "file_management": self.file_management.is_available(),
            "content_extraction": self.content_extraction.is_available(),
        }
    
    def assess_overall_performance(self) -> PerformanceLevel:
        """评估整体性能"""
        available_caps = self.get_available_capabilities()
        if not available_caps:
            return PerformanceLevel.POOR
        
        total_score = sum(cap.metrics.success_rate for cap in available_caps)
        average_score = total_score / len(available_caps)
        
        if average_score >= 0.90:
            return PerformanceLevel.EXCELLENT
        elif average_score >= 0.80:
            return PerformanceLevel.GOOD
        elif average_score >= 0.60:
            return PerformanceLevel.FAIR
        else:
            return PerformanceLevel.POOR
    
    def update_capability_metrics(self, capability_name: str, success: bool, elapsed_time: float):
        """更新能力指标"""
        capability = self.get_capability(capability_name)
        if capability:
            capability.metrics.update(success, elapsed_time)
    
    def generate_assessment_report(self) -> Dict[str, Any]:
        """生成能力评估报告"""
        available_caps = self.get_available_capabilities()
        
        report = {
            "platform": self.platform_name,
            "assessment_time": time.time(),
            "overall_performance": self.assess_overall_performance().value,
            "capabilities_summary": {
                "total": len([self.task_submission, self.history_download, self.file_management,
                            self.content_extraction, self.ai_analysis, self.multi_modal,
                            self.real_time_processing, self.web_search, self.voice_interaction,
                            self.collaborative_editing]),
                "available": len(available_caps),
                "core_ready": all(self.get_core_capabilities_status().values())
            },
            "capability_details": {}
        }
        
        # 详细能力报告
        for cap in [self.task_submission, self.history_download, self.file_management,
                   self.content_extraction, self.ai_analysis, self.multi_modal,
                   self.real_time_processing, self.web_search, self.voice_interaction,
                   self.collaborative_editing]:
            report["capability_details"][cap.name] = {
                "level": cap.level.value,
                "enabled": cap.enabled,
                "available": cap.is_available(),
                "performance": cap.metrics.performance_level.value,
                "success_rate": cap.metrics.success_rate,
                "average_time": cap.metrics.average_time,
                "total_attempts": cap.metrics.total_attempts,
                "error_count": cap.metrics.error_count
            }
        
        return report


class CapabilityValidator:
    """能力验证器"""
    
    def __init__(self):
        self.logger = get_logger("capability_validator")
    
    async def validate_platform_capabilities(
        self, 
        platform_instance, 
        capabilities: PlatformCapabilities
    ) -> Dict[str, Any]:
        """验证平台能力"""
        validation_results = {
            "platform": capabilities.platform_name,
            "validation_time": time.time(),
            "tests_passed": 0,
            "tests_failed": 0,
            "capability_results": {}
        }
        
        # 验证任务提交能力
        if capabilities.task_submission.is_available():
            result = await self._validate_task_submission(platform_instance)
            validation_results["capability_results"]["task_submission"] = result
            if result["success"]:
                validation_results["tests_passed"] += 1
            else:
                validation_results["tests_failed"] += 1
        
        # 验证历史下载能力
        if capabilities.history_download.is_available():
            result = await self._validate_history_download(platform_instance)
            validation_results["capability_results"]["history_download"] = result
            if result["success"]:
                validation_results["tests_passed"] += 1
            else:
                validation_results["tests_failed"] += 1
        
        # 计算总体验证结果
        total_tests = validation_results["tests_passed"] + validation_results["tests_failed"]
        validation_results["success_rate"] = (
            validation_results["tests_passed"] / total_tests if total_tests > 0 else 0.0
        )
        
        return validation_results
    
    async def _validate_task_submission(self, platform_instance) -> Dict[str, Any]:
        """验证任务提交能力"""
        try:
            # 简单的连接测试
            success = await platform_instance.test_connection()
            
            return {
                "success": success,
                "message": "连接测试通过" if success else "连接测试失败",
                "test_type": "connection_test"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"任务提交验证失败: {e}",
                "test_type": "connection_test",
                "error": str(e)
            }
    
    async def _validate_history_download(self, platform_instance) -> Dict[str, Any]:
        """验证历史下载能力"""
        try:
            # 检查是否有历史下载器
            has_downloader = hasattr(platform_instance, 'history_downloader')
            
            return {
                "success": has_downloader,
                "message": "历史下载器可用" if has_downloader else "历史下载器不可用",
                "test_type": "downloader_availability"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"历史下载验证失败: {e}",
                "test_type": "downloader_availability",
                "error": str(e)
            }


class CapabilityManager:
    """能力管理器"""
    
    def __init__(self):
        self.logger = get_logger("capability_manager")
        self.platform_capabilities: Dict[str, PlatformCapabilities] = {}
        self.validator = CapabilityValidator()
    
    def register_platform_capabilities(self, platform_name: str, config: Dict[str, Any]):
        """注册平台能力"""
        capabilities = PlatformCapabilities.from_config(platform_name, config)
        self.platform_capabilities[platform_name] = capabilities
        self.logger.info(f"注册平台能力: {platform_name}")
        return capabilities
    
    def get_platform_capabilities(self, platform_name: str) -> Optional[PlatformCapabilities]:
        """获取平台能力"""
        return self.platform_capabilities.get(platform_name)
    
    def get_platforms_by_capability(self, capability_name: str) -> List[str]:
        """根据能力查找平台"""
        platforms = []
        for platform_name, capabilities in self.platform_capabilities.items():
            capability = capabilities.get_capability(capability_name)
            if capability and capability.is_available():
                platforms.append(platform_name)
        return platforms
    
    async def validate_all_platforms(self, platform_instances: Dict[str, Any]) -> Dict[str, Any]:
        """验证所有平台能力"""
        validation_results = {
            "validation_time": time.time(),
            "platforms": {},
            "summary": {
                "total_platforms": len(platform_instances),
                "validated_platforms": 0,
                "failed_validations": 0
            }
        }
        
        for platform_name, platform_instance in platform_instances.items():
            capabilities = self.get_platform_capabilities(platform_name)
            if capabilities:
                try:
                    result = await self.validator.validate_platform_capabilities(
                        platform_instance, capabilities
                    )
                    validation_results["platforms"][platform_name] = result
                    validation_results["summary"]["validated_platforms"] += 1
                except Exception as e:
                    validation_results["platforms"][platform_name] = {
                        "success": False,
                        "error": str(e)
                    }
                    validation_results["summary"]["failed_validations"] += 1
        
        return validation_results
    
    def generate_compatibility_matrix(self) -> Dict[str, Any]:
        """生成兼容性矩阵"""
        capabilities_list = [
            "task_submission", "history_download", "file_management", 
            "content_extraction", "ai_analysis", "multi_modal",
            "real_time_processing", "web_search", "voice_interaction",
            "collaborative_editing"
        ]
        
        matrix = {
            "capabilities": capabilities_list,
            "platforms": {},
            "summary": {
                "total_capabilities": len(capabilities_list),
                "platform_count": len(self.platform_capabilities)
            }
        }
        
        for platform_name, capabilities in self.platform_capabilities.items():
            platform_matrix = {}
            for cap_name in capabilities_list:
                capability = capabilities.get_capability(cap_name)
                platform_matrix[cap_name] = {
                    "available": capability.is_available() if capability else False,
                    "level": capability.level.value if capability else "not_supported",
                    "performance": capability.metrics.performance_level.value if capability else "poor"
                }
            matrix["platforms"][platform_name] = platform_matrix
        
        return matrix 