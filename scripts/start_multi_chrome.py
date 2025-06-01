#!/usr/bin/env python3
"""
启动多个Chrome浏览器调试实例的脚本
用于同时管理多个平台的浏览器
"""

import subprocess
import sys
import time
import threading
import shutil
from pathlib import Path
from typing import Dict, List


class MultiChromeManager:
    """多Chrome实例管理器"""
    
    def __init__(self, use_system_profile=False, copy_profile=False):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.use_system_profile = use_system_profile
        self.copy_profile = copy_profile
        self.platform_configs = {
            "skywork": {
                "port": 9222,
                "url": "https://skywork.ai",
                "user_data_dir": "chrome_skywork_data"
            },
            "manus": {
                "port": 9223,
                "url": "https://manus.ai",
                "user_data_dir": "chrome_manus_data"
            }
        }
    
    def get_chrome_path(self) -> str:
        """获取Chrome浏览器路径"""
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
            raise Exception(f"不支持的操作系统: {system}")
        
        # 查找可用的Chrome路径
        for path in chrome_paths:
            if Path(path).exists():
                return path
        
        raise Exception(f"未找到Chrome浏览器，请确保Chrome已安装")
    
    def get_system_chrome_profile(self):
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
    
    def copy_chrome_profile(self, source_dir: Path, target_dir: Path, platform: str):
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
                        print(f"✅ {platform}: 已复制目录 {item}")
                    else:
                        shutil.copy2(source_item, target_item)
                        print(f"✅ {platform}: 已复制文件 {item}")
                else:
                    print(f"⚠️  {platform}: 未找到 {item}")
            
            print(f"🎉 {platform}: Chrome配置复制完成，登录状态已保留！")
            return True
            
        except Exception as e:
            print(f"❌ {platform}: 复制Chrome配置失败: {e}")
            return False
    
    def start_chrome_instance(self, platform: str, config: dict) -> bool:
        """启动单个Chrome实例"""
        try:
            chrome_path = self.get_chrome_path()
            port = config["port"]
            url = config["url"]
            user_data_dir = str(Path.home() / config["user_data_dir"])
            
            # 处理登录状态复用
            if self.use_system_profile:
                # 使用系统Chrome配置（直接复用登录状态）
                system_profile = self.get_system_chrome_profile()
                if system_profile and system_profile.exists():
                    user_data_dir = str(system_profile)
                    print(f"🔄 {platform}: 使用系统Chrome配置（直接复用登录状态）")
                else:
                    print(f"⚠️  {platform}: 未找到系统Chrome配置，使用独立配置")
            
            elif self.copy_profile:
                # 复制系统配置到调试目录
                system_profile = self.get_system_chrome_profile()
                if system_profile:
                    print(f"📋 {platform}: 复制系统Chrome配置...")
                    success = self.copy_chrome_profile(system_profile, Path(user_data_dir), platform)
                    if not success:
                        print(f"⚠️  {platform}: 配置复制失败，将使用空白配置")
                else:
                    print(f"⚠️  {platform}: 未找到系统Chrome配置")
            
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
            if not self.use_system_profile:
                cmd.extend([
                    "--no-default-browser-check",
                    "--disable-extensions"
                ])
            
            cmd.append(url)
            
            print(f"🚀 启动 {platform.upper()} Chrome实例...")
            print(f"   端口: {port}")
            print(f"   URL: {url}")
            print(f"   用户数据目录: {user_data_dir}")
            
            # 启动Chrome进程
            process = subprocess.Popen(cmd)
            self.processes[platform] = process
            
            print(f"✅ {platform.upper()} Chrome进程已启动 (PID: {process.pid})")
            print(f"   调试地址: http://localhost:{port}")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动 {platform.upper()} Chrome实例失败: {e}")
            return False
    
    def start_all_instances(self) -> bool:
        """启动所有Chrome实例"""
        print("🌟 开始启动多Chrome实例管理器...")
        print("=" * 60)
        
        success_count = 0
        
        for platform, config in self.platform_configs.items():
            if self.start_chrome_instance(platform, config):
                success_count += 1
                time.sleep(2)  # 给每个实例一点启动时间
            print()
        
        if success_count == len(self.platform_configs):
            print("🎉 所有Chrome实例启动成功！")
            print("=" * 60)
            print()
            print("📋 使用说明:")
            
            if self.use_system_profile or self.copy_profile:
                print("🎉 已复用登录状态，理论上无需重新登录！")
                print("📝 如果某些平台仍需登录，可能是因为安全策略或session过期")
                print()
                print("1. 检查两个Chrome窗口的登录状态:")
            else:
                print("1. 请分别在两个Chrome窗口中登录对应平台:")
            
            print(f"   - Skywork: http://localhost:{self.platform_configs['skywork']['port']}")
            print(f"   - Manus:   http://localhost:{self.platform_configs['manus']['port']}")
            print()
            print("2. 登录完成后，使用以下命令进行多平台历史下载:")
            print("   python main.py download-multi-history")
            print()
            print("3. 或者预览所有平台的历史任务:")
            print("   python main.py list-multi-history")
            print()
            print("按 Ctrl+C 退出并关闭所有Chrome实例")
            return True
        else:
            print(f"⚠️  部分Chrome实例启动失败 ({success_count}/{len(self.platform_configs)})")
            return False
    
    def monitor_processes(self):
        """监控Chrome进程状态"""
        while True:
            try:
                time.sleep(5)
                
                # 检查进程状态
                dead_processes = []
                for platform, process in self.processes.items():
                    if process.poll() is not None:
                        dead_processes.append(platform)
                
                # 移除已死亡的进程
                for platform in dead_processes:
                    print(f"⚠️  {platform.upper()} Chrome进程已退出")
                    del self.processes[platform]
                
                # 如果所有进程都死亡了，退出监控
                if not self.processes:
                    print("所有Chrome进程已退出")
                    break
                    
            except KeyboardInterrupt:
                break
    
    def cleanup(self):
        """清理所有Chrome进程"""
        print("\n🧹 正在关闭所有Chrome实例...")
        
        for platform, process in self.processes.items():
            try:
                print(f"   关闭 {platform.upper()} Chrome进程 (PID: {process.pid})")
                process.terminate()
                
                # 等待进程结束，超时后强制杀死
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"   强制杀死 {platform.upper()} Chrome进程")
                    process.kill()
                    process.wait()
                    
            except Exception as e:
                print(f"   关闭 {platform.upper()} Chrome进程失败: {e}")
        
        self.processes.clear()
        print("✅ 所有Chrome实例已关闭")
    
    def run(self):
        """运行多Chrome管理器"""
        try:
            # 启动所有实例
            if not self.start_all_instances():
                return False
            
            # 监控进程状态
            self.monitor_processes()
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="启动多个Chrome调试实例")
    parser.add_argument("--skywork-port", type=int, default=9222, help="Skywork Chrome调试端口")
    parser.add_argument("--manus-port", type=int, default=9223, help="Manus Chrome调试端口")
    parser.add_argument("--use-system-profile", action="store_true", 
                       help="使用系统Chrome配置（直接复用登录状态，可能影响正常Chrome使用）")
    parser.add_argument("--copy-profile", action="store_true",
                       help="复制系统Chrome配置到调试目录（推荐方式，复用登录状态）")
    
    args = parser.parse_args()
    
    if args.use_system_profile and args.copy_profile:
        print("❌ --use-system-profile 和 --copy-profile 不能同时使用")
        sys.exit(1)
    
    # 创建管理器并自定义端口
    manager = MultiChromeManager(
        use_system_profile=args.use_system_profile,
        copy_profile=args.copy_profile
    )
    manager.platform_configs["skywork"]["port"] = args.skywork_port
    manager.platform_configs["manus"]["port"] = args.manus_port
    
    # 运行管理器
    success = manager.run()
    
    if success:
        print("👋 多Chrome管理器已退出")
    else:
        print("❌ 多Chrome管理器启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 