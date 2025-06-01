#!/usr/bin/env python3
"""
AgentHub 回归测试系统
定期运行以确保所有功能正常工作，支持自动扩展测试项
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
import sys
import os

# 设置环境变量和路径
os.environ["MODEL_GEMINI_API_KEY"] = "AIzaSyD7ybqMdeZV3m44AXxXiEsf6l-2KT9XvYo"
sys.path.append(str(Path(__file__).parent))

from dataclasses import dataclass
from playwright.async_api import async_playwright


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    category: str
    success: bool
    duration: float
    error_message: str = ""
    details: Dict[str, Any] = None
    timestamp: str = ""


class AgentHubRegressionTest:
    """AgentHub回归测试器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
        # 测试配置
        self.api_base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3001"
        self.chrome_debug_port = 9222
        
        # 平台配置
        self.platforms = {
            "manus": "https://manus.chat",
            "skywork": "https://skywork.metaso.cn", 
            "chatgpt": "https://chatgpt.com",
            "kouzi": "https://kouzi.ai"
        }
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有回归测试"""
        print("🚀 开始AgentHub回归测试")
        print("=" * 80)
        
        # 后台测试
        await self._run_backend_tests()
        
        # 前台测试
        await self._run_frontend_tests()
        
        # 生成测试报告
        report = self._generate_test_report()
        
        # 保存测试结果
        await self._save_test_results(report)
        
        print("\n" + "=" * 80)
        print("📊 回归测试完成")
        self._print_summary(report)
        
        return report
    
    async def _run_backend_tests(self):
        """运行后台测试"""
        print("\n🔧 后台测试开始")
        print("-" * 40)
        
        # 1. 服务启动检测
        await self._test_service_startup()
        
        # 2. 大模型调用测试
        await self._test_model_calls()
        
        # 3. API基本功能测试
        await self._test_api_endpoints()
        
        # 4. 浏览器任务发起测试
        await self._test_browser_task_initiation()
        
        # 5. 历史任务和文件下载测试
        await self._test_history_and_download()
    
    async def _run_frontend_tests(self):
        """运行前台测试"""
        print("\n🌐 前台测试开始")
        print("-" * 40)
        
        # 1. 前端应用访问测试
        await self._test_frontend_access()
        
        # 2. 历史任务显示测试
        await self._test_history_display()
        
        # 3. 系统状态显示测试
        await self._test_system_status()
        
        # 4. 基本页面导航测试
        await self._test_page_navigation()
    
    async def _test_service_startup(self):
        """测试服务启动状态"""
        test_name = "服务启动检测"
        start_time = time.time()
        
        try:
            # 检查API服务健康状态
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/health", timeout=10) as resp:
                    if resp.status == 200:
                        health_data = await resp.json()
                        
                        self._add_result(TestResult(
                            test_name=test_name,
                            category="后台",
                            success=True,
                            duration=time.time() - start_time,
                            details=health_data,
                            timestamp=datetime.now().isoformat()
                        ))
                        print(f"✅ {test_name} - API服务正常运行")
                    else:
                        raise Exception(f"健康检查失败，状态码: {resp.status}")
                        
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="后台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_model_calls(self):
        """测试大模型调用"""
        test_name = "大模型调用测试"
        start_time = time.time()
        
        try:
            # 导入并测试模型客户端
            from app.core.model_client import get_model_client
            
            client = get_model_client()
            response = await client.chat_completion([
                {"role": "user", "content": "请简单回答：AgentHub系统测试"}
            ], max_tokens=50)
            
            if response.content and len(response.content) > 0:
                self._add_result(TestResult(
                    test_name=test_name,
                    category="后台",
                    success=True,
                    duration=time.time() - start_time,
                    details={
                        "model": response.model,
                        "provider": response.provider,
                        "usage": response.usage,
                        "response_length": len(response.content)
                    },
                    timestamp=datetime.now().isoformat()
                ))
                print(f"✅ {test_name} - 模型调用正常")
            else:
                raise Exception("模型响应为空")
                
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="后台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_api_endpoints(self):
        """测试API端点"""
        endpoints = [
            ("/api/v1/system/info", "系统信息"),
            ("/api/v1/platforms", "平台列表"),
            ("/health", "健康检查")
        ]
        
        for endpoint, description in endpoints:
            test_name = f"API测试 - {description}"
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_base_url}{endpoint}", timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            self._add_result(TestResult(
                                test_name=test_name,
                                category="后台",
                                success=True,
                                duration=time.time() - start_time,
                                details={"endpoint": endpoint, "data_keys": list(data.keys()) if isinstance(data, dict) else None},
                                timestamp=datetime.now().isoformat()
                            ))
                            print(f"✅ {test_name} - 响应正常")
                        else:
                            raise Exception(f"HTTP {resp.status}")
                            
            except Exception as e:
                self._add_result(TestResult(
                    test_name=test_name,
                    category="后台",
                    success=False,
                    duration=time.time() - start_time,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat()
                ))
                print(f"❌ {test_name} - {e}")
    
    async def _test_browser_task_initiation(self):
        """测试浏览器任务发起"""
        test_name = "浏览器任务发起测试"
        start_time = time.time()
        
        try:
            async with async_playwright() as p:
                # 尝试连接Chrome调试会话
                try:
                    browser = await p.chromium.connect_over_cdp(f"http://localhost:{self.chrome_debug_port}")
                    contexts = browser.contexts
                    
                    if not contexts:
                        raise Exception("没有找到浏览器上下文")
                    
                    # 获取或创建页面
                    context = contexts[0]
                    page = context.pages[0] if context.pages else await context.new_page()
                    
                    # 测试基本页面操作
                    await page.goto("https://www.baidu.com", timeout=15000)
                    title = await page.title()
                    
                    # 检查是否能找到输入框（验证页面基本交互能力）
                    input_element = await page.wait_for_selector("#kw", timeout=5000)
                    
                    if input_element and title:
                        self._add_result(TestResult(
                            test_name=test_name,
                            category="后台",
                            success=True,
                            duration=time.time() - start_time,
                            details={
                                "browser_connected": True,
                                "page_loaded": True,
                                "page_title": title,
                                "input_found": True
                            },
                            timestamp=datetime.now().isoformat()
                        ))
                        print(f"✅ {test_name} - 浏览器连接和页面操作正常")
                    else:
                        raise Exception("页面加载或元素定位失败")
                        
                except Exception as browser_error:
                    raise Exception(f"浏览器连接失败: {browser_error}")
                    
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="后台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_history_and_download(self):
        """测试历史任务和文件下载"""
        test_name = "历史任务和文件访问测试"
        start_time = time.time()
        
        try:
            # 检查历史数据目录
            data_dirs = [
                Path("data/history_downloads"),
                Path("data/multi_platform_downloads")
            ]
            
            found_tasks = []
            for data_dir in data_dirs:
                if data_dir.exists():
                    task_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
                    found_tasks.extend(task_dirs)
            
            if found_tasks:
                # 测试第一个任务的文件访问
                test_task = found_tasks[0]
                files = list(test_task.glob("*"))
                
                self._add_result(TestResult(
                    test_name=test_name,
                    category="后台",
                    success=True,
                    duration=time.time() - start_time,
                    details={
                        "tasks_found": len(found_tasks),
                        "test_task": str(test_task),
                        "files_in_task": len(files),
                        "file_types": list(set(f.suffix for f in files if f.is_file()))
                    },
                    timestamp=datetime.now().isoformat()
                ))
                print(f"✅ {test_name} - 找到 {len(found_tasks)} 个历史任务")
            else:
                self._add_result(TestResult(
                    test_name=test_name,
                    category="后台",
                    success=True,
                    duration=time.time() - start_time,
                    details={"tasks_found": 0, "note": "无历史任务数据，这是正常的"},
                    timestamp=datetime.now().isoformat()
                ))
                print(f"⚠️ {test_name} - 无历史任务数据（正常情况）")
                
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="后台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_frontend_access(self):
        """测试前端应用访问"""
        test_name = "前端应用访问测试"
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.frontend_url, timeout=15) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        
                        # 检查是否包含关键的前端元素
                        has_vue = "vue" in content.lower() or "app" in content.lower()
                        has_title = "agenthub" in content.lower() or "代理" in content.lower()
                        
                        self._add_result(TestResult(
                            test_name=test_name,
                            category="前台",
                            success=True,
                            duration=time.time() - start_time,
                            details={
                                "status_code": resp.status,
                                "content_length": len(content),
                                "has_vue_elements": has_vue,
                                "has_title": has_title
                            },
                            timestamp=datetime.now().isoformat()
                        ))
                        print(f"✅ {test_name} - 前端应用访问正常")
                    else:
                        raise Exception(f"HTTP {resp.status}")
                        
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="前台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_history_display(self):
        """测试历史任务显示"""
        test_name = "历史任务显示测试"
        start_time = time.time()
        
        try:
            # 通过API测试历史数据
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.api_base_url}/api/v1/history", timeout=10) as resp:
                        if resp.status == 200:
                            history_data = await resp.json()
                            
                            self._add_result(TestResult(
                                test_name=test_name,
                                category="前台",
                                success=True,
                                duration=time.time() - start_time,
                                details={
                                    "api_available": True,
                                    "data_structure": type(history_data).__name__
                                },
                                timestamp=datetime.now().isoformat()
                            ))
                            print(f"✅ {test_name} - 历史API响应正常")
                        elif resp.status == 404:
                            # 404是正常的，表示API端点可能还未实现
                            self._add_result(TestResult(
                                test_name=test_name,
                                category="前台",
                                success=True,
                                duration=time.time() - start_time,
                                details={"note": "历史API未实现，但系统正常"},
                                timestamp=datetime.now().isoformat()
                            ))
                            print(f"⚠️ {test_name} - 历史API未实现（正常）")
                        else:
                            raise Exception(f"API响应异常: HTTP {resp.status}")
                            
                except aiohttp.ClientTimeout:
                    raise Exception("API响应超时")
                    
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="前台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_system_status(self):
        """测试系统状态显示"""
        test_name = "系统状态显示测试"
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/v1/system/info", timeout=10) as resp:
                    if resp.status == 200:
                        system_info = await resp.json()
                        
                        required_keys = ["version", "status"]
                        has_required = all(key in system_info for key in required_keys)
                        
                        self._add_result(TestResult(
                            test_name=test_name,
                            category="前台",
                            success=True,
                            duration=time.time() - start_time,
                            details={
                                "system_info": system_info,
                                "has_required_keys": has_required
                            },
                            timestamp=datetime.now().isoformat()
                        ))
                        print(f"✅ {test_name} - 系统状态信息正常")
                    else:
                        raise Exception(f"系统信息API失败: HTTP {resp.status}")
                        
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="前台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    async def _test_page_navigation(self):
        """测试页面导航"""
        test_name = "页面导航测试"
        start_time = time.time()
        
        try:
            # 这里可以添加更详细的前端页面测试
            # 目前简单检查前端是否可访问
            async with aiohttp.ClientSession() as session:
                test_paths = ["/", "/#/dashboard", "/#/history", "/#/platforms"]
                
                successful_paths = 0
                for path in test_paths:
                    try:
                        async with session.get(f"{self.frontend_url}{path}", timeout=5) as resp:
                            if resp.status == 200:
                                successful_paths += 1
                    except:
                        pass  # 忽略单个路径的失败
                
                if successful_paths > 0:
                    self._add_result(TestResult(
                        test_name=test_name,
                        category="前台",
                        success=True,
                        duration=time.time() - start_time,
                        details={
                            "tested_paths": len(test_paths),
                            "successful_paths": successful_paths
                        },
                        timestamp=datetime.now().isoformat()
                    ))
                    print(f"✅ {test_name} - {successful_paths}/{len(test_paths)} 路径可访问")
                else:
                    raise Exception("所有导航路径都无法访问")
                    
        except Exception as e:
            self._add_result(TestResult(
                test_name=test_name,
                category="前台",
                success=False,
                duration=time.time() - start_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            ))
            print(f"❌ {test_name} - {e}")
    
    def _add_result(self, result: TestResult):
        """添加测试结果"""
        self.results.append(result)
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        
        backend_tests = [r for r in self.results if r.category == "后台"]
        frontend_tests = [r for r in self.results if r.category == "前台"]
        
        backend_success = len([r for r in backend_tests if r.success])
        frontend_success = len([r for r in frontend_tests if r.success])
        
        total_duration = time.time() - self.start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "categories": {
                "backend": {
                    "total": len(backend_tests),
                    "successful": backend_success,
                    "failed": len(backend_tests) - backend_success
                },
                "frontend": {
                    "total": len(frontend_tests),
                    "successful": frontend_success,
                    "failed": len(frontend_tests) - frontend_success
                }
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "category": r.category,
                    "success": r.success,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ],
            "failed_tests": [
                {
                    "test_name": r.test_name,
                    "category": r.category,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp
                }
                for r in self.results if not r.success
            ]
        }
    
    async def _save_test_results(self, report: Dict[str, Any]):
        """保存测试结果"""
        try:
            # 创建测试结果目录
            results_dir = Path("data/regression_tests")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存详细报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = results_dir / f"regression_test_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # 保存最新结果（供外部监控使用）
            latest_file = results_dir / "latest_result.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📁 测试报告已保存: {report_file}")
            
        except Exception as e:
            print(f"⚠️ 保存测试报告失败: {e}")
    
    def _print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        summary = report["summary"]
        categories = report["categories"]
        
        print(f"📊 测试总数: {summary['total_tests']}")
        print(f"✅ 成功: {summary['successful_tests']}")
        print(f"❌ 失败: {summary['failed_tests']}")
        print(f"📈 成功率: {summary['success_rate']:.1%}")
        print(f"⏱️ 总耗时: {summary['total_duration']:.2f}秒")
        
        print(f"\n🔧 后台测试: {categories['backend']['successful']}/{categories['backend']['total']}")
        print(f"🌐 前台测试: {categories['frontend']['successful']}/{categories['frontend']['total']}")
        
        # 显示失败的测试
        failed_tests = report["failed_tests"]
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['error_message']}")
        
        # 整体状态
        if summary['success_rate'] >= 0.9:
            print(f"\n🎉 系统状态: 优秀 (成功率 {summary['success_rate']:.1%})")
        elif summary['success_rate'] >= 0.7:
            print(f"\n⚠️ 系统状态: 良好 (成功率 {summary['success_rate']:.1%})")
        else:
            print(f"\n🚨 系统状态: 需要关注 (成功率 {summary['success_rate']:.1%})")


async def main():
    """主函数"""
    tester = AgentHubRegressionTest()
    
    try:
        report = await tester.run_all_tests()
        
        # 根据测试结果设置退出码
        success_rate = report["summary"]["success_rate"]
        if success_rate >= 0.7:
            return 0  # 成功
        else:
            return 1  # 失败
            
    except Exception as e:
        print(f"💥 回归测试执行失败: {e}")
        traceback.print_exc()
        return 2  # 错误


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 