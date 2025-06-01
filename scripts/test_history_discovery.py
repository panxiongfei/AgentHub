#!/usr/bin/env python3
"""
历史任务发现测试脚本
用于调试和测试历史任务发现功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright


async def test_history_discovery(debug_port=9222):
    """测试历史任务发现功能"""
    
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
        
        print(f"🔍 测试页面: {skywork_page.url}")
        
        # 1. 查找侧边栏
        print("\n🔍 步骤1: 查找侧边栏")
        sidebar_locator = skywork_page.locator(".sidebar")
        sidebar_count = await sidebar_locator.count()
        
        if sidebar_count == 0:
            print("❌ 未找到侧边栏")
            return
        
        print(f"✅ 找到侧边栏: {sidebar_count} 个")
        
        # 2. 分析侧边栏内容
        print("\n🔍 步骤2: 分析侧边栏内容")
        sidebar_text = await sidebar_locator.first.text_content()
        print(f"侧边栏文本长度: {len(sidebar_text)}")
        print(f"侧边栏文本预览: {sidebar_text[:200]}...")
        
        # 3. 查找任务项
        print("\n🔍 步骤3: 查找任务项")
        task_selectors = [
            ".sidebar li",
            ".sidebar .conversation-item",
            ".sidebar .chat-item",
            ".sidebar .history-item",
            ".sidebar .project-item"
        ]
        
        for selector in task_selectors:
            print(f"\n🔍 测试选择器: {selector}")
            try:
                items = await skywork_page.locator(selector).all()
                print(f"  总共找到: {len(items)} 个元素")
                
                if items:
                    visible_count = 0
                    for i, item in enumerate(items):
                        is_visible = await item.is_visible()
                        if is_visible:
                            visible_count += 1
                            
                        # 显示前3个元素的详细信息
                        if i < 3:
                            text = await item.text_content()
                            bbox = await item.bounding_box()
                            print(f"    [{i}] 可见: {is_visible}, 位置: {bbox}, 文本: {text[:50] if text else 'N/A'}...")
                    
                    print(f"  可见元素: {visible_count} 个")
                    
                    if visible_count > 0:
                        print(f"  ✅ 选择器 {selector} 找到 {visible_count} 个可见的潜在历史任务")
                else:
                    print(f"  ❌ 选择器 {selector} 没有找到元素")
                    
            except Exception as e:
                print(f"  ❌ 选择器 {selector} 出错: {e}")
        
        # 4. 尝试手动提取历史任务信息
        print("\n🔍 步骤4: 手动提取历史任务信息")
        try:
            # 直接在侧边栏中查找li元素
            li_elements = await skywork_page.locator(".sidebar li").all()
            print(f"侧边栏中的li元素总数: {len(li_elements)}")
            
            for i, li in enumerate(li_elements[:5]):  # 只处理前5个
                try:
                    is_visible = await li.is_visible()
                    text = await li.text_content()
                    bbox = await li.bounding_box()
                    
                    print(f"  li[{i}]:")
                    print(f"    可见: {is_visible}")
                    print(f"    位置: {bbox}")
                    print(f"    文本: {text[:100] if text else 'N/A'}...")
                    
                    if is_visible and text and len(text.strip()) > 10:
                        # 尝试获取更多属性
                        try:
                            attrs = await li.evaluate("""
                                el => Array.from(el.attributes).map(attr => `${attr.name}="${attr.value}"`).join(' ')
                            """)
                            print(f"    属性: {attrs}")
                            
                            # 检查是否是可点击的
                            tag_name = await li.evaluate("el => el.tagName")
                            onclick = await li.get_attribute("onclick")
                            href = await li.get_attribute("href")
                            
                            print(f"    标签: {tag_name}")
                            if onclick:
                                print(f"    点击事件: {onclick}")
                            if href:
                                print(f"    链接: {href}")
                                
                        except Exception as e:
                            print(f"    获取属性时出错: {e}")
                    
                    print()
                    
                except Exception as e:
                    print(f"  处理li[{i}]时出错: {e}")
        
        except Exception as e:
            print(f"手动提取出错: {e}")
        
        await playwright.stop()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    print("🧪 开始测试历史任务发现功能...")
    asyncio.run(test_history_discovery()) 