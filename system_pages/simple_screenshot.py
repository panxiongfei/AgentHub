#!/usr/bin/env python3
"""
AgentHub 简化截图工具
直接使用浏览器截取API端点和静态页面
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

# 页面配置 - 只截取能确保正常的页面
PAGES_CONFIG = [
    {
        "name": "api-health",
        "url": "http://localhost:8000/health",
        "title": "API健康检查",
        "wait_time": 2
    },
    {
        "name": "api-platforms",
        "url": "http://localhost:8000/api/v1/platforms",
        "title": "平台列表API",
        "wait_time": 2
    },
    {
        "name": "api-system-info",
        "url": "http://localhost:8000/api/v1/system/info",
        "title": "系统信息API",
        "wait_time": 2
    },
    {
        "name": "api-history",
        "url": "http://localhost:8000/api/v1/history",
        "title": "历史任务API",
        "wait_time": 2
    }
]

async def take_screenshot(page_config: dict, page, output_dir: Path):
    """截取单个页面"""
    try:
        print(f"📸 正在截取: {page_config['title']} ({page_config['url']})")
        
        # 导航到页面
        await page.goto(page_config['url'], wait_until='networkidle')
        
        # 等待页面加载
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
    
    print("🚀 AgentHub 简化截图工具")
    print("=" * 50)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,  # 无头模式
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
            await asyncio.sleep(1)
        
        await browser.close()
        
        print("\n" + "=" * 50)
        print(f"🎉 截图完成! 成功: {success_count}/{len(PAGES_CONFIG)}")
        print(f"📁 截图保存位置: {output_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main()) 