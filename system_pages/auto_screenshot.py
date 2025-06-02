#!/usr/bin/env python3
"""
AgentHub 系统页面自动截图工具
用于生成系统重要页面的截图，便于展示和文档记录
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

# 页面配置
PAGES_CONFIG = [
    {
        "name": "dashboard",
        "url": "http://localhost:3001/",
        "title": "仪表盘主页",
        "wait_selector": ".el-container",
        "wait_time": 3
    },
    {
        "name": "history",
        "url": "http://localhost:3001/history",
        "title": "历史任务",
        "wait_selector": ".el-table",
        "wait_time": 4
    },
    {
        "name": "platforms",
        "url": "http://localhost:3001/platforms",
        "title": "平台管理",
        "wait_selector": ".platform-card",
        "wait_time": 3
    },
    {
        "name": "browser-management",
        "url": "http://localhost:3001/system/browser",
        "title": "浏览器管理",
        "wait_selector": ".browser-config-card",
        "wait_time": 3
    },
    {
        "name": "system-status",
        "url": "http://localhost:3001/system",
        "title": "系统状态",
        "wait_selector": ".system-info",
        "wait_time": 3
    }
]

async def take_screenshot(page_config: dict, page, output_dir: Path):
    """截取单个页面"""
    try:
        print(f"📸 正在截取: {page_config['title']} ({page_config['url']})")
        
        # 导航到页面
        await page.goto(page_config['url'], wait_until='networkidle')
        
        # 等待关键元素加载
        try:
            await page.wait_for_selector(page_config['wait_selector'], timeout=10000)
            print(f"✅ 关键元素已加载: {page_config['wait_selector']}")
        except:
            print(f"⚠️  关键元素加载超时，继续截图: {page_config['wait_selector']}")
        
        # 额外等待时间
        await asyncio.sleep(page_config['wait_time'])
        
        # 截图
        screenshot_path = output_dir / f"{page_config['name']}.png"
        await page.screenshot(
            path=str(screenshot_path),
            full_page=True,
            type='png'
        )
        
        print(f"✅ 截图成功: {screenshot_path}")
        return True
        
    except Exception as e:
        print(f"❌ 截图失败 {page_config['name']}: {e}")
        return False

async def main():
    """主函数"""
    output_dir = Path(".")
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 AgentHub 系统页面自动截图工具")
    print("=" * 50)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口以便观察
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # 创建页面
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 截取所有页面
        success_count = 0
        for page_config in PAGES_CONFIG:
            if await take_screenshot(page_config, page, output_dir):
                success_count += 1
            
            # 页面间等待
            await asyncio.sleep(2)
        
        await browser.close()
        
        print("\n" + "=" * 50)
        print(f"🎉 截图完成! 成功: {success_count}/{len(PAGES_CONFIG)}")
        print(f"📁 截图保存位置: {output_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main()) 