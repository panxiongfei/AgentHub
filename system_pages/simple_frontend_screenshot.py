#!/usr/bin/env python3
"""
AgentHub 简化前端截图工具
直接尝试访问前端页面并截图
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def take_frontend_screenshot():
    """截取前端页面"""
    print("🚀 启动前端页面截图...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-web-security']
        )
        
        # 创建页面
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            print("📸 尝试访问 http://localhost:3001 ...")
            
            # 尝试访问页面
            response = await page.goto("http://localhost:3001", 
                                       wait_until='networkidle', 
                                       timeout=15000)
            
            if response:
                print(f"✅ 页面响应状态: {response.status}")
                
                # 等待页面加载
                await asyncio.sleep(3)
                
                # 尝试等待基本元素
                try:
                    await page.wait_for_selector('body', timeout=5000)
                    print("✅ 页面body元素已加载")
                except:
                    print("⚠️  body元素加载超时，继续截图")
                
                # 截图
                screenshot_path = Path("05-frontend-main.png")
                await page.screenshot(
                    path=str(screenshot_path),
                    full_page=True,
                    type='png'
                )
                
                print(f"✅ 截图成功: {screenshot_path.absolute()}")
                
                # 获取页面标题
                title = await page.title()
                print(f"📄 页面标题: {title}")
                
                # 获取页面内容摘要
                content = await page.content()
                print(f"📝 页面内容长度: {len(content)} 字符")
                
            else:
                print("❌ 无法获取页面响应")
                
        except Exception as e:
            print(f"❌ 访问页面失败: {e}")
            
            # 尝试截图当前状态
            try:
                error_screenshot_path = Path("05-frontend-error.png")
                await page.screenshot(
                    path=str(error_screenshot_path),
                    full_page=True,
                    type='png'
                )
                print(f"📸 错误状态截图: {error_screenshot_path.absolute()}")
            except:
                print("❌ 错误状态截图也失败")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(take_frontend_screenshot()) 