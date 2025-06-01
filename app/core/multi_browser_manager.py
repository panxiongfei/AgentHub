"""
多浏览器管理器
用于同时管理多个浏览器实例，实现多平台并发历史下载
"""

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.core.browser_engine import EnhancedBrowserEngine
from app.core.history_downloader import HistoryDownloader, DownloadResult
from app.core.logger import get_logger


@dataclass
class BrowserInstance:
    """浏览器实例信息"""
    platform: str
    port: int
    browser: Browser
    context: BrowserContext
    page: Page
    browser_engine: EnhancedBrowserEngine
    history_downloader: HistoryDownloader


@dataclass
class MultiPlatformDownloadResult:
    """多平台下载结果"""
    success: bool
    results: Dict[str, List[DownloadResult]]
    total_downloaded: int
    total_errors: int
    download_dir: Path
    duration: float
    error_message: str = ""


class MultiBrowserManager:
    """多浏览器管理器"""
    
    def __init__(self):
        self.logger = get_logger("multi_browser_manager")
        self.browsers: Dict[str, BrowserInstance] = {}
        self.playwright = None
        
    async def initialize_browsers(self, platform_configs: Dict[str, int]) -> bool:
        """
        初始化多个浏览器实例
        
        Args:
            platform_configs: 平台配置字典 {platform: debug_port}
        """
        try:
            self.playwright = await async_playwright().start()
            
            for platform, port in platform_configs.items():
                await self._initialize_browser_instance(platform, port)
                
            self.logger.info(f"成功初始化 {len(self.browsers)} 个浏览器实例")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化浏览器失败: {e}")
            await self.cleanup()
            return False
    
    async def _initialize_browser_instance(self, platform: str, port: int):
        """初始化单个浏览器实例"""
        try:
            # 连接到Chrome调试端点
            browser = await self.playwright.chromium.connect_over_cdp(
                f"http://localhost:{port}"
            )
            
            # 获取默认上下文和页面
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
                pages = context.pages
                if pages:
                    page = pages[0]
                else:
                    page = await context.new_page()
            else:
                context = await browser.new_context()
                page = await context.new_page()
            
            # 创建浏览器引擎和历史下载器
            browser_engine = EnhancedBrowserEngine(page)
            history_downloader = HistoryDownloader(platform, browser_engine)
            
            # 保存浏览器实例
            self.browsers[platform] = BrowserInstance(
                platform=platform,
                port=port,
                browser=browser,
                context=context,
                page=page,
                browser_engine=browser_engine,
                history_downloader=history_downloader
            )
            
            self.logger.info(f"浏览器实例初始化成功: {platform} (端口 {port})")
            
        except Exception as e:
            self.logger.error(f"初始化 {platform} 浏览器实例失败: {e}")
            raise
    
    async def download_all_histories(self, download_base_dir: Path) -> MultiPlatformDownloadResult:
        """
        并发下载所有平台的历史任务
        
        Args:
            download_base_dir: 下载根目录
        """
        start_time = time.time()
        
        try:
            self.logger.info("开始多平台并发历史下载...")
            
            # 创建下载目录
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            download_dir = download_base_dir / f"multi_platform_history_{timestamp}"
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # 并发执行各平台的历史下载
            download_tasks = []
            for platform, browser_instance in self.browsers.items():
                platform_download_dir = download_dir / platform
                platform_download_dir.mkdir(exist_ok=True)
                
                task = self._download_platform_history(
                    browser_instance, 
                    platform_download_dir
                )
                download_tasks.append(task)
            
            # 等待所有下载任务完成
            platform_results = await asyncio.gather(*download_tasks, return_exceptions=True)
            
            # 处理结果
            results = {}
            total_downloaded = 0
            total_errors = 0
            
            for i, (platform, browser_instance) in enumerate(self.browsers.items()):
                if isinstance(platform_results[i], Exception):
                    self.logger.error(f"平台 {platform} 下载失败: {platform_results[i]}")
                    results[platform] = []
                    total_errors += 1
                else:
                    download_results = platform_results[i]
                    results[platform] = download_results
                    
                    # 统计成功和失败的任务
                    for result in download_results:
                        if result.success:
                            total_downloaded += 1
                        else:
                            total_errors += 1
            
            # 生成总体报告
            await self._generate_multi_platform_report(results, download_dir)
            
            duration = time.time() - start_time
            
            return MultiPlatformDownloadResult(
                success=total_downloaded > 0,
                results=results,
                total_downloaded=total_downloaded,
                total_errors=total_errors,
                download_dir=download_dir,
                duration=duration
            )
            
        except Exception as e:
            self.logger.error(f"多平台历史下载失败: {e}")
            duration = time.time() - start_time
            
            return MultiPlatformDownloadResult(
                success=False,
                results={},
                total_downloaded=0,
                total_errors=len(self.browsers),
                download_dir=download_base_dir,
                duration=duration,
                error_message=str(e)
            )
    
    async def _download_platform_history(
        self, 
        browser_instance: BrowserInstance, 
        download_dir: Path
    ) -> List[DownloadResult]:
        """下载单个平台的历史任务"""
        try:
            self.logger.info(f"开始下载 {browser_instance.platform} 平台历史...")
            
            # 使用历史下载器进行下载
            results = await browser_instance.history_downloader.batch_download_all(download_dir)
            
            self.logger.info(
                f"{browser_instance.platform} 平台下载完成: "
                f"成功 {sum(1 for r in results if r.success)}, "
                f"失败 {sum(1 for r in results if not r.success)}"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"下载 {browser_instance.platform} 平台历史失败: {e}")
            return []
    
    async def _generate_multi_platform_report(
        self, 
        results: Dict[str, List[DownloadResult]], 
        download_dir: Path
    ):
        """生成多平台下载报告"""
        try:
            report = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "download_dir": str(download_dir),
                "platforms": {},
                "summary": {
                    "total_platforms": len(results),
                    "total_tasks": 0,
                    "total_successful": 0,
                    "total_failed": 0,
                    "success_rate": 0.0
                }
            }
            
            # 统计各平台结果
            for platform, platform_results in results.items():
                successful = sum(1 for r in platform_results if r.success)
                failed = sum(1 for r in platform_results if not r.success)
                
                report["platforms"][platform] = {
                    "total_tasks": len(platform_results),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": successful / len(platform_results) if platform_results else 0.0,
                    "tasks": [
                        {
                            "task_id": r.task.id,
                            "task_title": r.task.title,
                            "success": r.success,
                            "files_count": len(r.files),
                            "error": r.error if not r.success else None
                        }
                        for r in platform_results
                    ]
                }
                
                # 更新总体统计
                report["summary"]["total_tasks"] += len(platform_results)
                report["summary"]["total_successful"] += successful
                report["summary"]["total_failed"] += failed
            
            # 计算总体成功率
            if report["summary"]["total_tasks"] > 0:
                report["summary"]["success_rate"] = (
                    report["summary"]["total_successful"] / 
                    report["summary"]["total_tasks"]
                )
            
            # 保存报告
            report_file = download_dir / "multi_platform_download_report.json"
            import json
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"多平台下载报告已生成: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成多平台报告失败: {e}")
    
    async def get_browser_instance(self, platform: str) -> Optional[BrowserInstance]:
        """获取指定平台的浏览器实例"""
        return self.browsers.get(platform)
    
    async def list_all_histories(self) -> Dict[str, Any]:
        """列出所有平台的历史任务"""
        try:
            result = {}
            
            # 并发获取各平台的历史任务列表
            tasks = []
            for platform, browser_instance in self.browsers.items():
                task = browser_instance.history_downloader.discover_history_tasks()
                tasks.append((platform, task))
            
            # 等待所有任务完成
            for platform, task in tasks:
                try:
                    history_tasks = await task
                    result[platform] = {
                        "total_tasks": len(history_tasks),
                        "tasks": [
                            {
                                "id": t.id,
                                "title": t.title,
                                "date": t.date,
                                "preview": t.preview[:100] + "..." if len(t.preview) > 100 else t.preview
                            }
                            for t in history_tasks[:10]  # 只显示前10个
                        ]
                    }
                except Exception as e:
                    self.logger.error(f"获取 {platform} 历史任务失败: {e}")
                    result[platform] = {"error": str(e)}
            
            return result
            
        except Exception as e:
            self.logger.error(f"列出所有历史任务失败: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 关闭所有浏览器实例
            for platform, browser_instance in self.browsers.items():
                try:
                    await browser_instance.browser.close()
                    self.logger.info(f"已关闭 {platform} 浏览器实例")
                except Exception as e:
                    self.logger.warning(f"关闭 {platform} 浏览器实例失败: {e}")
            
            # 停止playwright
            if self.playwright:
                await self.playwright.stop()
            
            self.browsers.clear()
            self.logger.info("多浏览器管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}") 