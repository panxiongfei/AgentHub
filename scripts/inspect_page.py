#!/usr/bin/env python3
"""
页面检查脚本
用于诊断网页元素和查找历史任务相关的内容
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def inspect_skywork_page(debug_port=9222):
    """检查Skywork页面的详细结构"""
    
    try:
        playwright = await async_playwright().start()
        
        # 连接到现有的Chrome实例
        browser = await playwright.chromium.connect_over_cdp(
            f"http://localhost:{debug_port}"
        )
        
        # 获取上下文和页面
        contexts = browser.contexts
        if not contexts:
            print("❌ 没有找到浏览器上下文")
            return
        
        context = contexts[0]
        pages = context.pages
        
        # 查找Skywork页面
        skywork_page = None
        for page in pages:
            if "skywork.ai" in page.url.lower():
                skywork_page = page
                break
        
        if not skywork_page:
            print("❌ 没有找到Skywork页面")
            return
        
        print(f"🔍 检查页面: {skywork_page.url}")
        print(f"📄 页面标题: {await skywork_page.title()}")
        
        # 检查侧边栏结构
        print("\n🔍 检查侧边栏结构:")
        sidebar_selectors = [
            ".sidebar",
            ".history-panel", 
            ".left-panel",
            ".conversation-list",
            ".chat-history",
            "[data-testid='sidebar']",
            ".nav-left",
            ".side-nav"
        ]
        
        for selector in sidebar_selectors:
            try:
                elements = await skywork_page.locator(selector).all()
                if elements:
                    for i, element in enumerate(elements):
                        if await element.is_visible():
                            text = await element.text_content()
                            print(f"  ✅ {selector} [{i}]: 可见, 文本长度: {len(text) if text else 0}")
                            if text and len(text) < 200:
                                print(f"     文本预览: {text[:100]}...")
                        else:
                            print(f"  ⚪ {selector} [{i}]: 不可见")
            except Exception as e:
                print(f"  ❌ {selector}: 错误 - {e}")
        
        # 检查可能的历史任务项
        print("\n🔍 检查可能的历史任务项:")
        task_selectors = [
            ".conversation-item",
            ".chat-item", 
            ".history-item",
            ".task-item",
            ".conversation",
            "[data-conversation-id]",
            "a[href*='/chat/']",
            "a[href*='/conversation/']",
            ".list-item",
            "li",
            ".menu-item"
        ]
        
        for selector in task_selectors:
            try:
                elements = await skywork_page.locator(selector).all()
                visible_count = 0
                total_count = len(elements)
                
                for element in elements:
                    if await element.is_visible():
                        visible_count += 1
                
                if visible_count > 0:
                    print(f"  ✅ {selector}: 总共 {total_count} 个, 可见 {visible_count} 个")
                    
                    # 显示前几个元素的内容
                    for i, element in enumerate(elements[:3]):
                        if await element.is_visible():
                            text = await element.text_content()
                            href = await element.get_attribute("href")
                            print(f"     [{i}] 文本: {text[:50] if text else 'N/A'}...")
                            if href:
                                print(f"         链接: {href}")
                
            except Exception as e:
                print(f"  ❌ {selector}: 错误 - {e}")
        
        # 检查所有链接
        print("\n🔍 检查所有链接:")
        try:
            links = await skywork_page.locator("a").all()
            print(f"总共找到 {len(links)} 个链接")
            
            history_related_links = []
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    
                    if href and any(keyword in href.lower() for keyword in ["history", "chat", "conversation", "past", "previous"]):
                        history_related_links.append((href, text))
                    elif text and any(keyword in text.lower() for keyword in ["历史", "对话", "聊天", "过往", "之前"]):
                        history_related_links.append((href, text))
                except:
                    continue
            
            if history_related_links:
                print("找到与历史相关的链接:")
                for href, text in history_related_links[:10]:
                    print(f"  - {text[:30]}... -> {href}")
            else:
                print("未找到与历史相关的链接")
                
        except Exception as e:
            print(f"检查链接时出错: {e}")
        
        # 检查页面结构
        print("\n🔍 页面整体结构:")
        try:
            # 获取主要容器
            main_containers = [
                "main",
                ".main",
                ".container", 
                ".app",
                "#app",
                ".layout",
                "body > div"
            ]
            
            for selector in main_containers:
                try:
                    elements = await skywork_page.locator(selector).all()
                    for i, element in enumerate(elements):
                        if await element.is_visible():
                            # 获取子元素信息
                            child_count = await element.evaluate("el => el.children.length")
                            print(f"  ✅ {selector} [{i}]: {child_count} 个子元素")
                except:
                    continue
                    
        except Exception as e:
            print(f"检查页面结构时出错: {e}")
        
        # 检查特定的Skywork元素
        print("\n🔍 检查Skywork特有元素:")
        skywork_selectors = [
            '[class*="skywork"]',
            '[class*="conversation"]', 
            '[class*="chat"]',
            '[class*="history"]',
            '[id*="chat"]',
            '[id*="conversation"]',
            '[data-*="chat"]',
            '[data-*="conversation"]'
        ]
        
        for selector in skywork_selectors:
            try:
                elements = await skywork_page.locator(selector).all()
                if elements:
                    visible_elements = []
                    for element in elements:
                        if await element.is_visible():
                            visible_elements.append(element)
                    
                    if visible_elements:
                        print(f"  ✅ {selector}: {len(visible_elements)} 个可见元素")
                        
                        # 显示第一个元素的详细信息
                        first_element = visible_elements[0]
                        text = await first_element.text_content()
                        attrs = await first_element.evaluate("""
                            el => Array.from(el.attributes).map(attr => `${attr.name}="${attr.value}"`).join(' ')
                        """)
                        print(f"     属性: {attrs}")
                        print(f"     文本: {text[:100] if text else 'N/A'}...")
                        
            except Exception as e:
                print(f"  ❌ {selector}: 错误 - {e}")
        
        await playwright.stop()
        
    except Exception as e:
        print(f"❌ 页面检查失败: {e}")


if __name__ == "__main__":
    print("🔍 开始检查Skywork页面...")
    asyncio.run(inspect_skywork_page()) 