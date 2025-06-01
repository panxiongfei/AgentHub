"""
扣子空间平台实现
基于标准化架构的AI平台集成
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.platforms.enhanced_platform_base import EnhancedPlatformBase
from app.core.platform_capabilities import PlatformCapabilities, CapabilityLevel
from app.core.exceptions import PlatformError, PlatformConnectionError
from app.core.logger import get_logger


class CozeSpacePlatform(EnhancedPlatformBase):
    """扣子空间平台实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("coze_space", config)
        
        # 平台特定配置
        self.workflow_enabled = config.get("workflow_enabled", True)
        self.collaborative_mode = config.get("collaborative_mode", True)
        self.space_mode = config.get("space_mode", "conversation")
        
        self.logger.info(f"初始化扣子空间平台: 工作流={self.workflow_enabled}, 协作={self.collaborative_mode}")
    
    def _get_platform_selectors(self) -> Dict[str, List[str]]:
        """获取扣子空间平台特定的选择器配置"""
        return {
            # 导航相关
            "navigation": {
                "sidebar": [
                    ".sidebar",
                    ".left-sidebar", 
                    ".conversation-list",
                    "[class*='sidebar']",
                    ".chat-history",
                    "nav",
                    ".workspace-nav"
                ],
                "main_content": [
                    ".main",
                    ".chat-main",
                    ".conversation-area",
                    "[class*='main']",
                    ".workspace",
                    ".content-area"
                ]
            },
            
            # 任务操作相关
            "task_operations": {
                "input_field": [
                    "textarea",
                    "input[type='text']",
                    ".chat-input",
                    "[contenteditable='true']",
                    ".text-editor",
                    "[placeholder*='输入']",
                    "[placeholder*='请输入']",
                    ".message-input"
                ],
                "submit_button": [
                    "button[type='submit']",
                    ".send-btn",
                    ".submit-button",
                    "button:has-text('发送')",
                    "button:has-text('提交')",
                    "button:has-text('Send')",
                    "[class*='send']",
                    "[data-testid='send-button']"
                ],
                "workflow_trigger": [
                    ".workflow-btn",
                    "button:has-text('运行')",
                    "button:has-text('执行')",
                    ".run-workflow",
                    "[class*='workflow']"
                ]
            },
            
            # 历史任务相关
            "history_elements": {
                "task_items": [
                    ".conversation-item",
                    ".chat-item",
                    ".history-item",
                    "li[data-conversation]",
                    "[class*='conversation']",
                    ".task-card",
                    ".space-item"
                ],
                "task_title": [
                    ".conversation-title",
                    ".chat-title",
                    ".task-title",
                    "h3",
                    "h4",
                    ".title",
                    "[class*='title']",
                    ".space-name"
                ],
                "task_date": [
                    ".date",
                    ".time",
                    ".timestamp",
                    "time",
                    "[class*='time']",
                    ".meta-info",
                    ".created-at"
                ]
            },
            
            # 内容提取相关
            "content_extraction": {
                "messages": [
                    ".message",
                    ".chat-message",
                    ".conversation-message",
                    "[data-message-id]",
                    ".msg-item",
                    ".dialogue-item"
                ],
                "user_message": [
                    ".message.user",
                    ".user-message",
                    "[data-role='user']",
                    ".human-message"
                ],
                "assistant_message": [
                    ".message.assistant",
                    ".assistant-message", 
                    "[data-role='assistant']",
                    ".ai-message",
                    ".bot-message"
                ],
                "workflow_results": [
                    ".workflow-result",
                    ".execution-result",
                    ".output-container",
                    ".result-panel"
                ]
            }
        }
    
    def _get_platform_keywords(self) -> Dict[str, List[str]]:
        """获取扣子空间平台特定的关键词配置"""
        return {
            "title": ["coze", "扣子", "space", "ai", "助手"],
            "content": ["conversation", "chat", "dialogue", "workflow", "工作流"],
            "features": ["workflow", "collaboration", "space", "multi-agent", "automation"],
            "errors": ["rate limit", "quota", "network error", "timeout", "工作流错误"]
        }
    
    def _get_platform_domains(self) -> List[str]:
        """获取扣子空间平台域名列表"""
        return [
            "space.coze.cn",
            "coze.cn", 
            "coze.com"
        ]
    
    def _get_platform_capabilities(self) -> PlatformCapabilities:
        """获取平台能力配置"""
        capabilities = PlatformCapabilities(platform_name=self.name)
        
        # 核心能力
        capabilities.task_submission.level = CapabilityLevel.ADVANCED
        capabilities.task_submission.enabled = True
        capabilities.task_submission.description = "支持对话和工作流任务提交"
        
        capabilities.history_download.level = CapabilityLevel.ADVANCED
        capabilities.history_download.enabled = True
        capabilities.history_download.description = "支持完整的对话和工作流历史下载"
        
        capabilities.file_management.level = CapabilityLevel.ADVANCED
        capabilities.file_management.enabled = True
        capabilities.file_management.description = "支持文件上传、下载和管理"
        
        capabilities.content_extraction.level = CapabilityLevel.EXPERT
        capabilities.content_extraction.enabled = True
        capabilities.content_extraction.description = "支持智能内容提取和结构化"
        
        # 高级能力
        capabilities.ai_analysis.level = CapabilityLevel.EXPERT
        capabilities.ai_analysis.enabled = True
        capabilities.ai_analysis.description = "原生AI分析和推理能力"
        
        capabilities.multi_modal.level = CapabilityLevel.EXPERT
        capabilities.multi_modal.enabled = True
        capabilities.multi_modal.description = "支持文本、图片、文档多模态处理"
        
        capabilities.real_time_processing.level = CapabilityLevel.EXPERT
        capabilities.real_time_processing.enabled = True
        capabilities.real_time_processing.description = "实时对话和工作流处理"
        
        # 特殊能力 - 扣子空间的独特功能
        capabilities.collaborative_editing.level = CapabilityLevel.EXPERT
        capabilities.collaborative_editing.enabled = self.collaborative_mode
        capabilities.collaborative_editing.description = "协作空间和多人编辑能力"
        
        return capabilities
    
    async def submit_task(
        self,
        topic: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """提交任务到扣子空间平台"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            self.logger.info(f"开始提交扣子空间任务: {title or topic[:50]}")
            
            # 检查是否需要使用工作流模式
            use_workflow = kwargs.get("use_workflow", self.workflow_enabled)
            
            # 构建增强的提示词
            enhanced_prompt = await self._build_enhanced_prompt(topic, use_workflow)
            
            # 如果需要工作流，先检查是否有可用的工作流
            if use_workflow:
                await self._check_and_prepare_workflow()
            
            # 智能输入文本
            input_result = await self.browser_engine.smart_input_text(enhanced_prompt)
            
            if not input_result.success:
                raise PlatformError(f"输入文本失败: {input_result.error}", platform=self.name)
            
            self.logger.info("成功输入增强提示词")
            
            # 智能提交
            submit_result = await self.browser_engine.smart_submit()
            
            if not submit_result.success:
                raise PlatformError(f"提交任务失败: {submit_result.error}", platform=self.name)
            
            # 生成任务ID
            task_id = f"coze_space_{int(time.time())}"
            
            self.logger.info(f"扣子空间任务提交成功，任务ID: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"提交扣子空间任务失败: {e}")
            raise PlatformError(f"提交任务失败: {e}", platform=self.name)
    
    async def _build_enhanced_prompt(self, topic: str, use_workflow: bool) -> str:
        """构建增强的提示词"""
        # 基础提示词模板
        prompt_parts = []
        
        if use_workflow:
            prompt_parts.append("请使用工作流功能来处理以下任务，然后")
        
        prompt_parts.append(f"请针对以下主题进行深入分析和处理：\n\n{topic}")
        
        # 添加扣子空间特定的结构化要求
        prompt_parts.append("""

请按照以下结构提供分析结果：

1. **任务理解** - 明确任务目标和关键要求
2. **解决方案** - 提供具体的解决思路和方法
3. **执行步骤** - 详细的实施步骤和流程
4. **预期结果** - 期望达到的效果和产出
5. **风险评估** - 可能遇到的问题和应对策略

请确保：
- 分析全面且具有实用性
- 步骤清晰易于执行
- 充分利用AI助手的能力
- 结果可度量和验证""")
        
        return "\n".join(prompt_parts)
    
    async def _check_and_prepare_workflow(self):
        """检查并准备工作流"""
        try:
            # 查找工作流触发按钮
            workflow_selectors = self.platform_selectors.get("task_operations", {}).get("workflow_trigger", [])
            
            for selector in workflow_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element and await element.is_visible():
                        self.logger.info("发现可用工作流功能")
                        return
                except:
                    continue
            
            self.logger.info("未发现工作流功能，使用标准对话模式")
            
        except Exception as e:
            self.logger.warning(f"检查工作流功能失败: {e}")
    
    async def get_task_status(self, task_id: str) -> str:
        """获取扣子空间任务状态"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 页面智能分析
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查错误状态
            if analysis["errors_detected"]:
                error_text = "; ".join(analysis["errors_detected"])
                error_keywords = ["错误", "失败", "超时", "限制", "error", "failed", "timeout", "limit"]
                if any(keyword in error_text.lower() for keyword in error_keywords):
                    self.logger.warning(f"检测到错误信息: {error_text}")
                    return "failed"
            
            # 检查是否还在处理中
            processing_indicators = [
                "处理中", "生成中", "执行中", "运行中", "thinking", "processing", 
                "generating", "executing", "工作流执行", "停止生成"
            ]
            
            page_text = analysis["page_info"].get("visible_text", "").lower()
            if any(indicator in page_text for indicator in processing_indicators):
                self.logger.info("检测到正在处理状态")
                return "running"
            
            # 检查是否有完整的回复
            messages = await self._extract_conversation_messages()
            if messages and len(messages) >= 2:  # 至少有用户问题和AI回复
                last_message = messages[-1]
                if last_message.get("role") == "assistant" and len(last_message.get("content", "")) > 50:
                    self.logger.info("检测到完整的AI回复")
                    return "completed"
            
            # 检查工作流执行结果
            workflow_results = await self._check_workflow_results()
            if workflow_results:
                self.logger.info("检测到工作流执行结果")
                return "completed"
            
            # 默认返回运行中状态
            return "running"
            
        except Exception as e:
            self.logger.error(f"获取扣子空间任务状态失败: {e}")
            return "failed"
    
    async def _check_workflow_results(self) -> bool:
        """检查工作流执行结果"""
        try:
            result_selectors = self.platform_selectors.get("content_extraction", {}).get("workflow_results", [])
            
            for selector in result_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            if await element.is_visible():
                                content = await element.inner_text()
                                if content and len(content.strip()) > 20:
                                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"检查工作流结果失败: {e}")
            return False
    
    async def get_task_result(self, task_id: str):
        """获取扣子空间任务结果"""
        from app.platforms.base_platform import TaskResult as BaseTaskResult
        
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 提取对话消息
            messages = await self._extract_conversation_messages()
            
            # 提取工作流结果
            workflow_results = await self._extract_workflow_results()
            
            if not messages and not workflow_results:
                raise PlatformError("未找到对话内容或工作流结果", platform=self.name)
            
            # 构建结果文本
            result_parts = []
            
            # 添加对话内容
            for message in messages:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                
                if role == "user":
                    result_parts.append(f"**用户输入:**\n{content}\n")
                elif role == "assistant":
                    result_parts.append(f"**AI回复:**\n{content}\n")
            
            # 添加工作流结果
            if workflow_results:
                result_parts.append(f"**工作流执行结果:**\n{workflow_results}\n")
            
            result_text = "\n".join(result_parts)
            
            # 获取页面分析信息
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 构建元数据
            metadata = {
                "page_url": analysis["page_info"]["url"],
                "page_title": analysis["page_info"]["title"],
                "content_length": len(result_text),
                "message_count": len(messages),
                "workflow_enabled": self.workflow_enabled,
                "collaborative_mode": self.collaborative_mode,
                "extraction_method": "conversation_and_workflow_parsing",
                "has_workflow_results": bool(workflow_results),
                "space_mode": self.space_mode
            }
            
            self.logger.info(f"成功提取扣子空间结果，消息数: {len(messages)}, 长度: {len(result_text)}")
            
            return BaseTaskResult(
                platform=self.name,
                task_id=task_id,
                success=True,
                result=result_text,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"获取扣子空间任务结果失败: {e}")
            return BaseTaskResult(
                platform=self.name,
                task_id=task_id,
                success=False,
                result=f"获取结果失败: {e}"
            )
    
    async def _extract_conversation_messages(self) -> List[Dict[str, Any]]:
        """提取对话消息"""
        try:
            messages = []
            
            # 获取所有消息元素
            message_selectors = self.platform_selectors.get("content_extraction", {}).get("messages", [])
            
            for selector in message_selectors:
                try:
                    message_elements = await self.page.query_selector_all(selector)
                    if message_elements:
                        break
                except:
                    continue
            else:
                self.logger.warning("未找到消息元素")
                return []
            
            # 解析每个消息
            for element in message_elements:
                try:
                    # 确定消息角色
                    role = await self._determine_message_role(element)
                    
                    # 提取消息内容
                    content = await self._extract_message_content(element)
                    
                    if content and content.strip():
                        messages.append({
                            "role": role,
                            "content": content.strip()
                        })
                        
                except Exception as e:
                    self.logger.warning(f"解析消息失败: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f"提取对话消息失败: {e}")
            return []
    
    async def _extract_workflow_results(self) -> str:
        """提取工作流执行结果"""
        try:
            result_text = ""
            result_selectors = self.platform_selectors.get("content_extraction", {}).get("workflow_results", [])
            
            for selector in result_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            content = await element.inner_text()
                            if content and content.strip():
                                result_text += content.strip() + "\n"
                except:
                    continue
            
            return result_text.strip()
            
        except Exception as e:
            self.logger.warning(f"提取工作流结果失败: {e}")
            return ""
    
    async def _determine_message_role(self, element) -> str:
        """确定消息角色"""
        try:
            # 检查元素类名和属性
            class_name = await element.get_attribute("class") or ""
            data_role = await element.get_attribute("data-role") or ""
            
            if "user" in class_name.lower() or data_role == "user" or "human" in class_name.lower():
                return "user"
            elif "assistant" in class_name.lower() or data_role == "assistant" or "ai" in class_name.lower() or "bot" in class_name.lower():
                return "assistant"
            
            # 通过父元素或兄弟元素判断
            parent = await element.query_selector("..")
            if parent:
                parent_class = await parent.get_attribute("class") or ""
                if "user" in parent_class.lower():
                    return "user"
                elif "assistant" in parent_class.lower() or "ai" in parent_class.lower():
                    return "assistant"
            
            # 默认返回assistant
            return "assistant"
            
        except:
            return "unknown"
    
    async def _extract_message_content(self, element) -> str:
        """提取消息内容"""
        try:
            # 尝试多种内容提取方法
            
            # 方法1: 直接获取文本内容
            content = await element.inner_text()
            if content and len(content.strip()) > 10:
                return content
            
            # 方法2: 查找内容容器
            content_selectors = [
                ".message-content",
                ".content", 
                ".text",
                ".msg-text",
                "p",
                "div"
            ]
            
            for selector in content_selectors:
                try:
                    content_element = await element.query_selector(selector)
                    if content_element:
                        content = await content_element.inner_text()
                        if content and len(content.strip()) > 10:
                            return content
                except:
                    continue
            
            # 方法3: 获取HTML内容并清理
            html_content = await element.inner_html()
            if html_content:
                # 简单的HTML标签清理
                import re
                text_content = re.sub(r'<[^>]+>', ' ', html_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                return text_content
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"提取消息内容失败: {e}")
            return ""
    
    async def get_history_tasks(self) -> List[Dict[str, Any]]:
        """获取扣子空间历史任务列表"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            self.logger.info("开始获取扣子空间历史任务列表")
            
            # 查找侧边栏历史任务区域
            sidebar_selectors = self.platform_selectors.get("navigation", {}).get("sidebar", [])
            sidebar = None
            
            for selector in sidebar_selectors:
                try:
                    sidebar = await self.page.wait_for_selector(selector, timeout=5000)
                    if sidebar and await sidebar.is_visible():
                        self.logger.info(f"找到侧边栏: {selector}")
                        break
                except:
                    continue
            
            if not sidebar:
                self.logger.warning("未找到侧边栏，尝试从主页面获取历史任务")
                return await self._extract_history_from_main_page()
            
            # 从侧边栏提取历史任务
            history_tasks = await self._extract_history_from_sidebar(sidebar)
            
            self.logger.info(f"成功获取 {len(history_tasks)} 个历史任务")
            return history_tasks
            
        except Exception as e:
            self.logger.error(f"获取扣子空间历史任务失败: {e}")
            return []
    
    async def _extract_history_from_sidebar(self, sidebar) -> List[Dict[str, Any]]:
        """从侧边栏提取历史任务"""
        try:
            tasks = []
            task_selectors = self.platform_selectors.get("history_elements", {}).get("task_items", [])
            
            # 尝试不同的任务项选择器
            task_elements = []
            for selector in task_selectors:
                try:
                    elements = await sidebar.query_selector_all(selector)
                    if elements:
                        task_elements.extend(elements)
                        self.logger.info(f"通过选择器 {selector} 找到 {len(elements)} 个任务项")
                except:
                    continue
            
            # 去重
            unique_elements = []
            seen_text = set()
            
            for element in task_elements:
                try:
                    text = await element.inner_text()
                    if text and text.strip() and text.strip() not in seen_text:
                        unique_elements.append(element)
                        seen_text.add(text.strip())
                except:
                    continue
            
            # 解析每个任务项
            for i, element in enumerate(unique_elements[:20]):  # 限制最多20个
                try:
                    task_info = await self._parse_coze_task_item(element, i)
                    if task_info:
                        tasks.append(task_info)
                except Exception as e:
                    self.logger.warning(f"解析任务项 {i} 失败: {e}")
                    continue
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"从侧边栏提取历史任务失败: {e}")
            return []
    
    async def _extract_history_from_main_page(self) -> List[Dict[str, Any]]:
        """从主页面提取历史任务"""
        try:
            tasks = []
            
            # 尝试从页面中查找对话或工作流记录
            content_selectors = [
                ".conversation-list",
                ".space-list",
                ".chat-history",
                ".project-list",
                ".workflow-history",
                "[class*='history']",
                "[class*='conversation']",
                "[class*='space']"
            ]
            
            for selector in content_selectors:
                try:
                    container = await self.page.query_selector(selector)
                    if container:
                        task_elements = await container.query_selector_all("div, li, a")
                        
                        for i, element in enumerate(task_elements[:10]):
                            try:
                                text = await element.inner_text()
                                if text and len(text.strip()) > 5:
                                    task_info = await self._parse_coze_task_item(element, i)
                                    if task_info:
                                        tasks.append(task_info)
                            except:
                                continue
                        
                        if tasks:
                            break
                            
                except:
                    continue
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"从主页面提取历史任务失败: {e}")
            return []
    
    async def _parse_coze_task_item(self, element, index: int) -> Optional[Dict[str, Any]]:
        """解析扣子空间任务项"""
        try:
            # 提取任务标题
            title = await self._extract_coze_task_title(element)
            if not title or len(title.strip()) < 3:
                return None
            
            # 提取任务日期
            date = await self._extract_coze_task_date(element)
            
            # 提取任务URL
            url = await self._extract_coze_task_url(element)
            
            # 生成任务ID
            task_id = f"coze_space_history_{index}_{int(time.time())}"
            
            # 获取元素选择器路径
            selector = await self._get_element_selector_path(element)
            
            task_info = {
                "id": task_id,
                "title": title.strip(),
                "date": date,
                "url": url,
                "status": "completed",
                "platform": "coze_space",
                "preview": title[:100] + "..." if len(title) > 100 else title,
                "element_selector": selector,
                "metadata": {
                    "index": index,
                    "extraction_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "workflow_enabled": self.workflow_enabled,
                    "collaborative_mode": self.collaborative_mode
                }
            }
            
            return task_info
            
        except Exception as e:
            self.logger.warning(f"解析任务项失败: {e}")
            return None
    
    async def _extract_coze_task_title(self, element) -> str:
        """提取扣子空间任务标题"""
        try:
            # 尝试多种标题提取方法
            title_selectors = self.platform_selectors.get("history_elements", {}).get("task_title", [])
            
            # 方法1: 从子元素中查找标题
            for selector in title_selectors:
                try:
                    title_element = await element.query_selector(selector)
                    if title_element:
                        title = await title_element.inner_text()
                        if title and len(title.strip()) > 2:
                            return title.strip()
                except:
                    continue
            
            # 方法2: 直接获取元素文本
            title = await element.inner_text()
            if title and len(title.strip()) > 2:
                # 清理标题文本
                title = title.strip()
                # 移除多余的空白字符
                title = " ".join(title.split())
                # 截取合理长度
                if len(title) > 100:
                    title = title[:100] + "..."
                return title
            
            # 方法3: 获取元素属性
            title = await element.get_attribute("title")
            if title:
                return title.strip()
            
            title = await element.get_attribute("aria-label")
            if title:
                return title.strip()
            
            return "未知任务"
            
        except Exception as e:
            self.logger.warning(f"提取任务标题失败: {e}")
            return "未知任务"
    
    async def _extract_coze_task_date(self, element) -> str:
        """提取扣子空间任务日期"""
        try:
            date_selectors = self.platform_selectors.get("history_elements", {}).get("task_date", [])
            
            # 从子元素中查找日期
            for selector in date_selectors:
                try:
                    date_element = await element.query_selector(selector)
                    if date_element:
                        date_text = await date_element.inner_text()
                        if date_text and date_text.strip():
                            return date_text.strip()
                except:
                    continue
            
            # 从属性中查找日期
            datetime_attr = await element.get_attribute("datetime")
            if datetime_attr:
                return datetime_attr
            
            # 返回当前时间作为默认值
            return time.strftime("%Y-%m-%d %H:%M:%S")
            
        except:
            return time.strftime("%Y-%m-%d %H:%M:%S")
    
    async def _extract_coze_task_url(self, element) -> str:
        """提取扣子空间任务URL"""
        try:
            # 检查是否是链接元素
            if await element.evaluate("element => element.tagName.toLowerCase()") == "a":
                href = await element.get_attribute("href")
                if href:
                    if href.startswith("http"):
                        return href
                    elif href.startswith("/"):
                        return f"https://space.coze.cn{href}"
            
            # 查找子链接元素
            link = await element.query_selector("a")
            if link:
                href = await link.get_attribute("href")
                if href:
                    if href.startswith("http"):
                        return href
                    elif href.startswith("/"):
                        return f"https://space.coze.cn{href}"
            
            # 返回当前页面URL
            return self.page.url
            
        except:
            return self.page.url
    
    async def _get_element_selector_path(self, element) -> str:
        """获取元素的选择器路径"""
        try:
            # 尝试生成CSS选择器路径
            selector = await element.evaluate("""
                element => {
                    const path = [];
                    let current = element;
                    
                    while (current && current !== document.body) {
                        let selector = current.tagName.toLowerCase();
                        
                        if (current.id) {
                            selector += '#' + current.id;
                            path.unshift(selector);
                            break;
                        }
                        
                        if (current.className) {
                            const classes = current.className.split(' ').filter(c => c).slice(0, 2);
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }
                        
                        path.unshift(selector);
                        current = current.parentElement;
                        
                        if (path.length > 5) break;
                    }
                    
                    return path.join(' > ');
                }
            """)
            
            return selector or "unknown-selector"
            
        except:
            return "unknown-selector"
    
    async def download_history_task(self, task_info: Dict[str, Any], download_dir: Path) -> List[Path]:
        """下载单个历史任务"""
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            downloaded_files = []
            
            # 尝试打开任务页面
            if await self._open_history_task(task_info):
                # 等待页面加载
                await asyncio.sleep(2)
                
                # 提取任务内容
                content = await self._extract_task_content()
                
                # 保存任务内容
                content_file = download_dir / "conversation.txt"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(f"扣子空间历史任务\n")
                    f.write(f"任务ID: {task_info['id']}\n")
                    f.write(f"标题: {task_info['title']}\n")
                    f.write(f"日期: {task_info['date']}\n")
                    f.write(f"URL: {task_info['url']}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content)
                
                downloaded_files.append(content_file)
            
            # 保存任务元数据
            metadata_file = download_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(task_info, f, ensure_ascii=False, indent=2)
            
            downloaded_files.append(metadata_file)
            
            # 保存页面截图
            try:
                screenshot_file = download_dir / "screenshot.png"
                await self.page.screenshot(path=str(screenshot_file))
                downloaded_files.append(screenshot_file)
            except Exception as e:
                self.logger.warning(f"保存截图失败: {e}")
            
            # 保存页面HTML
            try:
                html_file = download_dir / "page.html"
                html_content = await self.page.content()
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                downloaded_files.append(html_file)
            except Exception as e:
                self.logger.warning(f"保存HTML失败: {e}")
            
            self.logger.info(f"历史任务下载完成: {len(downloaded_files)} 个文件")
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"下载历史任务失败: {e}")
            return []
    
    async def _open_history_task(self, task_info: Dict[str, Any]) -> bool:
        """打开历史任务页面"""
        try:
            # 方法1: 通过URL直接导航
            if task_info.get("url") and task_info["url"] != self.page.url:
                await self.page.goto(task_info["url"])
                await asyncio.sleep(2)
                return True
            
            # 方法2: 通过元素选择器点击
            if task_info.get("element_selector"):
                try:
                    element = await self.page.query_selector(task_info["element_selector"])
                    if element and await element.is_visible():
                        await element.click()
                        await asyncio.sleep(2)
                        return True
                except:
                    pass
            
            # 方法3: 通过标题文本查找并点击
            title = task_info.get("title", "")
            if title:
                # 尝试点击包含标题文本的元素
                elements = await self.page.query_selector_all("a, div[role='button'], li")
                for element in elements:
                    try:
                        text = await element.inner_text()
                        if title in text or text in title:
                            await element.click()
                            await asyncio.sleep(2)
                            return True
                    except:
                        continue
            
            return False
            
        except Exception as e:
            self.logger.warning(f"打开历史任务失败: {e}")
            return False
    
    async def _extract_task_content(self) -> str:
        """提取任务内容"""
        try:
            # 提取对话消息
            messages = await self._extract_conversation_messages()
            
            # 提取工作流结果
            workflow_results = await self._extract_workflow_results()
            
            # 构建内容
            content_parts = []
            
            # 添加对话内容
            for message in messages:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                
                if role == "user":
                    content_parts.append(f"**用户输入:**\n{content}\n")
                elif role == "assistant":
                    content_parts.append(f"**AI回复:**\n{content}\n")
            
            # 添加工作流结果
            if workflow_results:
                content_parts.append(f"**工作流执行结果:**\n{workflow_results}\n")
            
            return "\n".join(content_parts) if content_parts else "未能提取到内容"
            
        except Exception as e:
            self.logger.error(f"提取任务内容失败: {e}")
            return f"内容提取失败: {e}"
    
    async def download_files(self, task_id: str, download_dir: Path) -> List[Path]:
        """下载扣子空间任务文件"""
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取任务结果
            task_result = await self.get_task_result(task_id)
            
            downloaded_files = []
            
            # 保存主要内容
            content_file = download_dir / "conversation.txt"
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"扣子空间对话记录\n")
                f.write(f"任务ID: {task_id}\n")
                f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"工作流启用: {self.workflow_enabled}\n")
                f.write(f"协作模式: {self.collaborative_mode}\n")
                f.write(f"空间模式: {self.space_mode}\n")
                f.write("=" * 50 + "\n\n")
                f.write(task_result.result)
            
            downloaded_files.append(content_file)
            
            # 保存元数据
            metadata_file = download_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "task": {
                        "id": task_id,
                        "platform": self.name,
                        "timestamp": time.time(),
                        "workflow_enabled": self.workflow_enabled,
                        "collaborative_mode": self.collaborative_mode,
                        "space_mode": self.space_mode
                    },
                    "result": task_result.metadata
                }, f, ensure_ascii=False, indent=2)
            
            downloaded_files.append(metadata_file)
            
            # 保存页面截图
            try:
                screenshot_file = download_dir / "screenshot.png"
                await self.page.screenshot(path=str(screenshot_file))
                downloaded_files.append(screenshot_file)
            except Exception as e:
                self.logger.warning(f"保存截图失败: {e}")
            
            # 保存页面HTML
            try:
                html_file = download_dir / "page.html"
                html_content = await self.page.content()
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                downloaded_files.append(html_file)
            except Exception as e:
                self.logger.warning(f"保存HTML失败: {e}")
            
            self.logger.info(f"扣子空间文件下载完成: {len(downloaded_files)} 个文件")
            
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"下载扣子空间文件失败: {e}")
            return [] 