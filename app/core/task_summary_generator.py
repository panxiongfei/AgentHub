#!/usr/bin/env python3
"""
任务总结生成器

提供任务完成后的AI总结生成功能，支持：
1. 自动调用（任务下载完成后）
2. 手动调用（API接口）
3. 批量处理（批量脚本）
4. 容错处理（AI不可用时的基础总结）
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

from app.core.logger import get_logger
from app.config.settings import get_settings

logger = get_logger("task_summary_generator")


class TaskSummaryGenerator:
    """任务总结生成器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_processor = None
        self.use_ai = self._check_ai_availability()
        
        if self.use_ai:
            try:
                from app.core.ai_file_processor import AIFileProcessor
                self.ai_processor = AIFileProcessor()
                logger.info("AI总结生成器初始化成功 (AI模式)")
            except Exception as e:
                logger.warning(f"AI文件处理器初始化失败，切换到基础模式: {e}")
                self.use_ai = False
                self.ai_processor = None
        else:
            logger.info("AI总结生成器初始化成功 (基础模式)")
    
    def _check_ai_availability(self) -> bool:
        """检查AI模型是否可用"""
        try:
            if not hasattr(self.settings, 'model'):
                return False
            
            provider = getattr(self.settings.model, 'default_provider', '').lower()
            
            # 检查各个提供商的API密钥
            if provider == 'gemini' and getattr(self.settings.model, 'gemini_api_key', ''):
                return True
            elif provider == 'deepseek' and getattr(self.settings.model, 'deepseek_api_key', ''):
                return True
            elif provider == 'openai' and getattr(self.settings.model, 'openai_api_key', ''):
                return True
            elif provider == 'anthropic' and getattr(self.settings.model, 'anthropic_api_key', ''):
                return True
            
            return False
        except Exception as e:
            logger.warning(f"检查AI可用性时出错: {e}")
            return False
    
    async def generate_summary(
        self, 
        task_dir: Union[str, Path], 
        task_title: str = "",
        force: bool = False
    ) -> Dict:
        """
        为指定任务目录生成AI总结
        
        Args:
            task_dir: 任务目录路径
            task_title: 任务标题
            force: 是否强制重新生成（覆盖已有总结）
            
        Returns:
            Dict: 总结生成结果
        """
        task_dir = Path(task_dir)
        task_id = self._extract_task_id(task_dir)
        
        try:
            logger.info(f"开始生成任务总结: {task_id}")
            
            # 检查是否已有总结且不强制重新生成
            summary_file = task_dir / "ai_summary.json"
            if summary_file.exists() and not force:
                logger.info(f"任务 {task_id} 已有总结，跳过生成")
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "已有总结，跳过生成",
                    "summary_file": str(summary_file),
                    "cached": True
                }
            
            # 加载任务元数据
            task_info = self._load_task_metadata(task_dir)
            if not task_title:
                task_title = task_info.get("task", {}).get("title", task_id)
            
            # 生成总结
            if self.use_ai and self.ai_processor:
                # AI深度分析
                analysis_result = await self.ai_processor.analyze_task_files(task_dir, task_title)
                summary_data = self._format_ai_summary(analysis_result, task_id)
                analysis_type = "ai_powered"
            else:
                # 基础分析
                analysis_result = await self._basic_file_analysis(task_dir, task_title)
                summary_data = self._format_basic_summary(analysis_result, task_id)
                analysis_type = "basic"
            
            # 保存总结
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"任务 {task_id} 总结生成成功 ({analysis_type})")
            
            return {
                "success": True,
                "task_id": task_id,
                "analysis_type": analysis_type,
                "summary_file": str(summary_file),
                "summary": summary_data,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"任务 {task_id} 总结生成失败: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "summary": None
            }
    
    def get_existing_summary(self, task_dir: Union[str, Path]) -> Optional[Dict]:
        """获取已有的总结"""
        task_dir = Path(task_dir)
        summary_file = task_dir / "ai_summary.json"
        
        if summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"读取已有总结失败: {e}")
        
        return None
    
    def has_summary(self, task_dir: Union[str, Path]) -> bool:
        """检查是否已有总结"""
        task_dir = Path(task_dir)
        summary_file = task_dir / "ai_summary.json"
        return summary_file.exists()
    
    async def auto_generate_on_task_completion(
        self, 
        task_dir: Union[str, Path], 
        task_title: str = ""
    ) -> Dict:
        """
        任务完成后自动生成总结
        
        这个函数可以在任务下载完成后自动调用
        """
        logger.info("任务完成，开始自动生成AI总结")
        
        result = await self.generate_summary(
            task_dir=task_dir,
            task_title=task_title,
            force=False  # 自动生成不强制覆盖
        )
        
        if result["success"]:
            logger.info(f"任务自动总结生成成功: {result['task_id']}")
        else:
            logger.error(f"任务自动总结生成失败: {result.get('error', '未知错误')}")
        
        return result
    
    def _extract_task_id(self, task_dir: Path) -> str:
        """从任务目录路径中提取任务ID"""
        dir_name = task_dir.name
        if dir_name.startswith("task_"):
            return dir_name[5:]  # 移除 "task_" 前缀
        return dir_name
    
    def _load_task_metadata(self, task_dir: Path) -> Dict:
        """加载任务元数据"""
        metadata_file = task_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"读取任务元数据失败: {e}")
        
        return {"task": {"title": "未知任务"}}
    
    async def _basic_file_analysis(self, task_dir: Path, task_title: str) -> Dict:
        """基础文件分析（无需AI）"""
        files = list(task_dir.glob('*'))
        files = [f for f in files if f.is_file()]
        
        file_analyses = []
        total_size = 0
        
        for file_path in files:
            try:
                file_stat = file_path.stat()
                file_size = file_stat.st_size
                total_size += file_size
                
                file_type = self._get_file_type(file_path)
                
                # 基础内容分析
                content_preview = ""
                if file_type == "text" and file_size < 100000:  # 100KB以内的文本文件
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:2000]  # 前2000字符
                            content_preview = content[:200]
                    except:
                        content_preview = "无法读取文件内容"
                
                file_analyses.append({
                    "filename": file_path.name,
                    "file_type": file_type,
                    "size": file_size,
                    "summary": f"{file_path.name} ({file_type}文件, {self._format_file_size(file_size)})",
                    "key_info": [f"文件类型: {file_type}", f"文件大小: {self._format_file_size(file_size)}"],
                    "confidence": 0.6,
                    "content_preview": content_preview
                })
                
            except Exception as e:
                logger.warning(f"分析文件 {file_path} 失败: {e}")
        
        return {
            "task_title": task_title,
            "total_files": len(files),
            "total_size": total_size,
            "file_analyses": file_analyses,
            "analysis_type": "basic"
        }
    
    def _format_ai_summary(self, analysis_result, task_id: str) -> Dict:
        """格式化AI分析结果"""
        return {
            "task_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "ai_powered",
            "overall_summary": analysis_result.overall_summary,
            "key_findings": analysis_result.key_insights,
            "file_analysis": [
                {
                    "filename": Path(fa.file_path).name,
                    "file_type": fa.file_type,
                    "summary": fa.summary,
                    "key_info": fa.key_points,
                    "confidence": fa.importance_score
                }
                for fa in analysis_result.file_analyses
            ],
            "total_files": len(analysis_result.file_analyses),
            "analyzed_files": len([fa for fa in analysis_result.file_analyses if fa.analysis_success]),
            "confidence_score": analysis_result.content_quality_score,
            "content_quality": "high" if analysis_result.content_quality_score > 0.7 else "medium" if analysis_result.content_quality_score > 0.4 else "low",
            "main_topics": [insight.split("：")[0] if "：" in insight else insight for insight in analysis_result.key_insights[:5]],
            "task_completion_assessment": analysis_result.task_completion_assessment,
            "ai_recommendations": analysis_result.ai_recommendations,
            "processing_time": analysis_result.processing_time
        }
    
    def _format_basic_summary(self, analysis_result: Dict, task_id: str) -> Dict:
        """格式化基础分析结果"""
        file_analyses = analysis_result["file_analyses"]
        
        # 生成基础洞察
        key_findings = []
        if analysis_result["total_files"] > 0:
            key_findings.append(f"任务包含 {analysis_result['total_files']} 个文件")
            key_findings.append(f"总文件大小: {self._format_file_size(analysis_result['total_size'])}")
            
            # 统计文件类型
            file_types = {}
            for fa in file_analyses:
                file_type = fa["file_type"]
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            for file_type, count in file_types.items():
                key_findings.append(f"包含 {count} 个{file_type}文件")
            
            # 如果有文本文件，尝试提取主题
            text_files = [fa for fa in file_analyses if fa["file_type"] == "text"]
            if text_files:
                key_findings.append("包含文本内容，可能是研究报告或分析文档")
        
        # 生成总体总结
        overall_summary = f"任务 '{analysis_result['task_title']}' 包含 {analysis_result['total_files']} 个文件，总大小为 {self._format_file_size(analysis_result['total_size'])}。"
        
        # 添加内容类型判断
        if any(fa["file_type"] == "text" for fa in file_analyses):
            overall_summary += "包含文本内容，"
        if any(fa["file_type"] == "image" for fa in file_analyses):
            overall_summary += "包含图片文件，"
        if any(fa["file_type"] == "html" for fa in file_analyses):
            overall_summary += "包含网页文件，"
        
        overall_summary += "任务已完成下载。"
        
        return {
            "task_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "analysis_type": "basic",
            "overall_summary": overall_summary,
            "key_findings": key_findings,
            "file_analysis": file_analyses,
            "total_files": analysis_result["total_files"],
            "analyzed_files": analysis_result["total_files"],
            "confidence_score": 0.6,
            "content_quality": "basic",
            "main_topics": [analysis_result["task_title"]],
            "task_completion_assessment": "基础分析完成，任务文件已成功下载",
            "ai_recommendations": ["建议配置AI模型API密钥以获得更详细的内容分析"],
            "processing_time": 0.1
        }
    
    def _get_file_type(self, file_path: Path) -> str:
        """获取文件类型"""
        suffix = file_path.suffix.lower()
        
        type_map = {
            '.txt': 'text',
            '.md': 'text', 
            '.json': 'json',
            '.html': 'html',
            '.htm': 'html',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.log': 'text'
        }
        
        return type_map.get(suffix, 'binary')
    
    def _format_file_size(self, bytes_size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"


# 全局实例
_task_summary_generator = None


def get_task_summary_generator() -> TaskSummaryGenerator:
    """获取任务总结生成器实例（单例模式）"""
    global _task_summary_generator
    if _task_summary_generator is None:
        _task_summary_generator = TaskSummaryGenerator()
    return _task_summary_generator


async def auto_generate_task_summary(task_dir: Union[str, Path], task_title: str = "") -> Dict:
    """
    便捷函数：任务完成后自动生成总结
    
    这个函数可以在任务下载完成后直接调用
    """
    generator = get_task_summary_generator()
    return await generator.auto_generate_on_task_completion(task_dir, task_title)


async def generate_task_summary(
    task_dir: Union[str, Path], 
    task_title: str = "", 
    force: bool = False
) -> Dict:
    """
    便捷函数：生成任务总结
    
    Args:
        task_dir: 任务目录路径
        task_title: 任务标题
        force: 是否强制重新生成
    """
    generator = get_task_summary_generator()
    return await generator.generate_summary(task_dir, task_title, force)


def get_task_summary(task_dir: Union[str, Path]) -> Optional[Dict]:
    """
    便捷函数：获取已有的任务总结
    """
    generator = get_task_summary_generator()
    return generator.get_existing_summary(task_dir)


def has_task_summary(task_dir: Union[str, Path]) -> bool:
    """
    便捷函数：检查是否已有任务总结
    """
    generator = get_task_summary_generator()
    return generator.has_summary(task_dir) 