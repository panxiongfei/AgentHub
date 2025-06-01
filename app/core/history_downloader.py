"""
历史任务批量下载器
用于批量下载平台历史任务的结果文件
"""

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import Page

from app.core.browser_engine import EnhancedBrowserEngine
from app.core.logger import get_logger


@dataclass
class HistoryTask:
    """历史任务信息"""
    id: str
    title: str
    date: str
    url: str
    status: str
    preview: str = ""
    element_selector: str = ""


@dataclass
class DownloadResult:
    """下载结果"""
    task: HistoryTask
    success: bool
    files: List[Path]
    content: str = ""
    error: str = ""
    # 新增AI总结相关字段
    ai_summary_generated: bool = False
    ai_summary_error: str = ""


class HistoryDownloader:
    """历史任务批量下载器"""
    
    def __init__(self, platform: str, browser_engine: EnhancedBrowserEngine):
        self.platform = platform
        self.browser_engine = browser_engine
        self.page = browser_engine.page
        self.logger = get_logger(f"history_downloader.{platform}")
        
        # 平台特定的历史任务选择器
        self.history_selectors = self._get_history_selectors()
        
        # AI总结功能开关
        self.enable_ai_summary = True
        self._ai_summary_generator = None
    
    def _get_ai_summary_generator(self):
        """获取AI总结生成器（延迟初始化）"""
        if self._ai_summary_generator is None:
            try:
                from app.core.task_summary_generator import TaskSummaryGenerator
                self._ai_summary_generator = TaskSummaryGenerator()
                self.logger.info("AI总结生成器初始化成功")
            except Exception as e:
                self.logger.warning(f"AI总结生成器初始化失败: {e}")
                self.enable_ai_summary = False
        
        return self._ai_summary_generator
    
    async def _generate_task_ai_summary(self, task_dir: Path, task_id: str) -> tuple[bool, str]:
        """为单个任务生成AI总结
        
        Args:
            task_dir: 任务目录路径
            task_id: 任务ID
            
        Returns:
            tuple[bool, str]: (是否成功, 错误信息)
        """
        if not self.enable_ai_summary:
            return False, "AI总结功能未启用"
            
        try:
            generator = self._get_ai_summary_generator()
            if not generator:
                return False, "AI总结生成器未初始化"
            
            self.logger.info(f"开始为任务 {task_id} 生成AI总结...")
            
            # 调用通用AI总结生成功能
            result = await generator.generate_task_summary(task_id, str(task_dir))
            
            if result.success:
                self.logger.info(f"任务 {task_id} AI总结生成成功")
                return True, ""
            else:
                error_msg = f"AI总结生成失败: {result.error}"
                self.logger.warning(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"生成AI总结时出错: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        
    def _get_history_selectors(self) -> Dict[str, List[str]]:
        """获取平台特定的历史任务选择器"""
        if self.platform == "skywork":
            return {
                "sidebar": [
                    ".sidebar",
                    ".history-panel",
                    ".left-panel",
                    ".conversation-list",
                    ".chat-history",
                    "[data-testid='sidebar']",
                    "[data-testid='history']",
                    ".nav-left",
                    ".side-nav"
                ],
                "task_items": [
                    ".sidebar li",  # 根据检查结果，历史任务在侧边栏的li元素中
                    "li",  # 所有li元素
                    ".conversation-item",
                    ".chat-item",
                    ".history-item",
                    ".task-item",
                    ".conversation",
                    "[data-conversation-id]",
                    "[data-chat-id]",
                    "a[href*='/chat/']",
                    "a[href*='/conversation/']",
                    ".list-item",
                    ".history-entry"
                ],
                "task_title": [
                    ".conversation-title",
                    ".chat-title",
                    ".task-title",
                    ".title",
                    "h3",
                    "h4",
                    ".name",
                    ".subject"
                ],
                "task_date": [
                    ".date",
                    ".time",
                    ".created-at",
                    ".timestamp",
                    "time",
                    "[datetime]",
                    ".meta"
                ]
            }
        elif self.platform == "manus":
            return {
                "sidebar": [
                    "div[style*='width']",  # 基于截图，侧边栏可能通过style定义宽度
                    ".sidebar",
                    ".left-panel",
                    "div:has(> div > div)",  # 嵌套的div结构
                    "nav",
                    ".history-panel",
                    ".conversation-list",
                    "[data-testid='sidebar']",
                    ".nav-left"
                ],
                "task_items": [
                    "span.truncate.text-sm.font-medium",  # 基于调试结果，任务标题在这个span中
                    "div:has(span.truncate.text-sm.font-medium)",  # 包含任务标题的div
                    "div.flex.items-center.gap-2",  # 基于调试发现的父元素结构
                    "div:has(span.truncate)",  # 包含截断文本的div
                    "li",  # 基于调试，确实有li元素
                    "div[role='button']",  # 可点击的div元素
                    "a",  # 链接元素
                    ".conversation-item",
                    ".chat-item", 
                    ".history-item",
                    ".task-item",
                    ".project-item",
                    ".research-item",
                    "[data-conversation-id]",
                    "[data-project-id]",
                    "[data-research-id]",
                    "a[href*='/project/']",
                    "a[href*='/research/']",
                    ".list-item"
                ],
                "task_title": [
                    "span.truncate.text-sm.font-medium",  # 精确匹配调试发现的元素
                    ".truncate",  # 截断文本元素
                    "span.truncate",  # 截断span元素
                    "h3",  # 基于截图，任务标题可能是h3元素
                    "div:first-child",  # div的第一个子元素
                    ".project-title",
                    ".conversation-title",
                    ".research-title",
                    ".task-title",
                    ".title",
                    "h4",
                    ".name",
                    "p:first-child",
                    "span:first-child"
                ],
                "task_date": [
                    "small",  # 基于截图，时间信息可能在small元素中
                    ".date",
                    ".time",
                    ".created-at",
                    ".timestamp",
                    "time",
                    "[datetime]",
                    "div:last-child",
                    "span:last-child",
                    "p:last-child"
                ]
            }
        else:
            return {}
    
    async def discover_history_tasks(self) -> List[HistoryTask]:
        """发现并解析历史任务列表"""
        try:
            self.logger.info("开始发现历史任务...")
            
            # 等待页面加载完成
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # 查找侧边栏
            sidebar = await self._find_sidebar()
            if not sidebar:
                self.logger.warning("未找到历史任务侧边栏")
                return []
            
            # 查找任务项
            task_items = await self._find_task_items(sidebar)
            if not task_items:
                self.logger.warning("未找到历史任务项")
                return []
            
            # 解析任务信息
            history_tasks = []
            for i, task_item in enumerate(task_items):
                try:
                    task = await self._parse_task_item(task_item, i)
                    if task:
                        history_tasks.append(task)
                        self.logger.info(f"发现任务: {task.title[:50]}...")
                except Exception as e:
                    self.logger.warning(f"解析任务项失败: {e}")
                    continue
            
            self.logger.info(f"总共发现 {len(history_tasks)} 个历史任务")
            return history_tasks
            
        except Exception as e:
            self.logger.error(f"发现历史任务失败: {e}")
            return []
    
    async def _find_sidebar(self):
        """查找侧边栏"""
        selectors = self.history_selectors.get("sidebar", [])
        
        for selector in selectors:
            try:
                sidebar_locator = self.page.locator(selector)
                count = await sidebar_locator.count()
                if count > 0 and await sidebar_locator.first.is_visible():
                    self.logger.info(f"找到侧边栏: {selector}")
                    return True  # 只需要返回找到了即可，后续使用page.locator
            except:
                continue
        
        return None
    
    async def _find_task_items(self, sidebar):
        """使用智能浏览器引擎查找任务项"""
        try:
            self.logger.info("开始使用智能引擎查找任务项...")
            
            # 使用browser engine进行页面智能分析
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查页面是否准备就绪
            if not analysis.get("content_readiness", False):
                self.logger.info("页面内容未完全加载，等待3秒...")
                await asyncio.sleep(3)
                # 重新分析
                analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 显示页面分析结果
            page_info = analysis.get("page_info", {})
            self.logger.info(f"页面分析: URL={page_info.get('url', '')[:50]}..., 标题={page_info.get('title', '')[:30]}...")
            
            # 查找交互机会 - 寻找可能的历史任务元素
            opportunities = analysis.get("interaction_opportunities", [])
            self.logger.info(f"发现 {len(opportunities)} 个交互机会")
            
            # 使用多种策略查找任务项
            all_items = []
            
            # 策略1: 使用browser engine的智能选择器
            items_from_engine = await self._find_items_with_smart_engine()
            if items_from_engine:
                all_items.extend(items_from_engine)
                self.logger.info(f"智能引擎找到 {len(items_from_engine)} 个项目")
            
            # 策略2: 基于已知任务标题进行文本匹配（如果是manus平台）
            if self.platform == "manus":
                items_from_text = await self._find_items_by_known_text()
                if items_from_text:
                    all_items.extend(items_from_text)
                    self.logger.info(f"文本匹配找到 {len(items_from_text)} 个项目")
            
            # 策略3: 传统选择器方法（fallback）
            items_from_selectors = await self._find_items_with_traditional_selectors()
            if items_from_selectors:
                all_items.extend(items_from_selectors)
                self.logger.info(f"传统选择器找到 {len(items_from_selectors)} 个项目")
            
            # 去重和过滤
            unique_items = await self._deduplicate_and_filter_items(all_items)
            
            self.logger.info(f"最终确定 {len(unique_items)} 个有效任务项")
            
            return unique_items[:20]  # 限制最多20个任务
            
        except Exception as e:
            self.logger.error(f"使用智能引擎查找任务项失败: {e}")
            # 降级到传统方法
            return await self._find_items_with_traditional_selectors()
    
    async def _find_items_with_smart_engine(self):
        """使用智能引擎的方法查找项目"""
        try:
            items = []
            
            # 使用browser engine分析页面结构
            # 查找可能包含历史任务的容器
            containers = await self.page.locator('div, section, aside, nav').all()
            
            for container in containers:
                try:
                    # 检查容器是否可见且包含实质内容
                    if not await container.is_visible():
                        continue
                    
                    text_content = await container.text_content()
                    if not text_content or len(text_content.strip()) < 10:
                        continue
                    
                    # 检查是否包含历史任务特征
                    has_task_features = await self._container_has_task_features(container, text_content)
                    
                    if has_task_features:
                        # 在此容器内查找子项目
                        child_items = await self._find_child_task_items(container)
                        items.extend(child_items)
                        
                except Exception as e:
                    continue
            
            return items
            
        except Exception as e:
            self.logger.warning(f"智能引擎查找失败: {e}")
            return []
    
    async def _container_has_task_features(self, container, text_content: str) -> bool:
        """检查容器是否具有历史任务特征"""
        try:
            # 检查文本内容是否包含任务关键词
            task_keywords = [
                "企业级", "Agent", "DeepSeek", "瑞幸", "AI", "人工智能", "分析", "研究",
                "项目", "任务", "历史", "conversation", "chat", "project", "task"
            ]
            
            text_lower = text_content.lower()
            has_keywords = any(keyword.lower() in text_lower for keyword in task_keywords)
            
            if not has_keywords:
                return False
            
            # 检查容器结构 - 是否包含多个子项目
            child_count = await container.locator('> *').count()
            if child_count < 2:  # 至少要有2个子元素才可能是任务列表
                return False
            
            # 检查是否在页面左侧（侧边栏特征）
            try:
                bbox = await container.bounding_box()
                if bbox and bbox.get('x', 1000) < 300:  # x坐标小于300，可能是左侧边栏
                    return True
            except:
                pass
            
            return has_keywords and child_count >= 3
            
        except Exception as e:
            return False
    
    async def _find_child_task_items(self, container):
        """在容器内查找子任务项"""
        try:
            items = []
            
            # 查找可能的任务项选择器
            child_selectors = [
                'div', 'li', 'a', 'button', '[role="button"]',
                'div[class*="item"]', 'div[class*="task"]', 'div[class*="project"]'
            ]
            
            for selector in child_selectors:
                try:
                    child_elements = await container.locator(selector).all()
                    
                    for element in child_elements:
                        if await element.is_visible():
                            text = await element.text_content()
                            
                            # 过滤掉太短或太长的文本（可能不是任务标题）
                            if text and 10 <= len(text.strip()) <= 200:
                                # 检查是否看起来像任务标题
                                if await self._looks_like_task_title(text.strip()):
                                    items.append(element)
                                    
                                    # 限制每个容器最多提取10个项目
                                    if len(items) >= 10:
                                        break
                    
                    if items:  # 如果找到了项目，就不再尝试其他选择器
                        break
                        
                except Exception:
                    continue
            
            return items
            
        except Exception as e:
            return []
    
    async def _looks_like_task_title(self, text: str) -> bool:
        """判断文本是否看起来像任务标题"""
        # 检查是否包含任务相关关键词
        task_indicators = [
            "企业级", "Agent", "DeepSeek", "瑞幸", "AI", "人工智能", "分析", "研究",
            "房价", "咖啡", "技术", "发展", "管理", "应用", "创新", "系统", "平台"
        ]
        
        return any(indicator in text for indicator in task_indicators)
    
    async def _find_items_by_known_text(self):
        """基于已知任务标题进行文本匹配（针对Manus平台）"""
        try:
            items = []
            
            # 基于调试发现的已知任务标题
            known_task_titles = [
                "企业级Agent",
                "DeepSeek",
                "唐镇房价", 
                "瑞幸AI",
                "人工智能在医疗",
                "AI技术发展"
            ]
            
            for title_part in known_task_titles:
                try:
                    # 查找包含该文本的元素
                    elements = await self.page.locator(f'text={title_part}').all()
                    
                    for element in elements:
                        if await element.is_visible():
                            # 获取包含该文本的最近的可点击父元素
                            clickable_parent = await self._find_clickable_parent(element)
                            if clickable_parent:
                                items.append(clickable_parent)
                
                except Exception as e:
                    self.logger.debug(f"查找文本 '{title_part}' 时出错: {e}")
                    continue
            
            return items
            
        except Exception as e:
            self.logger.warning(f"基于已知文本查找失败: {e}")
            return []
    
    async def _find_clickable_parent(self, element):
        """查找元素的可点击父元素"""
        try:
            # 向上查找可点击的父元素
            current = element
            max_depth = 5  # 最多向上查找5层
            
            for _ in range(max_depth):
                try:
                    # 检查当前元素是否可点击
                    tag_name = await current.evaluate("el => el.tagName.toLowerCase()")
                    
                    if tag_name in ['a', 'button']:
                        return current
                    
                    # 检查是否有click事件或role属性
                    has_click = await current.evaluate("""
                        el => {
                            const hasRole = el.getAttribute('role') === 'button';
                            const hasClick = el.onclick !== null;
                            const hasCursor = window.getComputedStyle(el).cursor === 'pointer';
                            return hasRole || hasClick || hasCursor;
                        }
                    """)
                    
                    if has_click:
                        return current
                    
                    # 向上查找父元素
                    parent = current.locator('..')
                    if await parent.count() > 0:
                        current = parent
                    else:
                        break
                        
                except Exception:
                    break
            
            return element  # 如果没找到更好的，返回原元素
            
        except Exception:
            return element
    
    async def _find_items_with_traditional_selectors(self):
        """使用传统选择器方法查找（fallback）"""
        try:
            all_items = []
            selectors = self.history_selectors.get("task_items", [])
            
            for selector in selectors:
                try:
                    # 根据不同平台调整查找策略
                    if self.platform == "manus":
                        # 对于manus，直接在页面中查找
                        items = await self.page.locator(selector).all()
                    else:
                        # 对于其他平台，在侧边栏内查找
                        if selector.startswith(".sidebar"):
                            items = await self.page.locator(selector).all()
                        else:
                            items = await self.page.locator(f".sidebar {selector}").all()
                    
                    if items:
                        # 过滤可见的项目
                        visible_items = []
                        for item in items:
                            if await item.is_visible():
                                visible_items.append(item)
                        
                        if visible_items:
                            self.logger.debug(f"选择器 {selector} 找到 {len(visible_items)} 个可见项目")
                            all_items.extend(visible_items)
                
                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 查找失败: {e}")
                    continue
            
            return all_items
            
        except Exception as e:
            self.logger.warning(f"传统选择器查找失败: {e}")
            return []
    
    async def _deduplicate_and_filter_items(self, all_items):
        """去重和过滤项目"""
        try:
            unique_items = []
            seen_positions = set()
            seen_texts = set()
            
            for item in all_items:
                try:
                    # 基于位置去重
                    bbox = await item.bounding_box()
                    if bbox:
                        position = (round(bbox["x"]), round(bbox["y"]))
                        if position in seen_positions:
                            continue
                        seen_positions.add(position)
                    
                    # 基于文本内容去重
                    text = await item.text_content()
                    if text:
                        text_key = text.strip()[:50]  # 取前50个字符作为key
                        if text_key in seen_texts:
                            continue
                        seen_texts.add(text_key)
                    
                    # 过滤掉明显不是任务的项目
                    if await self._is_valid_task_item(item, text):
                        unique_items.append(item)
                
                except Exception:
                    continue
            
            return unique_items
            
        except Exception as e:
            self.logger.warning(f"去重和过滤失败: {e}")
            return all_items[:20]  # 返回前20个作为fallback
    
    async def _is_valid_task_item(self, item, text: str) -> bool:
        """判断是否是有效的任务项"""
        try:
            if not text or len(text.strip()) < 5:
                return False
            
            # 过滤掉太长的文本（可能是页面内容而不是任务标题）
            if len(text.strip()) > 300:
                return False
            
            # 过滤掉明显的UI元素
            ui_keywords = [
                "登录", "注册", "设置", "帮助", "菜单", "导航", "首页", "返回",
                "login", "register", "settings", "help", "menu", "nav", "home", "back"
            ]
            
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in ui_keywords):
                return False
            
            return True
            
        except Exception:
            return True
    
    async def _parse_task_item(self, task_item, index: int) -> Optional[HistoryTask]:
        """解析单个任务项"""
        try:
            # 获取任务标题
            title = await self._extract_task_title(task_item)
            if not title:
                title = f"未知任务 {index + 1}"
            
            # 获取任务日期
            date = await self._extract_task_date(task_item)
            if not date:
                date = "未知日期"
            
            # 获取任务URL（如果是链接）
            url = await self._extract_task_url(task_item)
            
            # 获取任务预览内容
            preview = await self._extract_task_preview(task_item)
            
            # 生成任务ID
            task_id = f"{self.platform}_history_{index}_{int(time.time())}"
            
            # 获取元素选择器（用于后续点击）
            element_selector = await self._get_element_selector(task_item)
            
            return HistoryTask(
                id=task_id,
                title=title,
                date=date,
                url=url,
                status="discovered",
                preview=preview,
                element_selector=element_selector
            )
            
        except Exception as e:
            self.logger.error(f"解析任务项失败: {e}")
            return None
    
    async def _extract_task_title(self, task_item) -> str:
        """提取任务标题"""
        title_selectors = self.history_selectors.get("task_title", [])
        
        # 首先尝试从特定选择器获取
        for selector in title_selectors:
            try:
                title_element = task_item.locator(selector).first
                if await title_element.count() > 0:
                    title = await title_element.text_content()
                    if title and title.strip():
                        return title.strip()
            except:
                continue
        
        # 如果没找到，使用任务项的文本内容
        try:
            text = await task_item.text_content()
            if text:
                # 取前100个字符作为标题
                lines = text.strip().split('\n')
                return lines[0][:100] if lines else text[:100]
        except:
            pass
        
        return ""
    
    async def _extract_task_date(self, task_item) -> str:
        """提取任务日期"""
        date_selectors = self.history_selectors.get("task_date", [])
        
        for selector in date_selectors:
            try:
                date_element = task_item.locator(selector).first
                if await date_element.count() > 0:
                    # 尝试获取datetime属性
                    datetime_attr = await date_element.get_attribute("datetime")
                    if datetime_attr:
                        return datetime_attr
                    
                    # 尝试获取文本内容
                    date_text = await date_element.text_content()
                    if date_text and date_text.strip():
                        return date_text.strip()
            except:
                continue
        
        return ""
    
    async def _extract_task_url(self, task_item) -> str:
        """提取任务URL"""
        try:
            # 检查任务项本身是否是链接
            href = await task_item.get_attribute("href")
            if href:
                return href
            
            # 查找内部链接
            link = task_item.locator("a").first
            if await link.count() > 0:
                href = await link.get_attribute("href")
                if href:
                    return href
        except:
            pass
        
        return ""
    
    async def _extract_task_preview(self, task_item) -> str:
        """提取任务预览内容"""
        try:
            text = await task_item.text_content()
            if text:
                # 清理文本，移除多余空白
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                preview = ' '.join(lines)
                return preview[:200]  # 限制预览长度
        except:
            pass
        
        return ""
    
    async def _get_element_selector(self, task_item) -> str:
        """获取元素选择器"""
        try:
            # 尝试生成唯一选择器
            selector = await task_item.evaluate('''
                el => {
                    // 尝试获取唯一标识
                    if (el.id) return '#' + el.id;
                    
                    // 尝试data属性
                    const dataAttrs = ['data-conversation-id', 'data-chat-id', 'data-project-id', 'data-task-id'];
                    for (const attr of dataAttrs) {
                        const value = el.getAttribute(attr);
                        if (value) return '[' + attr + '="' + value + '"]';
                    }
                    
                    // 使用文本内容生成选择器
                    const text = el.textContent || '';
                    if (text.length > 0) {
                        const firstLine = text.split('\\n')[0].trim();
                        if (firstLine.length > 0 && firstLine.length <= 50) {
                            return el.tagName.toLowerCase() + ':has-text("' + firstLine.slice(0, 30) + '")';
                        }
                    }
                    
                    // 使用位置信息
                    const parent = el.parentElement;
                    if (parent) {
                        const siblings = Array.from(parent.children);
                        const index = siblings.indexOf(el);
                        return parent.tagName.toLowerCase() + ' > ' + el.tagName.toLowerCase() + ':nth-child(' + (index + 1) + ')';
                    }
                    
                    return el.tagName.toLowerCase();
                }
            ''')
            
            return selector or ""
        except:
            return ""
    
    async def download_task_content(self, task: HistoryTask, download_dir: Path) -> DownloadResult:
        """下载单个任务的内容"""
        try:
            self.logger.info(f"开始下载任务: {task.title[:50]}...")
            
            # 创建任务专用目录
            task_dir = download_dir / f"task_{task.id}"
            task_dir.mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # 点击任务项打开任务
            success = await self._open_task(task)
            if not success:
                return DownloadResult(
                    task=task,
                    success=False,
                    files=[],
                    error="无法打开任务"
                )
            
            # 等待任务内容加载
            await asyncio.sleep(3)
            
            # 智能等待内容加载完成
            wait_result = await self.browser_engine.smart_wait_for_content(timeout=30)
            
            # 提取任务内容
            content_result = await self.browser_engine.smart_extract_content()
            content = content_result.result if content_result.success else ""
            
            # 保存任务内容
            if content:
                content_file = task_dir / f"content.txt"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(f"任务标题: {task.title}\n")
                    f.write(f"任务日期: {task.date}\n")
                    f.write(f"任务URL: {task.url}\n")
                    f.write(f"下载时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    f.write(content)
                downloaded_files.append(content_file)
            
            # 查找并下载文件
            file_downloads = await self._download_task_files(task_dir)
            downloaded_files.extend(file_downloads)
            
            # 保存页面截图
            screenshot_file = task_dir / "screenshot.png"
            await self.page.screenshot(path=str(screenshot_file), full_page=True)
            downloaded_files.append(screenshot_file)
            
            # 保存页面HTML
            html_file = task_dir / "page.html"
            html_content = await self.page.content()
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            downloaded_files.append(html_file)
            
            # 保存任务元数据
            metadata_file = task_dir / "metadata.json"
            metadata = {
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "date": task.date,
                    "url": task.url,
                    "preview": task.preview
                },
                "download": {
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "platform": self.platform,
                    "files_count": len(downloaded_files),
                    "content_length": len(content),
                    "page_url": self.page.url,
                    "page_title": await self.page.title()
                }
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            downloaded_files.append(metadata_file)
            
            self.logger.info(f"任务下载完成: {len(downloaded_files)} 个文件")
            
            # 🔥 新增：自动生成AI总结
            ai_summary_success = False
            ai_summary_error = ""
            
            if self.enable_ai_summary:
                try:
                    self.logger.info(f"开始为任务 {task.id} 生成AI总结...")
                    ai_summary_success, ai_summary_error = await self._generate_task_ai_summary(task_dir, task.id)
                    
                    if ai_summary_success:
                        self.logger.info(f"✅ 任务 {task.id} AI总结生成成功")
                    else:
                        self.logger.warning(f"⚠️ 任务 {task.id} AI总结生成失败: {ai_summary_error}")
                        
                except Exception as e:
                    ai_summary_error = f"AI总结生成异常: {e}"
                    self.logger.error(f"❌ 任务 {task.id} AI总结生成异常: {e}")
            
            return DownloadResult(
                task=task,
                success=True,
                files=downloaded_files,
                content=content,
                ai_summary_generated=ai_summary_success,
                ai_summary_error=ai_summary_error
            )
            
        except Exception as e:
            self.logger.error(f"下载任务失败: {e}")
            return DownloadResult(
                task=task,
                success=False,
                files=[],
                error=str(e)
            )
    
    async def _open_task(self, task: HistoryTask) -> bool:
        """使用智能浏览器引擎打开任务"""
        try:
            self.logger.info(f"开始打开任务: {task.title[:50]}...")
            
            # 记录打开前的页面状态
            before_url = self.page.url
            before_title = await self.page.title()
            
            # 策略1: 如果有URL，直接导航
            if task.url and task.url.startswith(('http://', 'https://')):
                self.logger.info(f"直接导航到URL: {task.url}")
                await self.page.goto(task.url)
                
                # 等待页面加载完成
                await self.page.wait_for_load_state("networkidle", timeout=15000)
                
                # 使用browser engine验证页面加载成功
                wait_result = await self.browser_engine.smart_wait_for_content(timeout=10)
                return wait_result.success
            
            # 策略2: 使用element_selector进行智能点击
            if task.element_selector:
                success = await self._click_with_smart_engine(task.element_selector)
                if success:
                    self.logger.info("通过element_selector成功打开任务")
                    return True
            
            # 策略3: 基于任务标题进行智能文本匹配点击
            success = await self._click_by_text_matching(task.title)
            if success:
                self.logger.info("通过文本匹配成功打开任务")
                return True
            
            # 策略4: 重新查找任务元素并点击
            success = await self._refind_and_click_task(task)
            if success:
                self.logger.info("通过重新查找成功打开任务")
                return True
            
            self.logger.warning(f"所有打开策略都失败了: {task.title}")
            return False
            
        except Exception as e:
            self.logger.error(f"打开任务时出错: {e}")
            return False
    
    async def _click_with_smart_engine(self, element_selector: str) -> bool:
        """使用智能引擎点击元素"""
        try:
            # 等待元素出现
            element = await self.page.wait_for_selector(element_selector, timeout=10000)
            
            if not element:
                return False
            
            # 检查元素是否可见和可点击
            if not await element.is_visible():
                self.logger.debug("元素不可见，尝试滚动到元素位置")
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(1)
            
            if not await element.is_visible():
                return False
            
            # 智能点击
            await self._smart_click_element(element)
            
            # 等待页面响应
            await asyncio.sleep(3)
            
            # 使用browser engine检查是否成功跳转
            return await self._verify_navigation_success()
            
        except Exception as e:
            self.logger.debug(f"智能点击失败: {e}")
            return False
    
    async def _smart_click_element(self, element):
        """智能点击元素（包含多种点击策略）"""
        try:
            # 策略1: 普通点击
            await element.click()
            return True
            
        except Exception:
            try:
                # 策略2: 强制点击
                await element.click(force=True)
                return True
                
            except Exception:
                try:
                    # 策略3: JavaScript点击
                    await element.evaluate("el => el.click()")
                    return True
                    
                except Exception:
                    try:
                        # 策略4: 触发鼠标事件
                        await element.hover()
                        await asyncio.sleep(0.5)
                        await element.click()
                        return True
                        
                    except Exception as e:
                        self.logger.debug(f"所有点击策略都失败: {e}")
                        return False
    
    async def _click_by_text_matching(self, task_title: str) -> bool:
        """基于文本匹配进行智能点击"""
        try:
            # 提取任务标题的关键词
            keywords = await self._extract_title_keywords(task_title)
            
            for keyword in keywords:
                if len(keyword) < 3:  # 跳过太短的关键词
                    continue
                
                try:
                    # 查找包含关键词的元素
                    elements = await self.page.locator(f'text="{keyword}"').all()
                    
                    for element in elements:
                        if await element.is_visible():
                            # 查找可点击的父元素
                            clickable_element = await self._find_clickable_parent(element)
                            
                            if clickable_element:
                                # 尝试点击
                                success = await self._smart_click_element(clickable_element)
                                
                                if success:
                                    # 等待并验证
                                    await asyncio.sleep(3)
                                    if await self._verify_navigation_success():
                                        return True
                
                except Exception as e:
                    self.logger.debug(f"文本匹配 '{keyword}' 点击失败: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.debug(f"文本匹配点击失败: {e}")
            return False
    
    async def _extract_title_keywords(self, title: str) -> List[str]:
        """从任务标题中提取关键词"""
        # 移除常见的停用词
        stop_words = {'的', '在', '与', '和', '或', '及', '是', '为', '了', '等', '中', '上', '下', '前', '后'}
        
        # 分割标题并过滤
        keywords = []
        
        # 按长度优先：优先使用较长的短语
        words = title.split()
        
        # 添加完整短语（如果不太长）
        if 5 <= len(title) <= 30:
            keywords.append(title)
        
        # 添加较长的词
        for word in words:
            if len(word) >= 3 and word not in stop_words:
                keywords.append(word)
        
        # 添加一些子字符串
        if len(title) > 10:
            keywords.append(title[:10])  # 前10个字符
            keywords.append(title[-10:])  # 后10个字符
        
        return keywords[:5]  # 最多返回5个关键词
    
    async def _refind_and_click_task(self, task: HistoryTask) -> bool:
        """重新查找并点击任务"""
        try:
            # 重新发现当前页面的任务项
            current_tasks = await self.discover_history_tasks()
            
            # 查找匹配的任务
            matching_task = None
            for current_task in current_tasks:
                # 基于标题相似度匹配
                if self._calculate_title_similarity(task.title, current_task.title) > 0.7:
                    matching_task = current_task
                    break
            
            if matching_task and matching_task.element_selector:
                return await self._click_with_smart_engine(matching_task.element_selector)
            
            return False
            
        except Exception as e:
            self.logger.debug(f"重新查找并点击失败: {e}")
            return False
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """计算两个标题的相似度"""
        try:
            # 简单的字符级相似度计算
            title1_clean = title1.strip().lower()
            title2_clean = title2.strip().lower()
            
            if title1_clean == title2_clean:
                return 1.0
            
            # 计算包含关系
            if title1_clean in title2_clean or title2_clean in title1_clean:
                return 0.8
            
            # 计算公共字符比例
            common_chars = set(title1_clean) & set(title2_clean)
            total_chars = set(title1_clean) | set(title2_clean)
            
            if total_chars:
                return len(common_chars) / len(total_chars)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    async def _verify_navigation_success(self) -> bool:
        """验证导航是否成功"""
        try:
            # 等待页面稳定
            await asyncio.sleep(2)
            
            # 使用browser engine分析页面内容
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查URL是否发生变化
            current_url = self.page.url
            current_title = await self.page.title()
            
            # 对于Manus平台，检查URL是否包含任务ID
            if self.platform == "manus":
                # 如果URL包含任务ID（长度超过基础URL），认为导航成功
                base_url = "https://manus.im/app"
                if len(current_url) > len(base_url) + 5:  # 基础URL + 一些任务ID字符
                    self.logger.debug(f"检测到URL变化: {current_url}")
                    return True
                
                # 如果标题包含具体任务名而不只是"Manus"，也认为成功
                if current_title and current_title != "Manus" and " - Manus" in current_title:
                    self.logger.debug(f"检测到标题变化: {current_title}")
                    return True
            
            # 通用检查：检查是否有实质性内容
            content_readiness = analysis.get("content_readiness", False)
            
            # 检查页面是否有任务内容特征
            try:
                # 查找可能的内容区域
                content_indicators = [
                    'article', 'main', '.content', '.result', '.response', 
                    '.output', '.message', '.analysis', '.report'
                ]
                
                has_content = False
                for selector in content_indicators:
                    try:
                        elements = await self.page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                text = await element.text_content()
                                if text and len(text.strip()) > 100:  # 有实质性长文本内容
                                    has_content = True
                                    break
                        if has_content:
                            break
                    except:
                        continue
                
                if has_content:
                    self.logger.debug("检测到实质性内容")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"内容检测失败: {e}")
            
            # 宽松的成功条件：只要没有明显错误就认为可能成功
            errors = analysis.get("errors_detected", [])
            serious_errors = [
                "404", "not found", "error", "failed", "无法访问", "页面不存在"
            ]
            
            has_serious_error = any(
                any(err_keyword in str(error).lower() for err_keyword in serious_errors)
                for error in errors
            )
            
            if not has_serious_error:
                self.logger.debug("未检测到严重错误，认为导航可能成功")
                return True
                
            return False
            
        except Exception as e:
            self.logger.debug(f"验证导航状态失败: {e}")
            # 出错时采用乐观策略，返回True
            return True
    
    async def _download_task_files(self, task_dir: Path) -> List[Path]:
        """下载任务相关文件"""
        downloaded_files = []
        
        try:
            # 查找下载链接
            download_selectors = [
                'a[href*=".pdf"]',
                'a[href*=".docx"]',
                'a[href*=".doc"]',
                'a[href*=".xlsx"]',
                'a[href*=".xls"]',
                'a[href*=".pptx"]',
                'a[href*=".ppt"]',
                'a[href*=".txt"]',
                'a[href*=".csv"]',
                'a[href*=".zip"]',
                'a[download]',
                'button:has-text("下载")',
                'button:has-text("导出")',
                'button:has-text("保存")',
                '.download-link',
                '.export-button',
                '.save-button'
            ]
            
            for selector in download_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements:
                        if await element.is_visible():
                            try:
                                # 设置下载处理
                                async with self.page.expect_download(timeout=15000) as download_info:
                                    await element.click()
                                
                                download = await download_info.value
                                filename = download.suggested_filename or f"download_{len(downloaded_files)}.bin"
                                file_path = task_dir / filename
                                
                                await download.save_as(file_path)
                                downloaded_files.append(file_path)
                                self.logger.info(f"下载文件: {filename}")
                                
                            except Exception:
                                continue
                except Exception:
                    continue
        except Exception as e:
            self.logger.warning(f"文件下载过程出错: {e}")
        
        return downloaded_files
    
    async def batch_download_all(self, download_dir: Path) -> List[DownloadResult]:
        """批量下载所有历史任务"""
        try:
            # 发现历史任务
            history_tasks = await self.discover_history_tasks()
            
            if not history_tasks:
                self.logger.warning("未发现任何历史任务")
                return []
            
            # 创建下载目录
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # 批量下载
            results = []
            total_tasks = len(history_tasks)
            
            for i, task in enumerate(history_tasks, 1):
                self.logger.info(f"处理任务 {i}/{total_tasks}: {task.title[:50]}...")
                
                try:
                    result = await self.download_task_content(task, download_dir)
                    results.append(result)
                    
                    if result.success:
                        self.logger.info(f"✅ 任务 {i} 下载成功")
                    else:
                        self.logger.warning(f"❌ 任务 {i} 下载失败: {result.error}")
                    
                    # 任务间短暂停顿，避免过于频繁的请求
                    if i < total_tasks:
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    self.logger.error(f"处理任务 {i} 时出错: {e}")
                    results.append(DownloadResult(
                        task=task,
                        success=False,
                        files=[],
                        error=str(e)
                    ))
            
            # 生成下载报告（包含AI总结统计）
            await self._generate_download_report(results, download_dir)
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量下载失败: {e}")
            return []
    
    async def _generate_download_report(self, results: List[DownloadResult], download_dir: Path):
        """生成下载报告"""
        try:
            report_file = download_dir / "download_report.json"
            
            successful_downloads = [r for r in results if r.success]
            failed_downloads = [r for r in results if not r.success]
            
            # 🔥 新增：AI总结统计
            ai_summary_success = [r for r in successful_downloads if getattr(r, 'ai_summary_generated', False)]
            ai_summary_failed = [r for r in successful_downloads if not getattr(r, 'ai_summary_generated', False)]
            
            report = {
                "summary": {
                    "total_tasks": len(results),
                    "successful": len(successful_downloads),
                    "failed": len(failed_downloads),
                    "success_rate": len(successful_downloads) / len(results) if results else 0,
                    "download_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "platform": self.platform,
                    # AI总结统计
                    "ai_summary_enabled": self.enable_ai_summary,
                    "ai_summary_successful": len(ai_summary_success),
                    "ai_summary_failed": len(ai_summary_failed),
                    "ai_summary_rate": len(ai_summary_success) / len(successful_downloads) if successful_downloads else 0
                },
                "successful_tasks": [
                    {
                        "id": r.task.id,
                        "title": r.task.title,
                        "date": r.task.date,
                        "files_count": len(r.files),
                        "content_length": len(r.content),
                        # AI总结状态
                        "ai_summary_generated": getattr(r, 'ai_summary_generated', False),
                        "ai_summary_error": getattr(r, 'ai_summary_error', "")
                    }
                    for r in successful_downloads
                ],
                "failed_tasks": [
                    {
                        "id": r.task.id,
                        "title": r.task.title,
                        "date": r.task.date,
                        "error": r.error
                    }
                    for r in failed_downloads
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"下载报告已生成: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成下载报告失败: {e}") 