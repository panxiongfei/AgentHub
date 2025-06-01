#!/usr/bin/env python3
"""
AgentHub 服务状态检查脚本
"""

import requests
import sys
import time
from rich.console import Console
from rich.table import Table

console = Console()

def check_backend():
    """检查后端API服务状态"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"健康状态: {data.get('status')}, 版本: {data.get('version')}"
        else:
            return False, f"HTTP状态码: {response.status_code}"
    except Exception as e:
        return False, f"连接失败: {str(e)}"

def check_frontend():
    """检查前端服务状态"""
    # 先检查3003端口，然后3002，最后3001
    for port in [3003, 3002, 3001]:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
            if response.status_code == 200:
                return True, f"前端页面响应正常 (端口: {port})", port
            else:
                continue
        except Exception:
            continue
    return False, "所有端口连接失败 (尝试了3001, 3002, 3003)", None

def main():
    """主函数"""
    console.print("🔍 检查 AgentHub 服务状态...", style="blue bold")
    
    # 创建状态表格
    table = Table(title="AgentHub 服务状态")
    table.add_column("服务", style="cyan")
    table.add_column("地址", style="yellow")
    table.add_column("状态", style="magenta")
    table.add_column("详情", style="green")
    
    # 检查后端服务
    backend_ok, backend_msg = check_backend()
    backend_status = "🟢 正常" if backend_ok else "🔴 异常"
    table.add_row(
        "后端 API",
        "http://127.0.0.1:8000",
        backend_status,
        backend_msg
    )
    
    # 检查前端服务
    frontend_result = check_frontend()
    if len(frontend_result) == 3:
        frontend_ok, frontend_msg, port = frontend_result
        frontend_url = f"http://127.0.0.1:{port}" if port else "http://127.0.0.1:3001"
    else:
        frontend_ok, frontend_msg = frontend_result
        frontend_url = "http://127.0.0.1:3001"
        port = None
    
    frontend_status = "🟢 正常" if frontend_ok else "🔴 异常"
    table.add_row(
        "前端界面",
        frontend_url,
        frontend_status,
        frontend_msg
    )
    
    console.print(table)
    
    # 总结
    if backend_ok and frontend_ok:
        console.print("✅ AgentHub 管理系统运行正常！", style="green bold")
        console.print(f"📱 前端管理界面: {frontend_url}", style="blue")
        console.print("📋 API 文档: http://127.0.0.1:8000/docs", style="blue")
        console.print("🏥 健康检查: http://127.0.0.1:8000/health", style="blue")
        return 0
    else:
        console.print("❌ 部分服务异常，请检查日志", style="red bold")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 