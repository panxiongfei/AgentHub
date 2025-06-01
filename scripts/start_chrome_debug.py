#!/usr/bin/env python3
"""
启动Chrome浏览器调试模式的脚本
支持复用系统Chrome登录状态，避免重复登录
"""

import subprocess
import sys
import time
import shutil
import os
from pathlib import Path


def get_system_chrome_profile():
    """获取系统Chrome默认配置目录"""
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library/Application Support/Google/Chrome"
    elif system == "Windows":
        return Path.home() / "AppData/Local/Google/Chrome/User Data"
    elif system == "Linux":
        return Path.home() / ".config/google-chrome"
    else:
        return None


def copy_chrome_profile(source_dir: Path, target_dir: Path):
    """复制Chrome配置文件（包含登录状态）"""
    try:
        if not source_dir.exists():
            print(f"⚠️  系统Chrome配置目录不存在: {source_dir}")
            return False
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制关键配置文件和目录
        important_items = [
            "Default",  # 默认配置文件（包含cookie、登录状态等）
            "Local State",  # 本地状态文件
        ]
        
        for item in important_items:
            source_item = source_dir / item
            target_item = target_dir / item
            
            if source_item.exists():
                if source_item.is_dir():
                    if target_item.exists():
                        shutil.rmtree(target_item)
                    shutil.copytree(source_item, target_item, ignore_dangling_symlinks=True)
                    print(f"✅ 已复制目录: {item}")
                else:
                    shutil.copy2(source_item, target_item)
                    print(f"✅ 已复制文件: {item}")
            else:
                print(f"⚠️  未找到: {item}")
        
        print(f"🎉 Chrome配置复制完成，登录状态已保留！")
        return True
        
    except Exception as e:
        print(f"❌ 复制Chrome配置失败: {e}")
        return False


def start_chrome_debug_mode(port: int = 9222, user_data_dir: str = None, 
                           use_system_profile: bool = False, copy_profile: bool = False):
    """
    启动Chrome浏览器的调试模式
    
    Args:
        port: 调试端口
        user_data_dir: 用户数据目录
        use_system_profile: 是否使用系统Chrome配置（直接复用登录状态）
        copy_profile: 是否复制系统Chrome配置到调试目录
    """
    
    # 检测操作系统并设置Chrome路径
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    elif system == "Windows":
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]
    elif system == "Linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    else:
        print(f"不支持的操作系统: {system}")
        return False
    
    # 查找可用的Chrome路径
    chrome_path = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_path = path
            break
    
    if not chrome_path:
        print("未找到Chrome浏览器，请确保Chrome已安装")
        print("支持的路径:")
        for path in chrome_paths:
            print(f"  - {path}")
        return False
    
    # 处理用户数据目录配置
    if use_system_profile:
        # 使用系统Chrome配置（直接复用登录状态）
        system_profile = get_system_chrome_profile()
        if system_profile and system_profile.exists():
            user_data_dir = str(system_profile)
            print("🔄 使用系统Chrome配置（直接复用登录状态）")
            print("⚠️  注意：这可能会影响您的正常Chrome使用")
        else:
            print("⚠️  未找到系统Chrome配置，回退到独立配置")
            user_data_dir = str(Path.home() / "chrome_debug_data")
    
    elif copy_profile:
        # 复制系统配置到调试目录
        if not user_data_dir:
            user_data_dir = str(Path.home() / "chrome_debug_data")
        
        system_profile = get_system_chrome_profile()
        if system_profile:
            print("📋 复制系统Chrome配置...")
            success = copy_chrome_profile(system_profile, Path(user_data_dir))
            if not success:
                print("⚠️  配置复制失败，将使用空白配置")
        else:
            print("⚠️  未找到系统Chrome配置")
    
    else:
        # 使用独立配置目录
        if not user_data_dir:
            user_data_dir = str(Path.home() / "chrome_debug_data")
    
    # 启动Chrome命令
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
    ]
    
    # 如果不是使用系统配置，添加额外的调试参数
    if not use_system_profile:
        cmd.extend([
            "--no-default-browser-check",
            "--disable-extensions"
        ])
    
    cmd.append("https://manus.ai")
    
    print(f"启动Chrome调试模式...")
    print(f"端口: {port}")
    print(f"用户数据目录: {user_data_dir}")
    print(f"Chrome路径: {chrome_path}")
    
    try:
        # 启动Chrome进程
        process = subprocess.Popen(cmd)
        print(f"Chrome进程已启动 (PID: {process.pid})")
        print(f"调试地址: http://localhost:{port}")
        
        if use_system_profile or copy_profile:
            print("🎉 已复用登录状态，理论上无需重新登录！")
            print("📝 如果仍需登录，可能是因为网站安全策略或session过期")
        else:
            print("请在Chrome中登录Manus平台，然后使用以下命令执行任务:")
        
        print()
        print(f"python main.py manus-task \"你的命题内容\" --debug-port {port}")
        print()
        print("按 Ctrl+C 退出")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在关闭Chrome...")
            process.terminate()
            process.wait()
            print("Chrome已关闭")
        
        return True
        
    except Exception as e:
        print(f"启动Chrome失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="启动Chrome调试模式")
    parser.add_argument("--port", type=int, default=9222, help="调试端口")
    parser.add_argument("--user-data-dir", help="用户数据目录")
    parser.add_argument("--use-system-profile", action="store_true", 
                       help="使用系统Chrome配置（直接复用登录状态，可能影响正常Chrome使用）")
    parser.add_argument("--copy-profile", action="store_true",
                       help="复制系统Chrome配置到调试目录（推荐方式）")
    
    args = parser.parse_args()
    
    if args.use_system_profile and args.copy_profile:
        print("❌ --use-system-profile 和 --copy-profile 不能同时使用")
        sys.exit(1)
    
    start_chrome_debug_mode(
        port=args.port, 
        user_data_dir=args.user_data_dir,
        use_system_profile=args.use_system_profile,
        copy_profile=args.copy_profile
    ) 