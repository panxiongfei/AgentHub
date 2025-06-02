#!/usr/bin/env python3
"""
AgentHub 完整截图工具
包含API端点和前端界面截图
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

# 页面配置
PAGES_CONFIG = [
    # API端点截图
    {
        "name": "01-api-health",
        "url": "http://localhost:8000/health",
        "title": "API健康检查",
        "wait_time": 2,
        "type": "api"
    },
    {
        "name": "02-api-platforms",
        "url": "http://localhost:8000/api/v1/platforms",
        "title": "平台列表API",
        "wait_time": 2,
        "type": "api"
    },
    {
        "name": "03-api-system-info",
        "url": "http://localhost:8000/api/v1/system/info",
        "title": "系统信息API",
        "wait_time": 2,
        "type": "api"
    },
    {
        "name": "04-api-history",
        "url": "http://localhost:8000/api/v1/history",
        "title": "历史任务API",
        "wait_time": 2,
        "type": "api"
    },
    # 前端界面截图
    {
        "name": "05-frontend-dashboard",
        "url": "http://localhost:3001/",
        "title": "前端仪表盘",
        "wait_time": 5,
        "type": "frontend",
        "wait_selector": ".el-container"
    },
    {
        "name": "06-frontend-history",
        "url": "http://localhost:3001/history",
        "title": "历史任务页面",
        "wait_time": 5,
        "type": "frontend",
        "wait_selector": ".el-table"
    },
    {
        "name": "07-frontend-platforms",
        "url": "http://localhost:3001/platforms",
        "title": "平台管理页面",
        "wait_time": 5,
        "type": "frontend",
        "wait_selector": ".platform-card"
    },
    {
        "name": "08-frontend-system",
        "url": "http://localhost:3001/system",
        "title": "系统状态页面",
        "wait_time": 5,
        "type": "frontend",
        "wait_selector": ".system-info"
    }
]

async def check_url_accessible(page, url: str) -> bool:
    """检查URL是否可访问"""
    try:
        response = await page.goto(url, wait_until='domcontentloaded', timeout=5000)
        return response.status < 400
    except Exception:
        return False

async def take_screenshot(page_config: dict, page, output_dir: Path):
    """截取单个页面"""
    try:
        print(f"📸 正在截取: {page_config['title']} ({page_config['url']})")
        
        # 检查URL是否可访问
        if not await check_url_accessible(page, page_config['url']):
            print(f"⚠️  URL不可访问，跳过: {page_config['url']}")
            return False
        
        # 重新导航到页面
        await page.goto(page_config['url'], wait_until='networkidle', timeout=10000)
        
        # 等待特定元素加载（如果指定了）
        if 'wait_selector' in page_config:
            try:
                await page.wait_for_selector(page_config['wait_selector'], timeout=8000)
                print(f"✅ 元素已加载: {page_config['wait_selector']}")
            except:
                print(f"⚠️  元素加载超时，继续截图: {page_config['wait_selector']}")
        
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
    
    print("🚀 AgentHub 完整截图工具")
    print("=" * 60)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,  # 无头模式
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # 创建页面
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 先检查服务状态
        print("🔍 检查服务状态...")
        api_accessible = await check_url_accessible(page, "http://localhost:8000/health")
        frontend_accessible = await check_url_accessible(page, "http://localhost:3001/")
        
        print(f"   API服务: {'✅ 可访问' if api_accessible else '❌ 不可访问'}")
        print(f"   前端服务: {'✅ 可访问' if frontend_accessible else '❌ 不可访问'}")
        print()
        
        # 截取所有页面
        success_count = 0
        for page_config in PAGES_CONFIG:
            # 根据服务状态决定是否截图
            if page_config['type'] == 'api' and not api_accessible:
                print(f"⏭️  跳过API页面: {page_config['title']}")
                continue
            elif page_config['type'] == 'frontend' and not frontend_accessible:
                print(f"⏭️  跳过前端页面: {page_config['title']}")
                continue
                
            if await take_screenshot(page_config, page, output_dir):
                success_count += 1
            
            # 页面间等待
            await asyncio.sleep(1)
        
        await browser.close()
        
        print("\n" + "=" * 60)
        print(f"🎉 截图完成! 成功: {success_count}/{len(PAGES_CONFIG)}")
        print(f"📁 截图保存位置: {output_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main()) 