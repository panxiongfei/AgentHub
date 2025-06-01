#!/usr/bin/env python3
"""
Skywork平台自动导航脚本
"""

import asyncio
from playwright.async_api import async_playwright

async def navigate_to_skywork():
    """自动导航到Skywork平台"""
    async with async_playwright() as p:
        try:
            # 连接到现有的Chrome调试会话
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # 获取或创建新的页面
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
            
            # 打开Skywork主页
            print("🚀 正在打开Skywork平台...")
            await page.goto("https://skywork.ai", wait_until="networkidle")
            
            print(f"✅ 已打开Skywork平台: {page.url}")
            print("📝 请手动登录并导航到历史记录页面")
            print("💡 登录完成后，运行以下命令：")
            print("   python main.py download-history --platform skywork --debug-port 9222")
            
        except Exception as e:
            print(f"❌ 导航失败: {e}")

if __name__ == "__main__":
    asyncio.run(navigate_to_skywork()) 