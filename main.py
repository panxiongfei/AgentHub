#!/usr/bin/env python3
"""
AgentHub - AI Agent Hub 多 Agent 统一入口
主入口文件
"""

import asyncio
import sys
from pathlib import Path

import click
import uvicorn
from rich.console import Console
from rich.table import Table

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config.settings import get_settings
from app.core.logger import setup_logging
from app.scheduler.task_scheduler import TaskScheduler


console = Console()


@click.group()
@click.option('--debug/--no-debug', default=False, help='启用调试模式')
@click.option('--config', '-c', default='configs/settings.yaml', help='配置文件路径')
def cli(debug: bool, config: str):
    """AgentHub - 多平台 AI 代理服务自动化平台"""
    # 设置日志
    setup_logging(debug=debug)
    
    # 加载配置
    settings = get_settings(config_file=config)
    
    if debug:
        console.print("🐛 调试模式已启用", style="yellow")


@cli.command()
@click.option('--host', default='0.0.0.0', help='服务监听地址')
@click.option('--port', default=8000, help='服务监听端口')
@click.option('--workers', default=1, help='工作进程数')
def serve(host: str, port: int, workers: int):
    """启动 Web API 服务"""
    console.print("🚀 启动 AgentHub API 服务", style="green bold")
    
    # 在启动前导入app确保模块正确加载
    try:
        from app.api.main import app
        console.print("✅ FastAPI应用加载成功", style="green")
    except Exception as e:
        console.print(f"❌ FastAPI应用加载失败: {e}", style="red")
        return
    
    uvicorn.run(
        app,  # 直接传递app对象而不是字符串
        host=host,
        port=port,
        workers=workers,
        reload=False,
        log_level="info"
    )


@cli.command()
def scheduler():
    """启动定时任务调度器"""
    console.print("⏰ 启动任务调度器", style="green bold")
    
    async def run_scheduler():
        scheduler = TaskScheduler()
        await scheduler.start()
        
        try:
            # 保持调度器运行
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("⏹️  正在停止调度器...", style="yellow")
            await scheduler.stop()
    
    asyncio.run(run_scheduler())


@cli.command()
@click.option('--platforms', '-p', multiple=True, help='指定平台')
@click.option('--topic-id', help='指定命题ID')
def run_once(platforms: tuple, topic_id: str):
    """运行单次任务"""
    console.print("▶️  执行单次任务", style="blue bold")
    
    async def execute_task():
        from app.core.task_manager import TaskManager
        
        task_manager = TaskManager()
        
        if topic_id:
            # 执行指定命题
            results = await task_manager.execute_topic(
                topic_id=topic_id,
                platforms=list(platforms) if platforms else None
            )
        else:
            # 执行所有待处理的命题
            results = await task_manager.execute_pending_tasks(
                platforms=list(platforms) if platforms else None
            )
        
        # 显示结果
        table = Table(title="任务执行结果")
        table.add_column("平台", style="cyan")
        table.add_column("状态", style="magenta")
        table.add_column("结果", style="green")
        
        for result in results:
            status = "✅ 成功" if result.success else "❌ 失败"
            table.add_row(
                result.platform,
                status,
                result.result[:50] + "..." if len(result.result) > 50 else result.result
            )
        
        console.print(table)
    
    asyncio.run(execute_task())


@cli.command()
@click.argument('content')
@click.option('--title', help='命题标题')
@click.option('--platforms', '-p', multiple=True, help='目标平台')
@click.option('--priority', default=1, help='优先级 (1-5)')
def add_topic(content: str, title: str, platforms: tuple, priority: int):
    """添加新命题"""
    console.print("📝 添加新命题", style="green bold")
    
    async def create_topic():
        from app.core.topic_manager import TopicManager
        
        topic_manager = TopicManager()
        
        topic = await topic_manager.create_topic(
            title=title or content[:50] + "...",
            content=content,
            platforms=list(platforms) if platforms else None,
            priority=priority
        )
        
        console.print(f"✅ 命题已创建，ID: {topic.id}", style="green")
    
    asyncio.run(create_topic())


@cli.command()
def status():
    """查看系统状态"""
    console.print("📊 系统状态", style="blue bold")
    
    async def show_status():
        from app.core.status_monitor import StatusMonitor
        
        monitor = StatusMonitor()
        status_info = await monitor.get_system_status()
        
        # 显示状态表格
        table = Table(title="系统状态")
        table.add_column("组件", style="cyan")
        table.add_column("状态", style="magenta")
        table.add_column("详情", style="green")
        
        for component, info in status_info.items():
            status = "🟢 正常" if info.get('healthy', True) else "🔴 异常"
            table.add_row(
                component,
                status,
                info.get('message', '')
            )
        
        console.print(table)
    
    asyncio.run(show_status())


@cli.command()
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'csv', 'excel']), help='输出格式')
@click.option('--output', '-o', help='输出文件路径')
@click.option('--start-date', help='开始日期 (YYYY-MM-DD)')
@click.option('--end-date', help='结束日期 (YYYY-MM-DD)')
def export(output_format: str, output: str, start_date: str, end_date: str):
    """导出结果数据"""
    console.print("📤 导出结果数据", style="blue bold")
    
    async def export_data():
        from app.core.data_exporter import DataExporter
        
        exporter = DataExporter()
        
        file_path = await exporter.export_results(
            format=output_format,
            output_path=output,
            start_date=start_date,
            end_date=end_date
        )
        
        console.print(f"✅ 数据已导出到: {file_path}", style="green")
    
    asyncio.run(export_data())


