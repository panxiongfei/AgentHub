"""
Skywork平台实现
使用Playwright连接现有Chrome浏览器实例进行自动化操作
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from app.core.exceptions import PlatformError, PlatformConnectionError
from app.platforms.base_platform import BasePlatform, TaskResult


class SkyworkPlatform(BasePlatform):
    """Skywork平台实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("skywork", config)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Skywork相关配置
        self.base_url = config.get("base_url", "https://skywork.ai")
        self.debug_port = config.get("debug_port", 9222)
        self.timeout = config.get("timeout", 30000)  # 30秒超时
        
    async def _connect_to_existing_browser(self) -> None:
        """连接到现有的Chrome浏览器实例"""
        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # 连接到现有的Chrome实例（通过调试端口）
            self.browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            
            # 获取所有上下文
            contexts = self.browser.contexts
            if not contexts:
                raise PlatformConnectionError("skywork", Exception("没有找到浏览器上下文"))
            
            # 使用第一个上下文
            self.context = contexts[0]
            
            # 查找Skywork页面
            pages = self.context.pages
            skywork_page = None
            
            for page in pages:
                url = page.url
                if "skywork" in url.lower() or "skywork.ai" in url.lower():
                    skywork_page = page
                    break
            
            if skywork_page:
                self.page = skywork_page
                self.logger.info(f"找到Skywork页面: {self.page.url}")
            else:
                # 如果没有找到Skywork页面，创建新标签页
                self.page = await self.context.new_page()
                await self.page.goto(self.base_url)
                self.logger.info("创建新的Skywork页面")
            
        except Exception as e:
            self.logger.error(f"连接浏览器失败: {e}")
            raise PlatformConnectionError("skywork", e)
    
    async def test_connection(self) -> bool:
        """测试平台连接"""
        try:
            await self._connect_to_existing_browser()
            
            # 检查页面是否包含Skywork相关内容
            if self.page:
                await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
                title = await self.page.title()
                
                if "skywork" in title.lower() or "登录" in title or "dashboard" in title.lower() or "天工" in title:
                    self.logger.info("Skywork平台连接成功")
                    return True
                else:
                    self.logger.warning(f"页面标题不匹配: {title}")
                    return False
            
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
        """提交任务到Skywork平台"""
        try:
            if not self.page:
                await self._connect_to_existing_browser()
            
            self.logger.info(f"开始提交任务: {title or topic[:50]}")
            
            # 等待页面加载完成
            await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            # 查找输入框 - Skywork的选择器
            input_selectors = [
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="请输入"]',
                'textarea[placeholder*="问题"]',
                'textarea[placeholder*="内容"]',
                'textarea[placeholder*="想问"]',
                'textarea[placeholder*="想了解"]',
                'input[type="text"][placeholder*="输入"]',
                'div[contenteditable="true"]',
                '.input-area textarea',
                '.question-input',
                '.chat-input textarea',
                '.message-input textarea',
                '.prompt-input',
                'textarea',
                'input[type="text"]'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = await self.page.wait_for_selector(
                        selector, 
                        timeout=5000
                    )
                    if input_element:
                        # 检查是否可见和可用
                        is_visible = await input_element.is_visible()
                        is_enabled = await input_element.is_enabled()
                        if is_visible and is_enabled:
                            self.logger.info(f"找到输入框: {selector}")
                            break
                        else:
                            input_element = None
                except:
                    continue
            
            if not input_element:
                # 尝试点击页面中的相关按钮来激活输入框
                click_selectors = [
                    'button:has-text("新建")',
                    'button:has-text("创建")',
                    'button:has-text("开始")',
                    'button:has-text("新对话")',
                    'button:has-text("开始对话")',
                    '.new-chat',
                    '.start-button',
                    '.new-conversation',
                    '.chat-start'
                ]
                
                for selector in click_selectors:
                    try:
                        button = await self.page.wait_for_selector(selector, timeout=2000)
                        if button and await button.is_visible():
                            await button.click()
                            self.logger.info(f"点击了按钮: {selector}")
                            await self.page.wait_for_timeout(2000)
                            
                            # 重新查找输入框
                            for input_selector in input_selectors:
                                try:
                                    input_element = await self.page.wait_for_selector(
                                        input_selector, 
                                        timeout=3000
                                    )
                                    if input_element and await input_element.is_visible():
                                        self.logger.info(f"找到输入框: {input_selector}")
                                        break
                                except:
                                    continue
                            if input_element:
                                break
                    except:
                        continue
            
            if not input_element:
                # 如果还是找不到，截图保存用于调试
                screenshot_path = Path("data/temp/skywork_debug.png")
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                await self.page.screenshot(path=str(screenshot_path))
                
                raise PlatformError(
                    "无法找到输入框，请检查Skywork页面是否正确加载",
                    platform="skywork"
                )
            
            # 清空输入框并输入内容
            await input_element.click()
            await input_element.fill("")
            await input_element.type(topic)
            
            self.logger.info(f"已输入命题: {topic[:100]}...")
            
            # 查找提交按钮
            submit_selectors = [
                'button:has-text("发送")',
                'button:has-text("提交")',
                'button:has-text("确定")',
                'button:has-text("开始")',
                'button:has-text("提问")',
                'button:has-text("询问")',
                'button[type="submit"]',
                '.submit-button',
                '.send-button',
                '.ask-button',
                'button[aria-label*="发送"]',
                'button[aria-label*="submit"]',
                'button[aria-label*="提交"]'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(
                        selector, 
                        timeout=3000
                    )
                    if submit_button:
                        # 检查按钮是否可见和可点击
                        is_visible = await submit_button.is_visible()
                        is_enabled = await submit_button.is_enabled()
                        
                        if is_visible and is_enabled:
                            self.logger.info(f"找到提交按钮: {selector}")
                            break
                        else:
                            submit_button = None
                except:
                    continue
            
            if not submit_button:
                # 尝试按Enter键提交
                self.logger.info("未找到提交按钮，尝试按Enter键")
                await input_element.press("Enter")
            else:
                # 点击提交按钮
                await submit_button.click()
                self.logger.info("已点击提交按钮")
            
            # 等待任务提交完成
            await self.page.wait_for_timeout(3000)
            
            # 生成任务ID（时间戳）
            task_id = f"skywork_{int(time.time())}"
            
            self.logger.info(f"任务提交成功，任务ID: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"提交任务失败: {e}")
            raise PlatformError(f"提交任务失败: {e}", platform="skywork")
    
    async def get_task_status(self, task_id: str) -> str:
        """获取任务状态"""
        try:
            if not self.page:
                await self._connect_to_existing_browser()
            
            # 等待页面内容更新
            await self.page.wait_for_timeout(2000)
            
            # 检查页面中是否有加载指示器
            loading_selectors = [
                '.loading',
                '.spinner',
                '[data-loading="true"]',
                '.generating',
                '.thinking',
                '.processing',
                '.typing',
                '.ai-thinking',
                '.dots-loading'
            ]
            
            for selector in loading_selectors:
                try:
                    loading_element = await self.page.query_selector(selector)
                    if loading_element and await loading_element.is_visible():
                        self.logger.info("检测到加载状态")
                        return "running"
                except:
                    continue
            
            # 检查是否有错误信息
            error_selectors = [
                '.error',
                '.failed',
                '.insufficient',
                '.limit-exceeded',
                '[class*="error"]',
                '[class*="fail"]',
                '.warning'
            ]
            
            for selector in error_selectors:
                try:
                    error_element = await self.page.query_selector(selector)
                    if error_element and await error_element.is_visible():
                        error_text = await error_element.text_content()
                        if error_text and any(keyword in error_text for keyword in ["积分", "insufficient", "error", "错误", "失败", "限制"]):
                            self.logger.warning(f"检测到错误信息: {error_text}")
                            return "failed"
                except:
                    continue
            
            # 检查是否有新的内容生成
            content_selectors = [
                '.message',
                '.response',
                '.result',
                '.answer',
                '.generated-content',
                '.chat-message',
                '.ai-message',
                '.assistant-message',
                '.output',
                '.reply'
            ]
            
            for selector in content_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        # 检查最后一个元素是否包含实质内容
                        last_element = elements[-1]
                        text_content = await last_element.text_content()
                        
                        if text_content and len(text_content.strip()) > 10:
                            self.logger.info("检测到内容生成")
                            # 检查内容是否看起来完整
                            if len(text_content.strip()) > 100:
                                return "completed"
                            else:
                                return "running"
                except:
                    continue
            
            # 默认返回运行中状态
            return "running"
            
        except Exception as e:
            self.logger.error(f"获取任务状态失败: {e}")
            return "failed"
    
    async def get_task_result(self, task_id: str) -> TaskResult:
        """获取任务结果（包括中间结果）"""
        try:
            if not self.page:
                await self._connect_to_existing_browser()
            
            # 等待内容完全加载
            await self.page.wait_for_timeout(3000)
            
            # 查找结果内容 - Skywork的选择器
            result_selectors = [
                '.message:last-child',
                '.response:last-child', 
                '.result:last-child',
                '.answer:last-child',
                '.generated-content:last-child',
                '.chat-message:last-child',
                '.ai-message:last-child',
                '.assistant-message:last-child',
                '.output:last-child',
                '.reply:last-child',
                # 获取所有消息内容
                '.message',
                '.response',
                '.result', 
                '.answer',
                '.generated-content',
                '.chat-message',
                '.ai-message',
                '.assistant-message',
                '.output',
                '.reply'
            ]
            
            result_text = ""
            all_content = []
            
            # 尝试获取所有可能的内容
            for selector in result_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and len(text.strip()) > 20:  # 过滤掉太短的内容
                            text_clean = text.strip()
                            if text_clean not in all_content:  # 避免重复
                                all_content.append(text_clean)
                except:
                    continue
            
            # 合并所有内容
            if all_content:
                # 取最长的内容作为主要结果
                result_text = max(all_content, key=len)
                
                # 如果有多个内容，也记录其他内容
                if len(all_content) > 1:
                    other_content = [content for content in all_content if content != result_text]
                    if other_content:
                        result_text += "\n\n=== 其他内容 ===\n" + "\n---\n".join(other_content)
            
            # 如果还是没有找到内容，尝试获取页面主要文本
            if not result_text:
                try:
                    # 获取页面中所有可见文本
                    result_text = await self.page.evaluate('''
                        () => {
                            const excludeSelectors = ['nav', 'header', 'footer', 'script', 'style', '.sidebar', '.menu'];
                            const contentElements = document.querySelectorAll('div, p, span, article, section');
                            let allTexts = [];
                            
                            contentElements.forEach(el => {
                                // 跳过导航等元素
                                if (excludeSelectors.some(selector => el.closest(selector))) {
                                    return;
                                }
                                
                                const text = el.textContent || '';
                                if (text.length > 50 && text.length < 10000) {
                                    allTexts.push(text.trim());
                                }
                            });
                            
                            // 去重并按长度排序
                            const uniqueTexts = [...new Set(allTexts)];
                            uniqueTexts.sort((a, b) => b.length - a.length);
                            
                            // 返回最长的几个文本
                            return uniqueTexts.slice(0, 3).join('\\n\\n=== 分段 ===\\n\\n');
                        }
                    ''')
                except:
                    result_text = "无法获取页面内容"
            
            # 如果还是没有内容，至少记录页面标题和URL
            if not result_text or len(result_text.strip()) < 10:
                try:
                    title = await self.page.title()
                    url = self.page.url
                    result_text = f"页面标题: {title}\n页面URL: {url}\n注意: 未能获取到具体内容，可能需要手动查看页面"
                except:
                    result_text = "无法获取任何内容"
            
            # 判断是否成功（有实质内容就算成功）
            success = len(result_text.strip()) > 20
            
            self.logger.info(f"获取到结果，长度: {len(result_text)}, 成功: {success}")
            
            return TaskResult(
                platform="skywork",
                task_id=task_id,
                success=success,
                result=result_text,  # 保存完整结果
                metadata={
                    "full_result_length": len(result_text),
                    "page_url": self.page.url,
                    "page_title": await self.page.title() if self.page else "Unknown",
                    "content_pieces": len(all_content) if all_content else 0
                }
            )
            
        except Exception as e:
            self.logger.error(f"获取任务结果失败: {e}")
            return TaskResult(
                platform="skywork",
                task_id=task_id,
                success=False,
                result=f"获取结果失败: {e}"
            )
    
    async def download_files(self, task_id: str, download_dir: Path) -> List[Path]:
        """下载任务相关文件（包括中间产物）"""
        downloaded_files = []
        
        try:
            if not self.page:
                await self._connect_to_existing_browser()
            
            # 创建下载目录
            download_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("开始查找和下载文件...")
            
            # 查找下载链接
            download_selectors = [
                'a[href*=".pdf"]',
                'a[href*=".docx"]', 
                'a[href*=".xlsx"]',
                'a[href*=".pptx"]',
                'a[href*=".zip"]',
                'a[href*=".txt"]',
                'a[download]',
                'button:has-text("下载")',
                'button:has-text("导出")', 
                'button:has-text("保存")',
                'button:has-text("复制")',
                '.download-link',
                '.export-button',
                '.save-button',
                '.copy-button'
            ]
            
            download_attempted = False
            
            for selector in download_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            try:
                                # 设置下载处理
                                async with self.page.expect_download(timeout=10000) as download_info:
                                    await element.click()
                                
                                download = await download_info.value
                                
                                # 保存文件
                                filename = download.suggested_filename or f"skywork_file_{len(downloaded_files)}.bin"
                                file_path = download_dir / filename
                                
                                await download.save_as(file_path)
                                downloaded_files.append(file_path)
                                download_attempted = True
                                
                                self.logger.info(f"下载文件: {filename}")
                                
                            except Exception as download_error:
                                self.logger.warning(f"下载文件失败: {download_error}")
                                continue
                            
                except Exception as e:
                    continue
            
            # 无论是否有文件下载，都保存页面内容作为中间产物
            self.logger.info("保存页面内容作为中间产物...")
            
            try:
                # 1. 保存页面截图（全页面）
                screenshot_path = download_dir / f"skywork_screenshot_{task_id}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                downloaded_files.append(screenshot_path)
                self.logger.info(f"保存截图: {screenshot_path.name}")
            except Exception as e:
                self.logger.warning(f"保存截图失败: {e}")
            
            try:
                # 2. 保存页面HTML
                html_path = download_dir / f"skywork_page_{task_id}.html"
                content = await self.page.content()
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                downloaded_files.append(html_path)
                self.logger.info(f"保存HTML: {html_path.name}")
            except Exception as e:
                self.logger.warning(f"保存HTML失败: {e}")
            
            try:
                # 3. 保存结果文本
                result = await self.get_task_result(task_id)
                if result.result and len(result.result.strip()) > 10:
                    text_path = download_dir / f"skywork_result_{task_id}.txt"
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(f"任务ID: {task_id}\n")
                        f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"页面URL: {result.metadata.get('page_url', 'Unknown')}\n")
                        f.write(f"页面标题: {result.metadata.get('page_title', 'Unknown')}\n")
                        f.write(f"内容长度: {len(result.result)}\n")
                        f.write("="*50 + "\n\n")
                        f.write(result.result)
                    downloaded_files.append(text_path)
                    self.logger.info(f"保存文本结果: {text_path.name}")
            except Exception as e:
                self.logger.warning(f"保存文本结果失败: {e}")
            
            try:
                # 4. 保存元数据
                metadata_path = download_dir / f"skywork_metadata_{task_id}.json"
                metadata = {
                    "task_id": task_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "page_url": self.page.url,
                    "page_title": await self.page.title(),
                    "files_downloaded": len(downloaded_files),
                    "download_attempted": download_attempted,
                    "result_length": len(result.result) if 'result' in locals() else 0
                }
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                downloaded_files.append(metadata_path)
                self.logger.info(f"保存元数据: {metadata_path.name}")
            except Exception as e:
                self.logger.warning(f"保存元数据失败: {e}")
            
            self.logger.info(f"总共保存了 {len(downloaded_files)} 个文件")
            
        except Exception as e:
            self.logger.error(f"下载文件过程出错: {e}")
            # 即使出错也尝试保存基本信息
            try:
                error_log_path = download_dir / f"skywork_error_{task_id}.txt"
                with open(error_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"任务ID: {task_id}\n")
                    f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"错误信息: {e}\n")
                downloaded_files.append(error_log_path)
            except:
                pass
        
        return downloaded_files
    
    async def execute_full_task(
        self,
        topic: str,
        title: Optional[str] = None,
        download_dir: Optional[Path] = None,
        **kwargs
    ) -> TaskResult:
        """
        执行完整任务流程：提交->监控->获取结果->下载文件
        增强版：即使中断也会尝试获取中间结果
        """
        task_id = None
        result = None
        
        try:
            # 提交任务
            task_id = await self.submit_task(topic, title, **kwargs)
            self.logger.info(f"任务已提交: {task_id}")
            
            # 监控任务状态
            import asyncio
            max_iterations = 180  # 最多监控30分钟（每10秒检查一次）
            iteration = 0
            
            while iteration < max_iterations:
                try:
                    status = await self.get_task_status(task_id)
                    self.logger.info(f"任务状态: {status} (第{iteration+1}次检查)")
                    
                    if status == "completed":
                        self.logger.info("任务已完成")
                        break
                    elif status == "failed":
                        self.logger.warning("任务失败，但将尝试获取中间结果")
                        break
                    elif status in ["pending", "running"]:
                        await asyncio.sleep(10)  # 等待10秒后再检查
                        iteration += 1
                    else:
                        self.logger.warning(f"未知任务状态: {status}")
                        await asyncio.sleep(10)
                        iteration += 1
                        
                except Exception as status_error:
                    self.logger.warning(f"状态检查出错: {status_error}")
                    await asyncio.sleep(10)
                    iteration += 1
            
            if iteration >= max_iterations:
                self.logger.warning("任务监控超时，但将尝试获取当前结果")
            
        except KeyboardInterrupt:
            self.logger.warning("任务被用户中断，正在尝试获取中间结果...")
        except Exception as e:
            self.logger.error(f"任务执行出错: {e}，但将尝试获取中间结果")
        
        # 无论任务是否完成，都尝试获取结果
        try:
            if not task_id:
                task_id = f"skywork_interrupted_{int(time.time())}"
            
            result = await self.get_task_result(task_id)
            self.logger.info(f"获取到结果，长度: {len(result.result)}")
            
        except Exception as e:
            self.logger.error(f"获取结果失败: {e}")
            result = TaskResult(
                platform="skywork",
                task_id=task_id or f"skywork_error_{int(time.time())}",
                success=False,
                result=f"获取结果失败: {e}",
                metadata={"error": str(e)}
            )
        
        # 下载文件和保存中间产物
        if download_dir and result:
            try:
                downloaded_files = await self.download_files(task_id, download_dir)
                result.files = downloaded_files
                self.logger.info(f"已保存 {len(downloaded_files)} 个文件到 {download_dir}")
            except Exception as e:
                self.logger.error(f"文件保存失败: {e}")
        
        return result
    
    async def close(self):
        """关闭连接"""
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            self.browser = None
            self.context = None
            self.page = None
            
        except Exception as e:
            self.logger.error(f"关闭连接失败: {e}")
    
    def __del__(self):
        """析构函数"""
        try:
            if self.playwright:
                import asyncio
                asyncio.create_task(self.close())
        except:
            pass 