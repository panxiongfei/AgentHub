#!/usr/bin/env python3
"""
Skywork平台登录辅助脚本
自动打开Skywork登录页面，等待用户手动登录后继续
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def open_skywork_login():
    """打开Skywork登录页面并等待用户登录"""
    print("🚀 正在打开Skywork平台登录页面...")
    
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
            skywork_url = "https://skywork.ai"
            print(f"📱 正在打开: {skywork_url}")
            await page.goto(skywork_url, wait_until="networkidle")
            
            print("\n" + "="*60)
            print("🔑 请在浏览器中手动完成以下步骤：")
            print("1. 点击登录按钮")
            print("2. 输入您的用户名和密码")
            print("3. 完成登录流程")
            print("4. 确保您能看到主界面或历史记录页面")
            print("="*60)
            
            # 等待用户登录
            print("\n⏳ 等待登录完成...")
            print("请在完成登录后按 Enter 键继续...")
            input()
            
            # 检查登录状态
            current_url = page.url
            print(f"✅ 当前页面: {current_url}")
            
            # 尝试导航到历史记录页面
            try:
                print("🔍 正在寻找历史记录页面...")
                
                # 尝试寻找历史记录链接或按钮
                history_selectors = [
                    'a[href*="history"]',
                    'a[href*="record"]',
                    'a[href*="chat"]',
                    '.history',
                    '.record',
                    '.sidebar a',
                    'nav a',
                    '[data-testid*="history"]'
                ]
                
                history_found = False
                for selector in history_selectors:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"📋 找到可能的历史记录元素: {len(elements)} 个")
                        for i, element in enumerate(elements[:3]):  # 检查前3个
                            try:
                                text = await element.text_content()
                                href = await element.get_attribute('href')
                                print(f"   {i+1}. 文本: '{text}' | 链接: {href}")
                                
                                if any(keyword in text.lower() for keyword in ['历史', 'history', '记录', 'record', '对话', 'chat']) if text else False:
                                    print(f"🎯 点击历史记录链接: {text}")
                                    await element.click()
                                    await page.wait_for_load_state("networkidle")
                                    history_found = True
                                    break
                            except Exception as e:
                                continue
                        
                        if history_found:
                            break
                
                if not history_found:
                    print("⚠️ 未找到明确的历史记录链接，请手动导航到历史记录页面")
                    print("请在浏览器中找到并点击历史记录页面，然后按 Enter 继续...")
                    input()
                
            except Exception as e:
                print(f"⚠️ 自动导航失败: {e}")
                print("请手动导航到历史记录页面，然后按 Enter 继续...")
                input()
            
            print("✅ 登录检查完成！")
            print("🔄 现在您可以运行历史任务下载命令了")
            
            # 保持浏览器打开
            print("\n💡 提示: 请保持浏览器窗口打开，现在可以运行下载命令：")
            print("python main.py download-history --platform skywork --debug-port 9222")
            
        except Exception as e:
            print(f"❌ 连接Chrome失败: {e}")
            print("请确保Chrome调试端口9222已经启动")

if __name__ == "__main__":
    asyncio.run(open_skywork_login()) 