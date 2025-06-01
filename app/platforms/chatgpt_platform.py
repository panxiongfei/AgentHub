"""
ChatGPT DeepSearch 平台实现
基于标准化架构的第三平台集成示例
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


class ChatGPTPlatform(EnhancedPlatformBase):
    """ChatGPT DeepSearch 平台实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("chatgpt_deepsearch", config)
        
        # 平台特定配置
        self.search_enabled = config.get("search_enabled", True)
        self.web_browsing = config.get("web_browsing", True)
        self.model_version = config.get("model_version", "gpt-4")
        
        self.logger.info(f"初始化ChatGPT平台: 搜索={self.search_enabled}, 浏览={self.web_browsing}")
    
    def _get_platform_selectors(self) -> Dict[str, List[str]]:
        """获取ChatGPT平台特定的选择器配置"""
        return {
            # 导航相关
            "navigation": {
                "sidebar": [
                    "nav",
                    ".sidebar", 
                    ".conversation-list",
                    "[data-testid='navigation']",
                    ".nav-panel"
                ],
                "main_content": [
                    "main",
                    ".conversation",
                    ".chat-container",
                    ".main-content"
                ]
            },
            
            # 任务操作相关
            "task_operations": {
                "input_field": [
                    "textarea[data-id]",
                    "#prompt-textarea", 
                    "textarea",
                    "[contenteditable='true']",
                    ".chat-input"
                ],
                "submit_button": [
                    "button[data-testid='send-button']",
                    ".send-button",
                    "button:has-text('Send')",
                    "button[type='submit']"
                ],
                "search_toggle": [
                    "button:has-text('Search')",
                    "[data-testid='search-toggle']",
                    ".search-toggle",
                    ".web-search-btn"
                ]
            },
            
            # 历史任务相关
            "history_elements": {
                "task_items": [
                    ".conversation-item",
                    "li[data-testid]",
                    ".chat-history-item",
                    "a[href*='/c/']",
                    ".conversation-link"
                ],
                "task_title": [
                    ".conversation-title",
                    "h3",
                    ".title",
                    ".chat-title"
                ],
                "task_date": [
                    ".timestamp",
                    ".date", 
                    "time",
                    ".created-time"
                ]
            },
            
            # 内容提取相关
            "content_extraction": {
                "messages": [
                    ".message",
                    ".chat-message",
                    "[data-message-id]",
                    ".conversation-turn"
                ],
                "user_message": [
                    ".message.user",
                    "[data-author='user']",
                    ".user-message"
                ],
                "assistant_message": [
                    ".message.assistant",
                    "[data-author='assistant']", 
                    ".assistant-message"
                ],
                "search_results": [
                    ".search-result",
                    ".web-search-result",
                    ".browsing-result"
                ]
            }
        }
    
    def _get_platform_keywords(self) -> Dict[str, List[str]]:
        """获取ChatGPT平台特定的关键词配置"""
        return {
            "title": ["chatgpt", "openai", "gpt", "chat"],
            "content": ["conversation", "chat", "search", "browsing"],
            "features": ["web search", "browsing", "real-time", "plugins"],
            "errors": ["rate limit", "quota", "network error", "timeout"]
        }
    
    def _get_platform_domains(self) -> List[str]:
        """获取ChatGPT平台域名列表"""
        return [
            "chatgpt.com",
            "openai.com", 
            "chat.openai.com"
        ]
    
    def _get_platform_capabilities(self) -> PlatformCapabilities:
        """获取平台能力配置"""
        capabilities = PlatformCapabilities(platform_name=self.name)
        
        # 核心能力
        capabilities.task_submission.level = CapabilityLevel.ADVANCED
        capabilities.task_submission.enabled = True
        capabilities.task_submission.description = "支持高级对话和搜索任务"
        
        capabilities.history_download.level = CapabilityLevel.BASIC
        capabilities.history_download.enabled = True
        capabilities.history_download.description = "支持对话历史下载"
        
        capabilities.file_management.level = CapabilityLevel.BASIC
        capabilities.file_management.enabled = True
        capabilities.file_management.description = "支持文件上传和下载"
        
        capabilities.content_extraction.level = CapabilityLevel.EXPERT
        capabilities.content_extraction.enabled = True
        capabilities.content_extraction.description = "支持智能内容提取"
        
        # 高级能力
        capabilities.ai_analysis.level = CapabilityLevel.EXPERT
        capabilities.ai_analysis.enabled = True
        capabilities.ai_analysis.description = "原生AI分析能力"
        
        capabilities.multi_modal.level = CapabilityLevel.ADVANCED
        capabilities.multi_modal.enabled = True
        capabilities.multi_modal.description = "支持图片、文档分析"
        
        capabilities.real_time_processing.level = CapabilityLevel.EXPERT
        capabilities.real_time_processing.enabled = True
        capabilities.real_time_processing.description = "实时响应处理"
        
        # 特殊能力 - ChatGPT的独特功能
        capabilities.web_search.level = CapabilityLevel.EXPERT
        capabilities.web_search.enabled = self.search_enabled
        capabilities.web_search.description = "实时网络搜索能力"
        
        return capabilities
    
    async def submit_task(
        self,
        topic: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """提交任务到ChatGPT平台"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            self.logger.info(f"开始提交ChatGPT任务: {title or topic[:50]}")
            
            # 检查是否需要启用网络搜索
            enable_search = kwargs.get("enable_search", self.search_enabled)
            
            # 构建增强的提示词
            enhanced_prompt = await self._build_enhanced_prompt(topic, enable_search)
            
            # 如果需要启用搜索，先点击搜索开关
            if enable_search:
                await self._enable_web_search()
            
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
            task_id = f"chatgpt_{int(time.time())}"
            
            self.logger.info(f"ChatGPT任务提交成功，任务ID: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"提交ChatGPT任务失败: {e}")
            raise PlatformError(f"提交任务失败: {e}", platform=self.name)
    
    async def _build_enhanced_prompt(self, topic: str, enable_search: bool) -> str:
        """构建增强的提示词"""
        # 基础提示词模板
        prompt_parts = []
        
        if enable_search:
            prompt_parts.append("请使用网络搜索功能来获取最新信息，然后")
        
        prompt_parts.append(f"请针对以下主题进行深入分析和研究：\n\n{topic}")
        
        # 添加结构化要求
        prompt_parts.append("""

请按照以下结构提供分析结果：

1. **概述** - 主题的基本概念和重要性
2. **现状分析** - 当前发展状态和趋势
3. **关键发现** - 重要的发现和洞察
4. **影响评估** - 对相关领域的影响
5. **未来展望** - 发展前景和建议

请确保：
- 信息准确且来源可靠
- 分析深入且具有实用价值
- 内容结构清晰，易于理解
- 包含具体的数据和案例支持""")
        
        return "\n".join(prompt_parts)
    
    async def _enable_web_search(self):
        """启用网络搜索功能"""
        try:
            # 查找搜索开关按钮
            search_selectors = self.platform_selectors.get("task_operations", {}).get("search_toggle", [])
            
            for selector in search_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        self.logger.info("已启用网络搜索功能")
                        await asyncio.sleep(1)  # 等待开关生效
                        return
                except:
                    continue
            
            self.logger.warning("未找到搜索开关，继续使用默认模式")
            
        except Exception as e:
            self.logger.warning(f"启用网络搜索失败: {e}")
    
    async def get_task_status(self, task_id: str) -> str:
        """获取ChatGPT任务状态"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 页面智能分析
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查错误状态
            if analysis["errors_detected"]:
                error_text = "; ".join(analysis["errors_detected"])
                if any(keyword in error_text.lower() for keyword in ["rate limit", "quota", "error", "failed"]):
                    self.logger.warning(f"检测到错误信息: {error_text}")
                    return "failed"
            
            # 检查是否还在生成中
            generating_indicators = [
                "生成中", "generating", "thinking", "typing",
                "停止生成", "stop generating"
            ]
            
            page_text = analysis["page_info"].get("visible_text", "").lower()
            if any(indicator in page_text for indicator in generating_indicators):
                self.logger.info("检测到正在生成状态")
                return "running"
            
            # 检查是否有完整的回复
            messages = await self._extract_conversation_messages()
            if messages and len(messages) >= 2:  # 至少有用户问题和AI回复
                last_message = messages[-1]
                if last_message.get("role") == "assistant" and len(last_message.get("content", "")) > 50:
                    self.logger.info("检测到完整的AI回复")
                    return "completed"
            
            # 默认返回运行中状态
            return "running"
            
        except Exception as e:
            self.logger.error(f"获取ChatGPT任务状态失败: {e}")
            return "failed"
    
    async def get_task_result(self, task_id: str):
        """获取ChatGPT任务结果"""
        from app.platforms.base_platform import TaskResult as BaseTaskResult
        
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 提取对话消息
            messages = await self._extract_conversation_messages()
            
            if not messages:
                raise PlatformError("未找到对话内容", platform=self.name)
            
            # 构建结果文本
            result_parts = []
            search_results = []
            
            for message in messages:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                
                if role == "user":
                    result_parts.append(f"**用户问题:**\n{content}\n")
                elif role == "assistant":
                    result_parts.append(f"**AI回复:**\n{content}\n")
                elif role == "search":
                    search_results.append(content)
            
            # 如果有搜索结果，添加到开头
            if search_results:
                result_parts.insert(0, f"**网络搜索结果:**\n{chr(10).join(search_results)}\n")
            
            result_text = "\n".join(result_parts)
            
            # 获取页面分析信息
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 构建元数据
            metadata = {
                "page_url": analysis["page_info"]["url"],
                "page_title": analysis["page_info"]["title"],
                "content_length": len(result_text),
                "message_count": len(messages),
                "search_enabled": self.search_enabled,
                "model_version": self.model_version,
                "extraction_method": "conversation_parsing",
                "has_search_results": len(search_results) > 0
            }
            
            self.logger.info(f"成功提取ChatGPT结果，消息数: {len(messages)}, 长度: {len(result_text)}")
            
            return BaseTaskResult(
                platform=self.name,
                task_id=task_id,
                success=True,
                result=result_text,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"获取ChatGPT任务结果失败: {e}")
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
    
    async def _determine_message_role(self, element) -> str:
        """确定消息角色"""
        try:
            # 检查元素类名和属性
            class_name = await element.get_attribute("class") or ""
            data_author = await element.get_attribute("data-author") or ""
            
            if "user" in class_name.lower() or data_author == "user":
                return "user"
            elif "assistant" in class_name.lower() or data_author == "assistant":
                return "assistant"
            
            # 通过父元素或兄弟元素判断
            parent = await element.query_selector("..")
            if parent:
                parent_class = await parent.get_attribute("class") or ""
                if "user" in parent_class.lower():
                    return "user"
                elif "assistant" in parent_class.lower():
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
    
    async def download_files(self, task_id: str, download_dir: Path) -> List[Path]:
        """下载ChatGPT任务文件"""
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取任务结果
            task_result = await self.get_task_result(task_id)
            
            downloaded_files = []
            
            # 保存主要内容
            content_file = download_dir / "conversation.txt"
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"ChatGPT对话记录\n")
                f.write(f"任务ID: {task_id}\n")
                f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"模型: {self.model_version}\n")
                f.write(f"搜索启用: {self.search_enabled}\n")
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
                        "model_version": self.model_version,
                        "search_enabled": self.search_enabled
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
            
            self.logger.info(f"ChatGPT文件下载完成: {len(downloaded_files)} 个文件")
            
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"下载ChatGPT文件失败: {e}")
            return [] 