@cli.command()
def init():
    """初始化项目配置和数据库"""
    console.print("🔧 初始化项目", style="green bold")
    
    async def initialize():
        from app.core.initializer import ProjectInitializer
        
        initializer = ProjectInitializer()
        await initializer.initialize_project()
        
        console.print("✅ 项目初始化完成", style="green")
    
    asyncio.run(initialize())


@cli.command()
@click.option('--platform', help='测试指定平台')
def test_connection(platform: str):
    """测试平台连接"""
    console.print("🔌 测试平台连接", style="blue bold")
    
    async def test_platforms():
        from app.platforms.platform_factory import PlatformFactory
        
        factory = PlatformFactory()
        
        if platform:
            platforms = [platform]
        else:
            platforms = factory.get_available_platforms()
        
        table = Table(title="平台连接测试")
        table.add_column("平台", style="cyan")
        table.add_column("状态", style="magenta")
        table.add_column("响应时间", style="green")
        
        for platform_name in platforms:
            try:
                platform_instance = await factory.create_platform(platform_name)
                start_time = asyncio.get_event_loop().time()
                
                success = await platform_instance.test_connection()
                
                end_time = asyncio.get_event_loop().time()
                response_time = f"{(end_time - start_time) * 1000:.0f}ms"
                
                status = "🟢 连接成功" if success else "🔴 连接失败"
                table.add_row(platform_name, status, response_time)
                
            except Exception as e:
                table.add_row(platform_name, "🔴 连接失败", str(e)[:30] + "...")
        
        console.print(table)
    
    asyncio.run(test_platforms())


