#!/usr/bin/env python3
"""
快速启动脚本 - 复用登录状态版本
自动复用系统Chrome的登录状态，避免重复登录
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    """主函数 - 演示复用登录状态的使用方法"""
    
    print("🌟 AgentHub 快速启动 - 复用登录状态版本")
    print("=" * 60)
    print()
    
    # 显示使用选项
    print("📋 选择启动方式:")
    print("1. 复制系统Chrome配置（推荐）- 安全且不影响正常浏览器使用")
    print("2. 直接使用系统Chrome配置 - 可能影响正常浏览器使用")
    print("3. 传统方式 - 需要手动登录")
    print("4. 退出")
    print()
    
    while True:
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            # 复制系统配置方式（推荐）
            print("\n🎯 选择方式1: 复制系统Chrome配置")
            print("✅ 优点: 复用登录状态，不影响正常浏览器使用")
            print("⚠️  注意: 需要确保系统Chrome已登录相关平台")
            print()
            
            confirm = input("确认启动？(y/n): ").lower()
            if confirm == 'y':
                start_with_copy_profile()
            break
            
        elif choice == "2":
            # 直接使用系统配置
            print("\n🎯 选择方式2: 直接使用系统Chrome配置")
            print("✅ 优点: 完全复用登录状态")
            print("⚠️  警告: 可能影响您正常的Chrome浏览器使用")
            print()
            
            confirm = input("确认启动？(y/n): ").lower()
            if confirm == 'y':
                start_with_system_profile()
            break
            
        elif choice == "3":
            # 传统方式
            print("\n🎯 选择方式3: 传统方式")
            print("📝 需要: 手动在浏览器中登录各平台")
            print()
            
            confirm = input("确认启动？(y/n): ").lower()
            if confirm == 'y':
                start_traditional()
            break
            
        elif choice == "4":
            print("👋 退出")
            sys.exit(0)
            
        else:
            print("❌ 无效选择，请输入1-4")


def start_with_copy_profile():
    """启动方式1: 复制系统Chrome配置"""
    print("\n🚀 启动多Chrome实例（复制配置模式）...")
    
    try:
        # 启动多Chrome实例并复制配置
        cmd = [
            sys.executable, "scripts/start_multi_chrome.py",
            "--copy-profile"
        ]
        
        print("📋 正在复制系统Chrome配置...")
        print("⏳ 这可能需要几秒钟...")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")


def start_with_system_profile():
    """启动方式2: 直接使用系统Chrome配置"""
    print("\n🚀 启动多Chrome实例（系统配置模式）...")
    print("⚠️  警告: 这将直接使用您的系统Chrome配置")
    
    try:
        # 启动多Chrome实例并使用系统配置
        cmd = [
            sys.executable, "scripts/start_multi_chrome.py",
            "--use-system-profile"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")


def start_traditional():
    """启动方式3: 传统方式"""
    print("\n🚀 启动多Chrome实例（传统模式）...")
    
    try:
        # 启动多Chrome实例（传统方式）
        cmd = [sys.executable, "scripts/start_multi_chrome.py"]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 用户取消启动")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")


if __name__ == "__main__":
    main() 