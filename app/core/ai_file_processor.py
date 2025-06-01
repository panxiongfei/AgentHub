"""
AI文件处理器
对下载的任务文件进行智能分析、总结和预览生成
"""

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from app.core.model_client import get_model_client, ModelResponse
from app.core.logger import get_logger


@dataclass
class FileAnalysisResult:
    """文件分析结果"""
    file_path: str
    file_type: str
    analysis_success: bool
    summary: str
    key_points: List[str]
    content_type: str
    importance_score: float
    ai_preview: str
    visual_description: Optional[str] = None
    raw_content: Optional[str] = None
    error: Optional[str] = None
    ai_usage: Optional[Dict[str, int]] = None


@dataclass
class TaskAnalysisResult:
    """任务分析结果"""
    task_id: str
    task_title: str
    analysis_success: bool
    overall_summary: str
    file_analyses: List[FileAnalysisResult]
    key_insights: List[str]
    task_completion_assessment: str
    content_quality_score: float
    ai_recommendations: List[str]
    total_ai_usage: Dict[str, int]
    processing_time: float


class AIFileProcessor:
    """AI文件处理器"""
    
    def __init__(self):
        self.logger = get_logger("ai_file_processor")
        self.model_client = get_model_client()
        
        # 支持的文件类型
        self.text_extensions = {'.txt', '.md', '.json', '.html', '.htm', '.log', '.csv'}
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        self.document_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        
    async def analyze_task_files(self, task_dir: Path, task_title: str = "") -> TaskAnalysisResult:
        """分析任务目录中的所有文件"""
        start_time = time.time()
        
        try:
            self.logger.info(f"开始AI分析任务文件: {task_dir}")
            
            # 扫描文件
            files = list(task_dir.glob('*'))
            files = [f for f in files if f.is_file()]
            
            if not files:
                return TaskAnalysisResult(
                    task_id=task_dir.name,
                    task_title=task_title,
                    analysis_success=False,
                    overall_summary="任务目录为空，无文件可分析",
                    file_analyses=[],
                    key_insights=[],
                    task_completion_assessment="未完成",
                    content_quality_score=0.0,
                    ai_recommendations=["任务似乎未完成或数据丢失"],
                    total_ai_usage={"total_tokens": 0},
                    processing_time=time.time() - start_time
                )
            
            # 分析每个文件
            file_analyses = []
            total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            
            for file_path in files:
                try:
                    analysis = await self.analyze_single_file(file_path)
                    file_analyses.append(analysis)
                    
                    # 累积AI使用统计
                    if analysis.ai_usage:
                        for key, value in analysis.ai_usage.items():
                            if key in total_usage:
                                total_usage[key] += value
                    
                except Exception as e:
                    self.logger.warning(f"分析文件失败 {file_path}: {e}")
                    file_analyses.append(FileAnalysisResult(
                        file_path=str(file_path),
                        file_type=self._get_file_type(file_path),
                        analysis_success=False,
                        summary=f"文件分析失败: {e}",
                        key_points=[],
                        content_type="unknown",
                        importance_score=0.0,
                        ai_preview="分析失败",
                        error=str(e)
                    ))
            
            # 生成整体分析
            overall_analysis = await self._generate_overall_analysis(
                task_title, file_analyses, total_usage
            )
            
            processing_time = time.time() - start_time
            
            # 构建最终结果
            result = TaskAnalysisResult(
                task_id=task_dir.name,
                task_title=task_title,
                analysis_success=len([a for a in file_analyses if a.analysis_success]) > 0,
                overall_summary=overall_analysis["summary"],
                file_analyses=file_analyses,
                key_insights=overall_analysis["insights"],
                task_completion_assessment=overall_analysis["completion"],
                content_quality_score=overall_analysis["quality_score"],
                ai_recommendations=overall_analysis["recommendations"],
                total_ai_usage=total_usage,
                processing_time=processing_time
            )
            
            self.logger.info(f"任务文件AI分析完成，耗时 {processing_time:.2f}秒")
            return result
            
        except Exception as e:
            self.logger.error(f"任务文件分析失败: {e}")
            return TaskAnalysisResult(
                task_id=task_dir.name,
                task_title=task_title,
                analysis_success=False,
                overall_summary=f"任务分析失败: {e}",
                file_analyses=[],
                key_insights=[],
                task_completion_assessment="分析失败",
                content_quality_score=0.0,
                ai_recommendations=[],
                total_ai_usage={"total_tokens": 0},
                processing_time=time.time() - start_time
            )
    
    async def analyze_single_file(self, file_path: Path) -> FileAnalysisResult:
        """分析单个文件"""
        try:
            file_type = self._get_file_type(file_path)
            
            if file_type == "text":
                return await self._analyze_text_file(file_path)
            elif file_type == "image":
                return await self._analyze_image_file(file_path)
            elif file_type == "json":
                return await self._analyze_json_file(file_path)
            elif file_type == "html":
                return await self._analyze_html_file(file_path)
            else:
                return await self._analyze_generic_file(file_path)
                
        except Exception as e:
            self.logger.error(f"文件分析失败 {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type=self._get_file_type(file_path),
                analysis_success=False,
                summary=f"文件分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="分析失败",
                error=str(e)
            )
    
    async def _analyze_text_file(self, file_path: Path) -> FileAnalysisResult:
        """分析文本文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return FileAnalysisResult(
                    file_path=str(file_path),
                    file_type="text",
                    analysis_success=False,
                    summary="文件为空",
                    key_points=[],
                    content_type="empty",
                    importance_score=0.0,
                    ai_preview="文件无内容"
                )
            
            # 使用AI分析内容
            prompt = f"""
            请分析以下文本文件的内容，这是一个任务执行的结果文件。

            文件名: {file_path.name}
            内容长度: {len(content)} 字符

            请提供：
            1. 内容摘要（150字以内）
            2. 关键信息点（3-5个要点）
            3. 内容类型识别（报告/对话/数据/代码等）
            4. 重要度评分（0-1，1为最重要）
            5. 简短预览（50字以内，吸引人的描述）

            文件内容：
            {content[:4000]}
            """
            
            response = await self.model_client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=800)
            
            # 解析AI响应
            analysis_data = self._parse_analysis_response(response.content)
            
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="text",
                analysis_success=True,
                summary=analysis_data.get("summary", "AI生成的内容摘要"),
                key_points=analysis_data.get("key_points", []),
                content_type=analysis_data.get("content_type", "文本"),
                importance_score=analysis_data.get("importance_score", 0.5),
                ai_preview=analysis_data.get("preview", file_path.name),
                raw_content=content[:1000],  # 保留前1000字符
                ai_usage=response.usage
            )
            
        except Exception as e:
            self.logger.error(f"文本文件分析失败 {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="text",
                analysis_success=False,
                summary=f"文本分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="分析失败",
                error=str(e)
            )
    
    async def _analyze_image_file(self, file_path: Path) -> FileAnalysisResult:
        """分析图片文件"""
        try:
            # 使用AI分析图片
            prompt = f"""
            请分析这张图片，这是一个任务执行过程中的截图。

            文件名: {file_path.name}

            请提供：
            1. 图片内容描述（100字以内）
            2. 识别的关键信息（3-5个要点）
            3. 图片类型（截图/图表/界面/文档等）
            4. 重要度评分（0-1）
            5. 吸引人的预览描述（30字以内）
            """
            
            response = await self.model_client.analyze_image(
                file_path, 
                prompt,
                max_tokens=600
            )
            
            # 解析AI响应
            analysis_data = self._parse_analysis_response(response.content)
            
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="image",
                analysis_success=True,
                summary=analysis_data.get("summary", "AI生成的图片描述"),
                key_points=analysis_data.get("key_points", []),
                content_type=analysis_data.get("content_type", "图片"),
                importance_score=analysis_data.get("importance_score", 0.6),
                ai_preview=analysis_data.get("preview", "图片截图"),
                visual_description=response.content,
                ai_usage=response.usage
            )
            
        except Exception as e:
            self.logger.error(f"图片文件分析失败 {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="image",
                analysis_success=False,
                summary=f"图片分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="分析失败",
                error=str(e)
            )
    
    async def _analyze_json_file(self, file_path: Path) -> FileAnalysisResult:
        """分析JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 为JSON数据生成摘要
            json_summary = self._summarize_json_structure(data)
            
            prompt = f"""
            请分析以下JSON数据结构，这是任务执行的元数据文件。

            文件名: {file_path.name}
            结构摘要: {json_summary}

            请提供：
            1. 数据内容摘要（100字以内）
            2. 关键信息字段（3-5个）
            3. 数据类型（配置/结果/元数据等）
            4. 重要度评分（0-1）
            5. 预览描述（30字以内）
            """
            
            response = await self.model_client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=500)
            
            analysis_data = self._parse_analysis_response(response.content)
            
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="json",
                analysis_success=True,
                summary=analysis_data.get("summary", "JSON数据文件"),
                key_points=analysis_data.get("key_points", []),
                content_type=analysis_data.get("content_type", "数据"),
                importance_score=analysis_data.get("importance_score", 0.4),
                ai_preview=analysis_data.get("preview", "数据文件"),
                raw_content=json.dumps(data, ensure_ascii=False, indent=2)[:1000],
                ai_usage=response.usage
            )
            
        except Exception as e:
            self.logger.error(f"JSON文件分析失败 {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="json",
                analysis_success=False,
                summary=f"JSON分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="分析失败",
                error=str(e)
            )
    
    async def _analyze_html_file(self, file_path: Path) -> FileAnalysisResult:
        """分析HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 清理HTML内容
            cleaned_content = self._clean_html_content(content)
            
            prompt = f"""
            请分析以下HTML页面内容，这是任务执行过程中保存的网页。

            文件名: {file_path.name}
            清理后内容长度: {len(cleaned_content)} 字符

            请提供：
            1. 页面内容摘要（120字以内）
            2. 关键信息（3-5个要点）
            3. 页面类型（结果页/表单/报告等）
            4. 重要度评分（0-1）
            5. 预览描述（40字以内）

            页面内容：
            {cleaned_content[:3000]}
            """
            
            response = await self.model_client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=700)
            
            analysis_data = self._parse_analysis_response(response.content)
            
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="html",
                analysis_success=True,
                summary=analysis_data.get("summary", "HTML页面内容"),
                key_points=analysis_data.get("key_points", []),
                content_type=analysis_data.get("content_type", "网页"),
                importance_score=analysis_data.get("importance_score", 0.5),
                ai_preview=analysis_data.get("preview", "网页快照"),
                raw_content=cleaned_content[:1000],
                ai_usage=response.usage
            )
            
        except Exception as e:
            self.logger.error(f"HTML文件分析失败 {file_path}: {e}")
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="html",
                analysis_success=False,
                summary=f"HTML分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="分析失败",
                error=str(e)
            )
    
    async def _analyze_generic_file(self, file_path: Path) -> FileAnalysisResult:
        """分析通用文件"""
        try:
            file_type = self._get_file_type(file_path)
            file_size = file_path.stat().st_size
            
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type=file_type,
                analysis_success=True,
                summary=f"{file_type}文件，大小 {file_size} 字节",
                key_points=[f"文件类型: {file_type}", f"文件大小: {file_size} 字节"],
                content_type=file_type,
                importance_score=0.3,
                ai_preview=f"{file_path.name} ({file_type})"
            )
            
        except Exception as e:
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="unknown",
                analysis_success=False,
                summary=f"文件分析失败: {e}",
                key_points=[],
                content_type="error",
                importance_score=0.0,
                ai_preview="未知文件",
                error=str(e)
            )
    
    async def _generate_overall_analysis(
        self, 
        task_title: str, 
        file_analyses: List[FileAnalysisResult],
        total_usage: Dict[str, int]
    ) -> Dict[str, Any]:
        """生成整体分析"""
        try:
            # 收集成功分析的文件信息
            successful_analyses = [a for a in file_analyses if a.analysis_success]
            
            if not successful_analyses:
                return {
                    "summary": "无法分析任务文件",
                    "insights": [],
                    "completion": "未完成",
                    "quality_score": 0.0,
                    "recommendations": ["重新执行任务", "检查文件完整性"]
                }
            
            # 构建分析汇总
            summaries = [a.summary for a in successful_analyses]
            all_key_points = []
            for a in successful_analyses:
                all_key_points.extend(a.key_points)
            
            avg_importance = sum(a.importance_score for a in successful_analyses) / len(successful_analyses)
            
            # 生成整体总结
            prompt = f"""
            基于以下任务文件的分析结果，生成整体评估：

            任务标题: {task_title}
            分析的文件数量: {len(successful_analyses)}
            
            各文件摘要:
            {chr(10).join(f"- {s}" for s in summaries[:5])}
            
            关键信息点:
            {chr(10).join(f"• {p}" for p in all_key_points[:10])}
            
            平均重要度: {avg_importance:.2f}

            请提供：
            1. 整体任务完成情况摘要（150字以内）
            2. 3-5个核心洞察
            3. 任务完成度评估（完成/部分完成/未完成）
            4. 内容质量评分（0-1）
            5. 3个改进建议
            """
            
            response = await self.model_client.chat_completion([
                {"role": "user", "content": prompt}
            ], max_tokens=800)
            
            # 更新AI使用统计
            for key, value in response.usage.items():
                if key in total_usage:
                    total_usage[key] += value
            
            # 解析整体分析
            overall_data = self._parse_overall_analysis_response(response.content)
            
            return overall_data
            
        except Exception as e:
            self.logger.error(f"生成整体分析失败: {e}")
            return {
                "summary": f"整体分析失败: {e}",
                "insights": ["分析过程出现错误"],
                "completion": "分析失败",
                "quality_score": 0.0,
                "recommendations": ["重新尝试分析", "检查AI服务连接"]
            }
    
    def _get_file_type(self, file_path: Path) -> str:
        """获取文件类型"""
        suffix = file_path.suffix.lower()
        
        if suffix in self.text_extensions:
            if suffix == '.json':
                return 'json'
            elif suffix in {'.html', '.htm'}:
                return 'html'
            else:
                return 'text'
        elif suffix in self.image_extensions:
            return 'image'
        elif suffix in self.document_extensions:
            return 'document'
        else:
            return 'binary'
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析AI分析响应"""
        try:
            # 尝试提取关键信息
            lines = response.split('\n')
            
            result = {
                "summary": "",
                "key_points": [],
                "content_type": "未知",
                "importance_score": 0.5,
                "preview": ""
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 识别段落类型
                if any(keyword in line.lower() for keyword in ["摘要", "总结", "概述"]):
                    current_section = "summary"
                elif any(keyword in line.lower() for keyword in ["关键", "要点", "信息点"]):
                    current_section = "key_points"
                elif any(keyword in line.lower() for keyword in ["类型", "分类"]):
                    current_section = "content_type"
                elif any(keyword in line.lower() for keyword in ["评分", "重要度"]):
                    current_section = "importance_score"
                elif any(keyword in line.lower() for keyword in ["预览", "描述"]):
                    current_section = "preview"
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                    if current_section == "key_points":
                        cleaned_point = line.lstrip('123456789.-•* ').strip()
                        if cleaned_point:
                            result["key_points"].append(cleaned_point)
                elif current_section and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    # 提取内容
                    if current_section == "summary" and not result["summary"]:
                        result["summary"] = line
                    elif current_section == "content_type" and not result["content_type"]:
                        result["content_type"] = line
                    elif current_section == "preview" and not result["preview"]:
                        result["preview"] = line
                    elif current_section == "importance_score":
                        # 尝试提取数字
                        import re
                        score_match = re.search(r'(\d*\.?\d+)', line)
                        if score_match:
                            score = float(score_match.group(1))
                            if score <= 1:
                                result["importance_score"] = score
                            elif score <= 10:
                                result["importance_score"] = score / 10
            
            # 设置默认值
            if not result["summary"]:
                result["summary"] = response[:200] if response else "AI分析结果"
            if not result["key_points"]:
                result["key_points"] = ["AI生成的关键信息"]
            if not result["preview"]:
                result["preview"] = result["summary"][:50]
            
            return result
            
        except Exception as e:
            self.logger.warning(f"解析AI响应失败: {e}")
            return {
                "summary": response[:200] if response else "分析失败",
                "key_points": ["解析失败"],
                "content_type": "unknown",
                "importance_score": 0.5,
                "preview": "AI分析"
            }
    
    def _parse_overall_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析整体分析响应"""
        try:
            lines = response.split('\n')
            
            result = {
                "summary": "",
                "insights": [],
                "completion": "部分完成",
                "quality_score": 0.5,
                "recommendations": []
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 识别段落
                if any(keyword in line.lower() for keyword in ["摘要", "总结", "完成情况"]):
                    current_section = "summary"
                elif any(keyword in line.lower() for keyword in ["洞察", "核心", "关键发现"]):
                    current_section = "insights"
                elif any(keyword in line.lower() for keyword in ["完成度", "评估"]):
                    current_section = "completion"
                elif any(keyword in line.lower() for keyword in ["质量", "评分"]):
                    current_section = "quality_score"
                elif any(keyword in line.lower() for keyword in ["建议", "推荐", "改进"]):
                    current_section = "recommendations"
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                    cleaned_item = line.lstrip('123456789.-•* ').strip()
                    if cleaned_item:
                        if current_section == "insights":
                            result["insights"].append(cleaned_item)
                        elif current_section == "recommendations":
                            result["recommendations"].append(cleaned_item)
                elif current_section and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    if current_section == "summary" and not result["summary"]:
                        result["summary"] = line
                    elif current_section == "completion":
                        if any(word in line.lower() for word in ["完成", "成功"]):
                            result["completion"] = "完成"
                        elif any(word in line.lower() for word in ["未完成", "失败"]):
                            result["completion"] = "未完成"
                        else:
                            result["completion"] = "部分完成"
                    elif current_section == "quality_score":
                        import re
                        score_match = re.search(r'(\d*\.?\d+)', line)
                        if score_match:
                            score = float(score_match.group(1))
                            if score <= 1:
                                result["quality_score"] = score
                            elif score <= 10:
                                result["quality_score"] = score / 10
            
            # 设置默认值
            if not result["summary"]:
                result["summary"] = response[:200] if response else "整体分析结果"
            if not result["insights"]:
                result["insights"] = ["AI生成的核心洞察"]
            if not result["recommendations"]:
                result["recommendations"] = ["继续优化任务执行流程"]
            
            return result
            
        except Exception as e:
            self.logger.warning(f"解析整体分析失败: {e}")
            return {
                "summary": response[:200] if response else "分析失败",
                "insights": ["解析失败"],
                "completion": "未知",
                "quality_score": 0.5,
                "recommendations": ["重新分析"]
            }
    
    def _summarize_json_structure(self, data: Any, max_depth: int = 2) -> str:
        """总结JSON结构"""
        try:
            if isinstance(data, dict):
                keys = list(data.keys())[:10]  # 最多显示10个键
                return f"对象包含 {len(data)} 个字段: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}"
            elif isinstance(data, list):
                return f"数组包含 {len(data)} 个元素"
            else:
                return f"简单值: {type(data).__name__}"
        except:
            return "复杂数据结构"
    
    def _clean_html_content(self, html: str) -> str:
        """清理HTML内容"""
        try:
            import re
            
            # 移除script和style标签
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # 移除HTML标签
            html = re.sub(r'<[^>]+>', ' ', html)
            
            # 清理空白字符
            html = re.sub(r'\s+', ' ', html)
            
            return html.strip()
        except:
            return html[:1000] 