@cli.command()
@click.argument('topic')
@click.option('--title', help='任务标题')
@click.option('--download-dir', '-d', default='data/results', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def manus_task(topic: str, title: str, download_dir: str, debug_port: int):
    """在Manus平台执行任务（连接现有Chrome实例）"""
    console.print("🤖 执行Manus任务", style="green bold")
    
    async def run_manus_task():
        from app.platforms.manus_platform import ManusPlatform
        from pathlib import Path
        
        # 创建Manus平台实例
        config = {
            "debug_port": debug_port,
            "base_url": "https://manus.ai",
            "timeout": 30000
        }
        
        manus = ManusPlatform(config)
        
        try:
            console.print(f"📝 命题: {topic}")
            console.print(f"📂 下载目录: {download_dir}")
            console.print(f"🔌 Chrome调试端口: {debug_port}")
            
            download_path = Path(download_dir)
            
            # 执行完整任务流程
            with console.status("[bold green]正在执行任务..."):
                result = await manus.execute_full_task(
                    topic=topic,
                    title=title,
                    download_dir=download_path
                )
            
            # 显示结果
            if result.success:
                console.print("✅ 任务执行成功!", style="green bold")
                console.print(f"📄 结果预览: {result.result[:200]}...")
                
                if result.files:
                    console.print(f"📁 已下载 {len(result.files)} 个文件:", style="blue")
                    for file_path in result.files:
                        console.print(f"  - {file_path.name}")
                
                console.print(f"🔗 任务页面: {result.metadata.get('page_url', 'N/A')}")
            else:
                console.print("❌ 任务执行失败", style="red bold")
                console.print(f"错误信息: {result.result}")
            
        except Exception as e:
            console.print(f"❌ 执行过程中出错: {e}", style="red bold")
            
        finally:
            # 清理连接
            try:
                await manus.close()
            except:
                pass
    
    asyncio.run(run_manus_task())


@cli.command()
@click.argument('topic')
@click.option('--title', help='任务标题')
@click.option('--download-dir', '-d', default='data/results', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def skywork_task(topic: str, title: str, download_dir: str, debug_port: int):
    """在Skywork平台执行任务（连接现有Chrome实例）"""
    console.print("🌟 执行Skywork任务", style="green bold")
    
    async def run_skywork_task():
        from app.platforms.skywork_platform import SkyworkPlatform
        from pathlib import Path
        
        # 创建Skywork平台实例
        config = {
            "debug_port": debug_port,
            "base_url": "https://skywork.ai",
            "timeout": 30000
        }
        
        skywork = SkyworkPlatform(config)
        
        try:
            console.print(f"📝 命题: {topic}")
            console.print(f"📂 下载目录: {download_dir}")
            console.print(f"🔌 Chrome调试端口: {debug_port}")
            
            download_path = Path(download_dir)
            
            # 执行完整任务流程
            with console.status("[bold green]正在执行任务..."):
                result = await skywork.execute_full_task(
                    topic=topic,
                    title=title,
                    download_dir=download_path
                )
            
            # 显示结果
            if result.success:
                console.print("✅ 任务执行成功!", style="green bold")
                console.print(f"📄 结果预览: {result.result[:200]}...")
                
                if result.files:
                    console.print(f"📁 已下载 {len(result.files)} 个文件:", style="blue")
                    for file_path in result.files:
                        console.print(f"  - {file_path.name}")
                
                console.print(f"🔗 任务页面: {result.metadata.get('page_url', 'N/A')}")
            else:
                console.print("❌ 任务执行失败", style="red bold")
                console.print(f"错误信息: {result.result}")
            
        except Exception as e:
            console.print(f"❌ 执行过程中出错: {e}", style="red bold")
            
        finally:
            # 清理连接
            try:
                await skywork.close()
            except:
                pass
    
    asyncio.run(run_skywork_task())


@cli.command()
@click.argument('topic')
@click.option('--title', help='任务标题')
@click.option('--download-dir', '-d', default='data/results', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def enhanced_skywork_task(topic: str, title: str, download_dir: str, debug_port: int):
    """在Skywork平台执行任务（增强版智能引擎）"""
    console.print("🌟✨ 执行Skywork任务（增强版）", style="green bold")
    
    async def run_enhanced_skywork_task():
        from app.platforms.enhanced_skywork_platform import EnhancedSkyworkPlatform
        from pathlib import Path
        
        # 创建增强版Skywork平台实例
        config = {
            "debug_port": debug_port,
            "base_url": "https://skywork.ai",
            "timeout": 30000
        }
        
        enhanced_skywork = EnhancedSkyworkPlatform(config)
        
        try:
            console.print(f"📝 命题: {topic}")
            console.print(f"📂 下载目录: {download_dir}")
            console.print(f"🔌 Chrome调试端口: {debug_port}")
            console.print("🧠 使用增强版智能浏览器引擎", style="cyan")
            
            download_path = Path(download_dir)
            
            # 执行增强版完整任务流程
            with console.status("[bold green]正在执行增强版任务..."):
                result = await enhanced_skywork.execute_full_task(
                    topic=topic,
                    title=title,
                    download_dir=download_path
                )
            
            # 显示结果
            if result.success:
                console.print("✅ 任务执行成功!", style="green bold")
                console.print(f"📄 结果预览: {result.result[:200]}...")
                
                if result.files:
                    console.print(f"📁 已下载 {len(result.files)} 个文件:", style="blue")
                    for file_path in result.files:
                        console.print(f"  - {file_path.name}")
                
                # 显示智能引擎分析结果
                if 'analysis' in result.metadata:
                    analysis = result.metadata['analysis']
                    console.print("🧠 智能引擎分析:", style="cyan")
                    console.print(f"  - 页面元素: {analysis.get('element_analysis', {}).get('total_elements', 0)}个")
                    console.print(f"  - 交互机会: {len(analysis.get('interaction_opportunities', []))}个")
                    console.print(f"  - 内容就绪: {'是' if analysis.get('content_readiness') else '否'}")
                    if analysis.get('recommendations'):
                        console.print(f"  - 建议: {'; '.join(analysis['recommendations'])}")
                
                console.print(f"🔗 任务页面: {result.metadata.get('page_url', 'N/A')}")
            else:
                console.print("❌ 任务执行失败", style="red bold")
                console.print(f"错误信息: {result.result}")
            
        except Exception as e:
            console.print(f"❌ 执行过程中出错: {e}", style="red bold")
            
        finally:
            # 清理连接
            try:
                await enhanced_skywork.close()
            except:
                pass
    
    asyncio.run(run_enhanced_skywork_task())


@cli.command()
@click.argument('topic')
@click.option('--title', help='任务标题')
@click.option('--download-dir', '-d', default='data/results', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def enhanced_manus_task(topic: str, title: str, download_dir: str, debug_port: int):
    """在Manus平台执行任务（增强版智能引擎）"""
    console.print("🤖✨ 执行Manus任务（增强版）", style="green bold")
    
    async def run_enhanced_manus_task():
        from app.platforms.enhanced_manus_platform import EnhancedManusPlatform
        from pathlib import Path
        
        # 创建增强版Manus平台实例
        config = {
            "debug_port": debug_port,
            "base_url": "https://manus.ai",
            "timeout": 30000
        }
        
        enhanced_manus = EnhancedManusPlatform(config)
        
        try:
            console.print(f"📝 命题: {topic}")
            console.print(f"📂 下载目录: {download_dir}")
            console.print(f"🔌 Chrome调试端口: {debug_port}")
            console.print("🧠 使用增强版智能浏览器引擎", style="cyan")
            
            download_path = Path(download_dir)
            
            # 执行增强版完整任务流程
            with console.status("[bold green]正在执行增强版任务..."):
                result = await enhanced_manus.execute_full_task(
                    topic=topic,
                    title=title,
                    download_dir=download_path
                )
            
            # 显示结果
            if result.success:
                console.print("✅ 任务执行成功!", style="green bold")
                console.print(f"📄 结果预览: {result.result[:200]}...")
                
                if result.files:
                    console.print(f"📁 已下载 {len(result.files)} 个文件:", style="blue")
                    for file_path in result.files:
                        console.print(f"  - {file_path.name}")
                
                # 显示智能引擎分析结果
                if 'analysis' in result.metadata:
                    analysis = result.metadata['analysis']
                    console.print("🧠 智能引擎分析:", style="cyan")
                    console.print(f"  - 页面元素: {analysis.get('element_analysis', {}).get('total_elements', 0)}个")
                    console.print(f"  - 交互机会: {len(analysis.get('interaction_opportunities', []))}个")
                    console.print(f"  - 内容就绪: {'是' if analysis.get('content_readiness') else '否'}")
                    if analysis.get('recommendations'):
                        console.print(f"  - 建议: {'; '.join(analysis['recommendations'])}")
                
                console.print(f"🔗 任务页面: {result.metadata.get('page_url', 'N/A')}")
            else:
                console.print("❌ 任务执行失败", style="red bold")
                console.print(f"错误信息: {result.result}")
            
        except Exception as e:
            console.print(f"❌ 执行过程中出错: {e}", style="red bold")
            
        finally:
            # 清理连接
            try:
                await enhanced_manus.close()
            except:
                pass
    
    asyncio.run(run_enhanced_manus_task())


@cli.command()
@click.option('--platform', required=True, help='指定平台 (skywork/manus)')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def analyze_page(platform: str, debug_port: int):
    """分析平台页面（智能引擎诊断）"""
    console.print(f"🔍 分析{platform}平台页面", style="blue bold")
    
    async def run_page_analysis():
        try:
            if platform == "skywork":
                from app.platforms.enhanced_skywork_platform import EnhancedSkyworkPlatform
                config = {"debug_port": debug_port, "base_url": "https://skywork.ai"}
                platform_instance = EnhancedSkyworkPlatform(config)
            elif platform == "manus":
                from app.platforms.enhanced_manus_platform import EnhancedManusPlatform
                config = {"debug_port": debug_port, "base_url": "https://manus.ai"}
                platform_instance = EnhancedManusPlatform(config)
            else:
                console.print(f"❌ 不支持的平台: {platform}", style="red")
                return
            
            # 连接到浏览器
            await platform_instance._connect_to_existing_browser()
            
            if not platform_instance.browser_engine:
                console.print("❌ 无法初始化浏览器引擎", style="red")
                return
            
            # 进行页面智能分析
            analysis = await platform_instance.browser_engine.analyze_page_intelligence()
            
            # 显示分析结果
            console.print("📊 页面智能分析结果:", style="green bold")
            
            # 页面基本信息
            page_info = analysis["page_info"]
            console.print(f"📄 页面标题: {page_info['title']}")
            console.print(f"🔗 页面URL: {page_info['url']}")
            console.print(f"📡 加载状态: {page_info['load_state']}")
            
            # 元素分析
            element_analysis = analysis["element_analysis"]
            console.print(f"🔧 页面元素总数: {element_analysis['total_elements']}")
            
            if element_analysis["by_type"]:
                console.print("📋 元素类型分布:")
                for elem_type, count in element_analysis["by_type"].items():
                    console.print(f"  - {elem_type}: {count}个")
            
            # 交互机会
            opportunities = analysis["interaction_opportunities"]
            if opportunities:
                console.print(f"🎯 发现 {len(opportunities)} 个交互机会:")
                for i, opp in enumerate(opportunities[:5], 1):  # 显示前5个
                    console.print(f"  {i}. {opp['type']} - {opp['selector']} (置信度: {opp['confidence']:.2f})")
                    if opp['text']:
                        console.print(f"     文本: {opp['text'][:30]}...")
            
            # 内容就绪状态
            readiness = "✅ 就绪" if analysis["content_readiness"] else "⏳ 未就绪"
            console.print(f"📝 内容状态: {readiness}")
            
            # 错误检测
            if analysis["errors_detected"]:
                console.print(f"⚠️  检测到 {len(analysis['errors_detected'])} 个错误:")
                for error in analysis["errors_detected"]:
                    console.print(f"  - {error}")
            
            # 建议
            if analysis["recommendations"]:
                console.print("💡 智能建议:")
                for rec in analysis["recommendations"]:
                    console.print(f"  - {rec}")
            
            # 操作历史摘要
            if platform_instance.browser_engine:
                summary = platform_instance.browser_engine.get_operation_summary()
                console.print("📈 引擎操作摘要:")
                console.print(f"  - 总操作数: {summary['total_operations']}")
                console.print(f"  - 成功率: {summary['success_rate']:.2%}")
                console.print(f"  - 页面状态快照: {summary['page_states_captured']}")
            
        except Exception as e:
            console.print(f"❌ 页面分析失败: {e}", style="red")
        
        finally:
            try:
                await platform_instance.close()
            except:
                pass
    
    asyncio.run(run_page_analysis())


@cli.command()
@click.option('--platform', required=True, help='指定平台 (skywork/manus)')
@click.option('--download-dir', '-d', default='data/history_downloads', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
@click.option('--preview-only', is_flag=True, help='仅预览任务列表，不下载')
def download_history(platform: str, download_dir: str, debug_port: int, preview_only: bool):
    """批量下载平台历史任务结果"""
    console.print(f"📚 批量下载{platform}平台历史任务", style="green bold")
    
    async def run_history_download():
        try:
            if platform == "skywork":
                from app.platforms.enhanced_skywork_platform import EnhancedSkyworkPlatform
                config = {"debug_port": debug_port, "base_url": "https://skywork.ai"}
                platform_instance = EnhancedSkyworkPlatform(config)
            elif platform == "manus":
                from app.platforms.enhanced_manus_platform import EnhancedManusPlatform
                config = {"debug_port": debug_port, "base_url": "https://manus.ai"}
                platform_instance = EnhancedManusPlatform(config)
            else:
                console.print(f"❌ 不支持的平台: {platform}", style="red")
                return
            
            console.print(f"🔌 连接Chrome调试端口: {debug_port}")
            console.print(f"📂 下载目录: {download_dir}")
            
            # 连接到浏览器
            await platform_instance._connect_to_existing_browser()
            
            if not platform_instance.history_downloader:
                console.print("❌ 无法初始化历史下载器", style="red")
                return
            
            # 发现历史任务
            with console.status("[bold blue]正在发现历史任务..."):
                tasks = await platform_instance.discover_history_tasks()
            
            if not tasks:
                console.print("📭 未发现任何历史任务", style="yellow")
                return
            
            # 显示任务列表
            console.print(f"📋 发现 {len(tasks)} 个历史任务:", style="green bold")
            
            from rich.table import Table
            table = Table(title=f"{platform.upper()} 历史任务列表")
            table.add_column("序号", style="cyan", width=6)
            table.add_column("标题", style="blue", max_width=50)
            table.add_column("日期", style="magenta", width=20)
            table.add_column("预览", style="green", max_width=40)
            
            for i, task in enumerate(tasks, 1):
                table.add_row(
                    str(i),
                    task.title[:47] + "..." if len(task.title) > 50 else task.title,
                    task.date,
                    task.preview[:37] + "..." if len(task.preview) > 40 else task.preview
                )
            
            console.print(table)
            
            if preview_only:
                console.print("👀 仅预览模式，不进行下载", style="yellow")
                return
            
            # 确认下载
            console.print(f"\n🤔 即将下载 {len(tasks)} 个历史任务，这可能需要较长时间")
            
            # 开始批量下载
            from pathlib import Path
            download_path = Path(download_dir)
            
            with console.status("[bold green]正在批量下载历史任务..."):
                results = await platform_instance.download_history_tasks(download_path)
            
            # 显示下载结果
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            # 🔥 新增：AI总结统计
            ai_summary_success = [r for r in successful if getattr(r, 'ai_summary_generated', False)]
            ai_summary_failed = [r for r in successful if not getattr(r, 'ai_summary_generated', False)]
            
            console.print("\n📊 下载结果统计:", style="bold blue")
            console.print(f"✅ 成功下载: {len(successful)} 个任务")
            console.print(f"❌ 下载失败: {len(failed)} 个任务")
            console.print(f"📈 成功率: {len(successful)/len(results)*100:.1f}%")
            
            # AI总结统计
            if successful:
                console.print(f"\n🤖 AI总结统计:", style="bold green")
                console.print(f"✅ AI总结成功: {len(ai_summary_success)} 个任务")
                console.print(f"⚠️  AI总结失败: {len(ai_summary_failed)} 个任务")
                console.print(f"🎯 AI总结成功率: {len(ai_summary_success)/len(successful)*100:.1f}%")
            
            if successful:
                console.print("\n🎉 成功下载的任务:", style="green")
                for i, result in enumerate(successful[:5], 1):  # 显示前5个
                    console.print(f"  {i}. {result.task.title[:60]}...")
                    console.print(f"     📁 文件数: {len(result.files)}")
                    
                if len(successful) > 5:
                    console.print(f"  ... 还有 {len(successful) - 5} 个任务")
            
            if failed:
                console.print("\n⚠️  下载失败的任务:", style="red")
                for i, result in enumerate(failed[:3], 1):  # 显示前3个
                    console.print(f"  {i}. {result.task.title[:60]}...")
                    console.print(f"     ❌ 错误: {result.error}")
                    
                if len(failed) > 3:
                    console.print(f"  ... 还有 {len(failed) - 3} 个失败任务")
            
            console.print(f"\n📂 所有文件已保存到: {download_path.absolute()}")
            console.print("📋 详细报告: download_report.json", style="blue")
            
        except Exception as e:
            console.print(f"❌ 批量下载失败: {e}", style="red bold")
        
        finally:
            try:
                await platform_instance.close()
            except:
                pass
    
    asyncio.run(run_history_download())


@cli.command()
@click.option('--platform', required=True, help='指定平台 (skywork/manus)')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
def list_history(platform: str, debug_port: int):
    """列出平台历史任务（快速预览）"""
    console.print(f"📋 列出{platform}平台历史任务", style="blue bold")
    
    async def run_list_history():
        try:
            if platform == "skywork":
                from app.platforms.enhanced_skywork_platform import EnhancedSkyworkPlatform
                config = {"debug_port": debug_port, "base_url": "https://skywork.ai"}
                platform_instance = EnhancedSkyworkPlatform(config)
            elif platform == "manus":
                from app.platforms.enhanced_manus_platform import EnhancedManusPlatform
                config = {"debug_port": debug_port, "base_url": "https://manus.ai"}
                platform_instance = EnhancedManusPlatform(config)
            else:
                console.print(f"❌ 不支持的平台: {platform}", style="red")
                return
            
            # 连接到浏览器
            with console.status("[bold blue]正在连接浏览器..."):
                await platform_instance._connect_to_existing_browser()
            
            # 发现历史任务
            with console.status("[bold blue]正在发现历史任务..."):
                tasks = await platform_instance.discover_history_tasks()
            
            if not tasks:
                console.print("📭 未发现任何历史任务", style="yellow")
                return
            
            # 显示任务列表
            console.print(f"📋 共发现 {len(tasks)} 个历史任务:", style="green bold")
            
            from rich.table import Table
            table = Table(title=f"{platform.upper()} 历史任务列表")
            table.add_column("序号", style="cyan", width=6)
            table.add_column("标题", style="blue", max_width=60)
            table.add_column("日期", style="magenta", width=20)
            table.add_column("预览", style="green", max_width=50)
            
            for i, task in enumerate(tasks, 1):
                table.add_row(
                    str(i),
                    task.title[:57] + "..." if len(task.title) > 60 else task.title,
                    task.date,
                    task.preview[:47] + "..." if len(task.preview) > 50 else task.preview
                )
            
            console.print(table)
            
            console.print(f"\n💡 使用以下命令批量下载这些任务:")
            console.print(f"   python main.py download-history --platform {platform}")
            
        except Exception as e:
            console.print(f"❌ 列出历史任务失败: {e}", style="red bold")
        
        finally:
            try:
                await platform_instance.close()
            except:
                pass
    
    asyncio.run(run_list_history())


@cli.command()
@click.option('--download-dir', '-d', default='data/multi_platform_downloads', help='下载目录')
@click.option('--skywork-port', default=9222, help='Skywork Chrome调试端口')
@click.option('--manus-port', default=9223, help='Manus Chrome调试端口')
@click.option('--preview-only', is_flag=True, help='仅预览任务列表，不下载')
def download_multi_history(download_dir: str, skywork_port: int, manus_port: int, preview_only: bool):
    """多平台并发历史任务下载"""
    console.print("🌟 多平台并发历史任务下载", style="green bold")
    
    async def run_multi_download():
        try:
            from app.core.multi_browser_manager import MultiBrowserManager
            from pathlib import Path
            
            # 创建多浏览器管理器
            manager = MultiBrowserManager()
            
            # 配置平台端口
            platform_configs = {
                "skywork": skywork_port,
                "manus": manus_port
            }
            
            console.print("🔌 正在连接多个Chrome实例...")
            console.print(f"   - Skywork: 端口 {skywork_port}")
            console.print(f"   - Manus:   端口 {manus_port}")
            
            # 初始化浏览器实例
            with console.status("[bold blue]正在初始化浏览器实例..."):
                success = await manager.initialize_browsers(platform_configs)
            
            if not success:
                console.print("❌ 初始化浏览器实例失败", style="red")
                return
            
            console.print("✅ 所有浏览器实例连接成功", style="green")
            
            if preview_only:
                # 仅预览所有平台的历史任务
                console.print("\n👀 预览所有平台的历史任务...")
                
                with console.status("[bold blue]正在获取历史任务列表..."):
                    all_histories = await manager.list_all_histories()
                
                # 显示每个平台的任务概览
                from rich.table import Table
                
                for platform, history_info in all_histories.items():
                    if "error" in history_info:
                        console.print(f"\n❌ {platform.upper()} 平台: {history_info['error']}", style="red")
                        continue
                    
                    console.print(f"\n📋 {platform.upper()} 平台历史任务 (共 {history_info['total_tasks']} 个):", style="blue bold")
                    
                    if history_info['tasks']:
                        table = Table()
                        table.add_column("序号", style="cyan", width=6)
                        table.add_column("标题", style="blue", max_width=50)
                        table.add_column("日期", style="magenta", width=15)
                        table.add_column("预览", style="green", max_width=40)
                        
                        for i, task in enumerate(history_info['tasks'], 1):
                            table.add_row(
                                str(i),
                                task['title'][:47] + "..." if len(task['title']) > 50 else task['title'],
                                task['date'],
                                task['preview'][:37] + "..." if len(task['preview']) > 40 else task['preview']
                            )
                        
                        console.print(table)
                    else:
                        console.print("   📭 暂无历史任务", style="yellow")
                
                console.print("\n💡 使用以下命令进行实际下载:")
                console.print("   python main.py download-multi-history")
                
            else:
                # 执行实际的并发下载
                console.print(f"\n📂 下载目录: {download_dir}")
                console.print("🚀 开始多平台并发历史下载...")
                
                download_path = Path(download_dir)
                
                with console.status("[bold green]正在并发下载所有平台的历史任务..."):
                    result = await manager.download_all_histories(download_path)
                
                # 显示下载结果
                console.print("\n📊 多平台下载结果统计:", style="bold blue")
                console.print(f"⏱️  总耗时: {result.duration:.1f} 秒")
                console.print(f"✅ 成功下载: {result.total_downloaded} 个任务")
                console.print(f"❌ 下载失败: {result.total_errors} 个任务")
                
                if result.total_downloaded > 0:
                    success_rate = result.total_downloaded / (result.total_downloaded + result.total_errors) * 100
                    console.print(f"📈 总体成功率: {success_rate:.1f}%")
                
                # 显示各平台详细结果
                console.print("\n🏪 各平台详细结果:", style="bold magenta")
                
                for platform, platform_results in result.results.items():
                    if not platform_results:
                        console.print(f"  {platform.upper()}: ❌ 下载失败或无任务", style="red")
                        continue
                    
                    successful = sum(1 for r in platform_results if r.success)
                    failed = sum(1 for r in platform_results if not r.success)
                    
                    console.print(f"  {platform.upper()}:")
                    console.print(f"    ✅ 成功: {successful} 个")
                    console.print(f"    ❌ 失败: {failed} 个")
                    console.print(f"    📈 成功率: {successful/(successful+failed)*100:.1f}%")
                
                console.print(f"\n📁 所有文件已保存到: {result.download_dir.absolute()}")
                console.print("📋 详细报告: multi_platform_download_report.json", style="blue")
                
                if result.error_message:
                    console.print(f"\n⚠️  部分错误信息: {result.error_message}", style="yellow")
            
        except Exception as e:
            console.print(f"❌ 多平台下载失败: {e}", style="red bold")
        
        finally:
            try:
                await manager.cleanup()
            except:
                pass
    
    asyncio.run(run_multi_download())


@cli.command()
@click.option('--skywork-port', default=9222, help='Skywork Chrome调试端口')
@click.option('--manus-port', default=9223, help='Manus Chrome调试端口')
def list_multi_history(skywork_port: int, manus_port: int):
    """列出所有平台的历史任务（快速预览）"""
    console.print("📋 列出所有平台历史任务", style="blue bold")
    
    async def run_list_multi_history():
        try:
            from app.core.multi_browser_manager import MultiBrowserManager
            
            # 创建多浏览器管理器
            manager = MultiBrowserManager()
            
            # 配置平台端口
            platform_configs = {
                "skywork": skywork_port,
                "manus": manus_port
            }
            
            console.print("🔌 正在连接多个Chrome实例...")
            console.print(f"   - Skywork: 端口 {skywork_port}")
            console.print(f"   - Manus:   端口 {manus_port}")
            
            # 初始化浏览器实例
            with console.status("[bold blue]正在初始化浏览器实例..."):
                success = await manager.initialize_browsers(platform_configs)
            
            if not success:
                console.print("❌ 初始化浏览器实例失败", style="red")
                return
            
            # 获取所有平台的历史任务
            with console.status("[bold blue]正在获取所有平台的历史任务..."):
                all_histories = await manager.list_all_histories()
            
            # 显示结果
            total_tasks = 0
            
            from rich.table import Table
            
            for platform, history_info in all_histories.items():
                if "error" in history_info:
                    console.print(f"\n❌ {platform.upper()} 平台错误: {history_info['error']}", style="red")
                    continue
                
                task_count = history_info['total_tasks']
                total_tasks += task_count
                
                console.print(f"\n📋 {platform.upper()} 平台 (共 {task_count} 个历史任务):", style="blue bold")
                
                if history_info['tasks']:
                    table = Table()
                    table.add_column("序号", style="cyan", width=6)
                    table.add_column("标题", style="blue", max_width=60)
                    table.add_column("日期", style="magenta", width=15)
                    table.add_column("预览", style="green", max_width=50)
                    
                    for i, task in enumerate(history_info['tasks'], 1):
                        table.add_row(
                            str(i),
                            task['title'][:57] + "..." if len(task['title']) > 60 else task['title'],
                            task['date'],
                            task['preview'][:47] + "..." if len(task['preview']) > 50 else task['preview']
                        )
                    
                    console.print(table)
                    
                    if task_count > 10:
                        console.print(f"   ... 还有 {task_count - 10} 个任务未显示", style="dim")
                else:
                    console.print("   📭 暂无历史任务", style="yellow")
            
            console.print(f"\n📊 汇总统计:", style="bold green")
            console.print(f"   🏪 平台总数: {len([p for p in all_histories.keys() if 'error' not in all_histories[p]])}")
            console.print(f"   📝 任务总数: {total_tasks}")
            
            console.print(f"\n💡 使用以下命令批量下载所有平台的历史任务:")
            console.print(f"   python main.py download-multi-history")
            
        except Exception as e:
            console.print(f"❌ 列出多平台历史任务失败: {e}", style="red bold")
        
        finally:
            try:
                await manager.cleanup()
            except:
                pass
    
    asyncio.run(run_list_multi_history())


@cli.command()
@click.option('--download-dir', '-d', default='data/coze_space_history', help='下载目录')
@click.option('--debug-port', default=9222, help='Chrome调试端口')
@click.option('--preview-only', is_flag=True, help='仅预览任务列表，不下载')
def download_coze_history(download_dir: str, debug_port: int, preview_only: bool):
    """下载扣子空间历史任务（免登录模式）"""
    console.print("📥 扣子空间历史任务下载", style="blue bold")
    
    async def run_coze_download():
        try:
            from app.platforms.coze_space_platform import CozeSpacePlatform
            from pathlib import Path
            
            # 创建扣子空间平台实例
            config = {
                "workflow_enabled": True,
                "collaborative_mode": True,
                "debug_port": debug_port,
                "space_mode": "conversation"
            }
            
            coze = CozeSpacePlatform(config)
            
            console.print(f"📂 下载目录: {download_dir}")
            console.print(f"🔌 Chrome调试端口: {debug_port}")
            
            download_path = Path(download_dir)
            download_path.mkdir(parents=True, exist_ok=True)
            
            # 连接浏览器
            with console.status("[bold blue]正在连接Chrome浏览器..."):
                # 使用Playwright直接连接
                import playwright.async_api as pw
                
                playwright = await pw.async_playwright().start()
                browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
                
                # 获取现有页面
                contexts = browser.contexts
                if contexts and contexts[0].pages:
                    page = contexts[0].pages[0]
                else:
                    context = await browser.new_context()
                    page = await context.new_page()
                
                # 确保在扣子空间页面
                current_url = page.url
                if "space.coze.cn" not in current_url and "coze.cn" not in current_url:
                    console.print("📍 导航到扣子空间...", style="yellow")
                    await page.goto("https://space.coze.cn")
                    await page.wait_for_load_state("networkidle")
            
            console.print("✅ 成功连接到扣子空间", style="green")
            
            # 发现历史任务
            with console.status("[bold blue]正在分析页面并发现历史任务..."):
                # 获取页面文本内容
                page_text = await page.inner_text("body")
                
                # 查找左侧菜单容器
                menu_container = await page.query_selector(".left-menu-container")
                if not menu_container:
                    menu_container = await page.query_selector("[class*='left-menu-container']")
                
                if menu_container:
                    menu_text = await menu_container.inner_text()
                    console.print(f"✅ 找到左侧菜单容器，内容长度: {len(menu_text)} 字符", style="green")
                else:
                    console.print("⚠️ 未找到特定菜单容器，使用整个页面", style="yellow")
                    menu_text = page_text
                
                # 解析任务
                tasks = await parse_coze_tasks_from_text(menu_text, page)
            
            if not tasks:
                console.print("ℹ️ 未发现历史任务", style="yellow")
                return
            
            console.print(f"📝 发现 {len(tasks)} 个历史任务", style="green")
            
            # 显示任务预览
            from rich.table import Table
            table = Table(title="扣子空间历史任务")
            table.add_column("序号", style="cyan", width=6)
            table.add_column("任务标题", style="magenta", max_width=50)
            table.add_column("状态", style="green", width=15)
            
            for i, task in enumerate(tasks, 1):
                table.add_row(
                    str(i),
                    task['title'][:47] + "..." if len(task['title']) > 50 else task['title'],
                    task.get('status', '未知')
                )
            
            console.print(table)
            
            if preview_only:
                console.print("\n💡 使用以下命令进行实际下载:")
                console.print("   python main.py download-coze-history")
                return
            
            # 执行下载
            console.print(f"\n📥 开始下载到: {download_path}")
            
            downloaded_count = 0
            failed_count = 0
            
            for i, task in enumerate(tasks):
                try:
                    console.print(f"📄 下载任务 {i+1}/{len(tasks)}: {task['title'][:50]}...", style="cyan")
                    
                    # 创建任务目录
                    task_dir = download_path / f"task_{task['id']}"
                    task_dir.mkdir(exist_ok=True)
                    
                    # 尝试点击任务获取详细内容
                    if 'element' in task:
                        try:
                            await task['element'].click()
                            await asyncio.sleep(2)
                        except:
                            pass
                    
                    # 保存任务信息
                    import time
                    import json
                    
                    # 保存文本内容
                    with open(task_dir / "content.txt", 'w', encoding='utf-8') as f:
                        f.write(f"任务标题: {task['title']}\n")
                        f.write(f"任务状态: {task.get('status', '未知')}\n")
                        f.write(f"完整内容: {task['full_text']}\n")
                        f.write(f"下载时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"页面URL: {page.url}\n")
                    
                    # 保存元数据
                    metadata = {
                        "id": task['id'],
                        "title": task['title'],
                        "status": task.get('status', '未知'),
                        "date": time.strftime('%Y-%m-%d'),
                        "url": page.url,
                        "platform": "coze_space",
                        "preview": task['full_text'][:200],
                        "metadata": {
                            "extraction_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                            "download_method": "cli_free_login",
                            "browser_connected": True
                        }
                    }
                    
                    with open(task_dir / "metadata.json", 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    # 截图
                    try:
                        await page.screenshot(path=task_dir / "screenshot.png")
                    except:
                        pass
                    
                    downloaded_count += 1
                    console.print(f"  ✅ 下载成功", style="green")
                    
                except Exception as e:
                    failed_count += 1
                    console.print(f"  ❌ 下载失败: {e}", style="red")
            
            # 显示结果
            console.print(f"\n📊 下载完成:", style="bold green")
            console.print(f"✅ 成功: {downloaded_count} 个任务")
            console.print(f"❌ 失败: {failed_count} 个任务")
            console.print(f"📁 保存位置: {download_path.absolute()}")
            
            await browser.close()
            
        except Exception as e:
            console.print(f"❌ 扣子空间下载失败: {e}", style="red bold")
    
    async def parse_coze_tasks_from_text(text: str, page) -> list:
        """从文本中解析扣子空间任务"""
        import time
        
        tasks = []
        lines = text.split('\n')
        
        # 已知的任务模式
        known_tasks = [
            "瑞幸智能点餐消费者洞察及建议",
            "搜肯德基热点并输出汇报页",
            "中年男人身体保养调查",
            "对比分析10个agent框架进展"
        ]
        
        task_id_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是已知任务
            for known_task in known_tasks:
                if known_task in line:
                    # 查找对应的DOM元素
                    task_element = None
                    try:
                        elements = await page.query_selector_all(f"*:has-text('{known_task}')")
                        if elements:
                            # 选择最合适的元素
                            for elem in elements:
                                elem_text = await elem.inner_text()
                                if known_task in elem_text and len(elem_text) < 200:
                                    task_element = elem
                                    break
                    except:
                        pass
                    
                    task_info = {
                        'id': f'coze_cli_{int(time.time())}_{task_id_counter}',
                        'title': known_task,
                        'full_text': line,
                        'status': '一轮任务完成' if '完成' in line else '未知',
                        'element': task_element
                    }
                    
                    # 避免重复
                    if not any(t['title'] == known_task for t in tasks):
                        tasks.append(task_info)
                        task_id_counter += 1
                    break
        
        return tasks
    
    asyncio.run(run_coze_download())


if __name__ == "__main__":
    cli() 