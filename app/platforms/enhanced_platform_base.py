"""
增强版平台基类
集成智能浏览器操作引擎
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from app.core.exceptions import PlatformError, PlatformConnectionError
from app.platforms.base_platform import BasePlatform, TaskResult
from app.core.browser_engine import EnhancedBrowserEngine
from app.core.history_downloader import HistoryDownloader, DownloadResult
from app.core.logger import get_logger


class EnhancedPlatformBase(BasePlatform, ABC):
    """增强版平台基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.browser_engine: Optional[EnhancedBrowserEngine] = None
        self.history_downloader: Optional[HistoryDownloader] = None
        
        # 平台特定配置
        self.base_url = config.get("base_url", "")
        self.debug_port = config.get("debug_port", 9222)
        self.timeout = config.get("timeout", 30000)
        
        # 平台特定选择器配置
        self.platform_selectors = self._get_platform_selectors()
        
    @abstractmethod
    def _get_platform_selectors(self) -> Dict[str, List[str]]:
        """获取平台特定的选择器配置"""
        pass
    
    @abstractmethod
    def _get_platform_keywords(self) -> Dict[str, List[str]]:
        """获取平台特定的关键词配置"""
        pass
    
    async def _connect_to_existing_browser(self) -> None:
        """连接到现有的Chrome浏览器实例"""
        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # 连接到现有的Chrome实例
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            
            # 获取所有上下文
            contexts = self.browser.contexts
            if not contexts:
                raise PlatformConnectionError(self.name, Exception("没有找到浏览器上下文"))
            
            # 使用第一个上下文
            self.context = contexts[0]
            
            # 查找平台页面或创建新页面
            self.page = await self._find_or_create_platform_page()
            
            # 初始化增强浏览器引擎
            if self.page:
                self.browser_engine = EnhancedBrowserEngine(self.page)
                
                # 自定义平台选择器
                if self.platform_selectors:
                    self.browser_engine.selector_strategies.update(self.platform_selectors)
                
                # 初始化历史下载器
                self.history_downloader = HistoryDownloader(self.name, self.browser_engine)
                
                self.logger.info(f"增强浏览器引擎已初始化")
            
        except Exception as e:
            self.logger.error(f"连接浏览器失败: {e}")
            raise PlatformConnectionError(self.name, e)
    
    async def _find_or_create_platform_page(self) -> Page:
        """查找或创建平台页面"""
        # 查找现有平台页面
        pages = self.context.pages
        platform_page = None
        
        platform_domains = self._get_platform_domains()
        
        for page in pages:
            url = page.url
            if any(domain in url.lower() for domain in platform_domains):
                platform_page = page
                self.logger.info(f"找到现有{self.name}页面: {url}")
                break
        
        if platform_page:
            return platform_page
        else:
            # 创建新标签页并导航到平台
            new_page = await self.context.new_page()
            await new_page.goto(self.base_url)
            self.logger.info(f"创建新{self.name}页面: {self.base_url}")
            return new_page
    
    @abstractmethod
    def _get_platform_domains(self) -> List[str]:
        """获取平台域名列表用于页面识别"""
        pass
    
    async def test_connection(self) -> bool:
        """测试平台连接"""
        try:
            await self._connect_to_existing_browser()
            
            if not self.browser_engine:
                return False
            
            # 使用增强引擎分析页面
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查页面是否包含平台相关内容
            page_info = analysis["page_info"]
            
            platform_keywords = self._get_platform_keywords()
            title_keywords = platform_keywords.get("title", [])
            
            title_match = any(keyword in page_info["title"].lower() for keyword in title_keywords)
            
            if title_match or any(domain in page_info["url"] for domain in self._get_platform_domains()):
                self.logger.info(f"{self.name}平台连接成功")
                return True
            else:
                self.logger.warning(f"页面内容不匹配: {page_info}")
                return False
        
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    async def submit_task(
        self,
        topic: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """提交任务到平台"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            self.logger.info(f"开始提交任务: {title or topic[:50]}")
            
            # 页面智能分析
            analysis = await self.browser_engine.analyze_page_intelligence()
            self.logger.info(f"页面分析: {analysis['recommendations']}")
            
            # 等待页面准备就绪
            if analysis["page_info"]["load_state"] != "complete":
                await asyncio.sleep(3)
            
            # 智能输入文本
            input_result = await self.browser_engine.smart_input_text(topic)
            
            if not input_result.success:
                raise PlatformError(f"输入文本失败: {input_result.error}", platform=self.name)
            
            self.logger.info(f"成功输入命题: {topic[:100]}...")
            
            # 智能提交
            submit_result = await self.browser_engine.smart_submit()
            
            if not submit_result.success:
                raise PlatformError(f"提交任务失败: {submit_result.error}", platform=self.name)
            
            # 生成任务ID
            task_id = f"{self.name}_{int(time.time())}"
            
            self.logger.info(f"任务提交成功，任务ID: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"提交任务失败: {e}")
            raise PlatformError(f"提交任务失败: {e}", platform=self.name)
    
    async def get_task_status(self, task_id: str) -> str:
        """获取任务状态"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 页面智能分析
            analysis = await self.browser_engine.analyze_page_intelligence()
            
            # 检查错误状态
            if analysis["errors_detected"]:
                error_text = "; ".join(analysis["errors_detected"])
                if any(keyword in error_text.lower() for keyword in ["积分", "insufficient", "error", "错误", "失败", "限制"]):
                    self.logger.warning(f"检测到错误信息: {error_text}")
                    return "failed"
            
            # 检查加载状态
            loading_elements = [
                op for op in analysis["interaction_opportunities"] 
                if op["type"] == "loading"
            ]
            
            if loading_elements:
                self.logger.info("检测到加载状态")
                return "running"
            
            # 检查内容就绪状态
            if analysis["content_readiness"]:
                self.logger.info("检测到内容已生成")
                return "completed"
            
            # 默认返回运行中状态
            return "running"
            
        except Exception as e:
            self.logger.error(f"获取任务状态失败: {e}")
            return "failed"
    
    async def get_task_result(self, task_id: str) -> TaskResult:
        """获取任务结果"""
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 智能提取内容
            extract_result = await self.browser_engine.smart_extract_content()
            
            if extract_result.success:
                result_text = extract_result.result
                
                # 获取页面分析信息
                analysis = await self.browser_engine.analyze_page_intelligence()
                
                # 构建元数据
                metadata = {
                    "page_url": analysis["page_info"]["url"],
                    "page_title": analysis["page_info"]["title"],
                    "content_length": len(result_text),
                    "extraction_method": "smart_engine",
                    "analysis": analysis
                }
                
                self.logger.info(f"成功提取结果，长度: {len(result_text)}")
                
                return TaskResult(
                    platform=self.name,
                    task_id=task_id,
                    success=True,
                    result=result_text,
                    metadata=metadata
                )
            else:
                self.logger.error(f"提取结果失败: {extract_result.error}")
                return TaskResult(
                    platform=self.name,
                    task_id=task_id,
                    success=False,
                    result=f"提取结果失败: {extract_result.error}"
                )
            
        except Exception as e:
            self.logger.error(f"获取任务结果失败: {e}")
            return TaskResult(
                platform=self.name,
                task_id=task_id,
                success=False,
                result=f"获取结果失败: {e}"
            )
    
    async def download_files(self, task_id: str, download_dir: Path) -> List[Path]:
        """下载任务相关文件"""
        downloaded_files = []
        
        try:
            if not self.browser_engine:
                await self._connect_to_existing_browser()
            
            # 创建下载目录
            download_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("开始保存页面内容和下载文件...")
            
            # 尝试下载文件
            try:
                download_selectors = [
                    'a[href*=".pdf"]',
                    'a[href*=".docx"]', 
                    'a[href*=".xlsx"]',
                    'a[href*=".txt"]',
                    'a[download]',
                    'button:has-text("下载")',
                    'button:has-text("导出")'
                ]
                
                for selector in download_selectors:
                    try:
                        elements = await self.page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                try:
                                    async with self.page.expect_download(timeout=10000) as download_info:
                                        await element.click()
                                    
                                    download = await download_info.value
                                    filename = download.suggested_filename or f"{self.name}_file_{len(downloaded_files)}.bin"
                                    file_path = download_dir / filename
                                    
                                    await download.save_as(file_path)
                                    downloaded_files.append(file_path)
                                    self.logger.info(f"下载文件: {filename}")
                                    
                                except Exception:
                                    continue
                    except Exception:
                        continue
            except Exception as e:
                self.logger.warning(f"文件下载失败: {e}")
            
            # 保存页面内容作为备用
            try:
                # 1. 页面截图
                screenshot_path = download_dir / f"{self.name}_screenshot_{task_id}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                downloaded_files.append(screenshot_path)
                
                # 2. 页面HTML
                html_path = download_dir / f"{self.name}_page_{task_id}.html"
                content = await self.page.content()
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                downloaded_files.append(html_path)
                
                # 3. 结果文本
                result = await self.get_task_result(task_id)
                if result.result and len(result.result.strip()) > 10:
                    text_path = download_dir / f"{self.name}_result_{task_id}.txt"
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(f"任务ID: {task_id}\n")
                        f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"平台: {self.name}\n")
                        f.write("="*50 + "\n\n")
                        f.write(result.result)
                    downloaded_files.append(text_path)
                
                # 4. 元数据和操作历史
                metadata_path = download_dir / f"{self.name}_metadata_{task_id}.json"
                metadata = {
                    "task_id": task_id,
                    "platform": self.name,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "page_url": self.page.url,
                    "page_title": await self.page.title(),
                    "files_downloaded": len(downloaded_files),
                    "browser_engine_summary": self.browser_engine.get_operation_summary() if self.browser_engine else {}
                }
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                downloaded_files.append(metadata_path)
                
                self.logger.info(f"保存了 {len(downloaded_files)} 个文件")
                
            except Exception as e:
                self.logger.error(f"保存页面内容失败: {e}")
            
        except Exception as e:
            self.logger.error(f"下载文件过程出错: {e}")
        
        return downloaded_files
    
    async def execute_full_task(
        self,
        topic: str,
        title: Optional[str] = None,
        download_dir: Optional[Path] = None,
        **kwargs
    ) -> TaskResult:
        """执行完整任务流程（增强版）"""
        task_id = None
        result = None
        
        try:
            # 提交任务
            task_id = await self.submit_task(topic, title, **kwargs)
            self.logger.info(f"任务已提交: {task_id}")
            
            # 智能等待内容生成
            wait_result = await self.browser_engine.smart_wait_for_content(timeout=1800)  # 30分钟
            
            if wait_result.success:
                self.logger.info("内容生成完成")
            else:
                self.logger.warning(f"等待内容超时或失败: {wait_result.error}")
            
        except KeyboardInterrupt:
            self.logger.warning("任务被用户中断，正在尝试获取中间结果...")
        except Exception as e:
            self.logger.error(f"任务执行出错: {e}，但将尝试获取中间结果")
        
        # 无论如何都尝试获取结果
        try:
            if not task_id:
                task_id = f"{self.name}_interrupted_{int(time.time())}"
            
            result = await self.get_task_result(task_id)
            self.logger.info(f"获取到结果，长度: {len(result.result)}")
            
        except Exception as e:
            self.logger.error(f"获取结果失败: {e}")
            result = TaskResult(
                platform=self.name,
                task_id=task_id or f"{self.name}_error_{int(time.time())}",
                success=False,
                result=f"获取结果失败: {e}",
                metadata={"error": str(e)}
            )
        
        # 下载文件和保存
        if download_dir and result:
            try:
                downloaded_files = await self.download_files(task_id, download_dir)
                result.files = downloaded_files
                self.logger.info(f"已保存 {len(downloaded_files)} 个文件到 {download_dir}")
            except Exception as e:
                self.logger.error(f"文件保存失败: {e}")
        
        return result
    
    async def download_history_tasks(self, download_dir: Path) -> List[DownloadResult]:
        """批量下载历史任务"""
        try:
            if not self.history_downloader:
                await self._connect_to_existing_browser()
            
            if not self.history_downloader:
                raise PlatformError("历史下载器未初始化", platform=self.name)
            
            self.logger.info("开始批量下载历史任务...")
            
            # 确保在主页面
            await self.page.goto(self.base_url)
            await asyncio.sleep(3)
            
            # 执行批量下载
            results = await self.history_downloader.batch_download_all(download_dir)
            
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            self.logger.info(f"历史任务下载完成: 成功 {len(successful)}, 失败 {len(failed)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量下载历史任务失败: {e}")
            raise PlatformError(f"批量下载历史任务失败: {e}", platform=self.name)
    
    async def discover_history_tasks(self):
        """发现历史任务列表"""
        try:
            if not self.history_downloader:
                await self._connect_to_existing_browser()
            
            if not self.history_downloader:
                raise PlatformError("历史下载器未初始化", platform=self.name)
            
            # 确保在主页面
            await self.page.goto(self.base_url)
            await asyncio.sleep(3)
            
            # 发现历史任务
            tasks = await self.history_downloader.discover_history_tasks()
            
            self.logger.info(f"发现 {len(tasks)} 个历史任务")
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"发现历史任务失败: {e}")
            raise PlatformError(f"发现历史任务失败: {e}", platform=self.name)
    
    async def close(self):
        """关闭连接"""
        try:
            if self.browser_engine:
                # 保存操作历史摘要
                summary = self.browser_engine.get_operation_summary()
                self.logger.info(f"浏览器引擎操作摘要: {summary}")
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.browser = None
            self.context = None
            self.page = None
            self.browser_engine = None
            self.history_downloader = None
            
        except Exception as e:
            self.logger.error(f"关闭连接失败: {e}") 