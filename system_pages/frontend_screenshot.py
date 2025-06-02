#!/usr/bin/env python3
"""
AgentHub 前端页面截图工具
专门截取前端界面页面
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# 前端页面配置
FRONTEND_PAGES = [
    {
        "name": "05-frontend-home",
        "url": "http://localhost:3001/",
        "title": "前端首页",
        "wait_time": 5,
        "wait_selector": "body"
    },
    {
        "name": "06-frontend-dashboard", 
        "url": "http://localhost:3001/dashboard",
        "title": "仪表盘页面",
        "wait_time": 5,
        "wait_selector": "body"
    },
    {
        "name": "07-frontend-history",
        "url": "http://localhost:3001/history",
        "title": "历史任务页面", 
        "wait_time": 5,
        "wait_selector": "body"
    },
    {
        "name": "08-frontend-platforms",
        "url": "http://localhost:3001/platforms",
        "title": "平台管理页面",
        "wait_time": 5,
        "wait_selector": "body"
    }
]

async def check_url_accessible(page, url: str) -> bool:
    """检查URL是否可访问"""
    try:
        response = await page.goto(url, wait_until='domcontentloaded', timeout=10000)
        return response and response.status < 400
    except Exception as e:
        print(f"检查URL失败: {e}")
        return False

async def take_frontend_screenshot(page_config: dict, page, output_dir: Path):
    """截取前端页面"""
    try:
        print(f"📸 正在截取: {page_config['title']} ({page_config['url']})")
        
        # 检查URL是否可访问
        if not await check_url_accessible(page, page_config['url']):
            print(f"⚠️  URL不可访问，跳过: {page_config['url']}")
            return False
        
        # 等待页面加载
        await asyncio.sleep(page_config['wait_time'])
        
        # 等待body元素加载
        try:
            await page.wait_for_selector(page_config['wait_selector'], timeout=8000)
            print(f"✅ 页面元素已加载: {page_config['wait_selector']}")
        except:
            print(f"⚠️  页面元素加载超时，继续截图: {page_config['wait_selector']}")
        
        # 额外等待
        await asyncio.sleep(2)
        
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
    
    print("🚀 AgentHub 前端页面截图工具")
    print("=" * 50)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,  # 无头模式
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
        )
        
        # 创建页面
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 先检查前端服务状态
        print("🔍 检查前端服务状态...")
        frontend_accessible = await check_url_accessible(page, "http://localhost:3001/")
        print(f"   前端服务: {'✅ 可访问' if frontend_accessible else '❌ 不可访问'}")
        print()
        
        if not frontend_accessible:
            print("❌ 前端服务不可访问，请确保服务正在运行")
            await browser.close()
            return
        
        # 截取所有前端页面
        success_count = 0
        for page_config in FRONTEND_PAGES:
            if await take_frontend_screenshot(page_config, page, output_dir):
                success_count += 1
            
            # 页面间等待
            await asyncio.sleep(1)
        
        await browser.close()
        
        print("\n" + "=" * 50)
        print(f"🎉 前端截图完成! 成功: {success_count}/{len(FRONTEND_PAGES)}")
        print(f"📁 截图保存位置: {output_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(main()) 