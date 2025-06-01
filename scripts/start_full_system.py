#!/usr/bin/env python3
"""
AgentHub 完整系统启动脚本
自动启动后端服务、前端界面和浏览器实例
"""

import subprocess
import sys
import time
import requests
import signal
import os
from pathlib import Path

class SystemLauncher:
    """系统启动器"""
    
    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent.parent
        
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                      AgentHub v2.1                          ║
║            企业级多平台 AI 代理服务自动化平台                   ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 正在启动完整系统...                                       ║
║  📊 仪表盘: http://localhost:3000                             ║
║  🔧 API服务: http://localhost:8000                            ║
║  🌐 Skywork: http://localhost:9222                           ║
║  🌐 Manus: http://localhost:9223                             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_dependencies(self):
        """检查依赖项"""
        print("🔍 检查系统依赖...")
        
        # 检查Python环境
        if sys.version_info < (3, 8):
            print("❌ 需要 Python 3.8 或更高版本")
            return False
            
        # 检查Node.js
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ 需要安装 Node.js")
                return False
            print(f"✅ Node.js: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ 未找到 Node.js，请先安装")
            return False
            
        # 检查npm
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ 需要安装 npm")
                return False
            print(f"✅ npm: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ 未找到 npm，请先安装")
            return False
            
        # 检查Chrome
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_found = True
                print(f"✅ Chrome: {path}")
                break
                
        if not chrome_found:
            print("❌ 未找到 Chrome 浏览器，请先安装")
            return False
            
        print("✅ 所有依赖检查通过")
        return True
    
    def install_python_dependencies(self):
        """安装Python依赖"""
        print("📦 检查Python依赖...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️  未找到 requirements.txt，跳过Python依赖安装")
            return True
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, cwd=self.project_root)
            print("✅ Python依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Python依赖安装失败: {e}")
            return False
    
    def install_frontend_dependencies(self):
        """安装前端依赖"""
        print("📦 检查前端依赖...")
        
        frontend_dir = self.project_root / "frontend"
        package_json = frontend_dir / "package.json"
        node_modules = frontend_dir / "node_modules"
        
        if not package_json.exists():
            print("⚠️  未找到前端项目，跳过前端依赖安装")
            return True
            
        if node_modules.exists():
            print("✅ 前端依赖已存在")
            return True
            
        try:
            subprocess.run(["npm", "install"], check=True, cwd=frontend_dir)
            print("✅ 前端依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 前端依赖安装失败: {e}")
            return False
    
    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        
        try:
            # 检查main.py是否存在
            main_py = self.project_root / "main.py"
            if not main_py.exists():
                print("❌ 未找到 main.py，无法启动后端")
                return False
                
            # 启动FastAPI服务
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000", "--reload"
            ], cwd=self.project_root)
            
            self.processes['backend'] = process
            
            # 等待服务启动
            print("⏳ 等待后端服务启动...")
            max_attempts = 30
            for i in range(max_attempts):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ 后端服务启动成功")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
                
            print("❌ 后端服务启动超时")
            return False
            
        except Exception as e:
            print(f"❌ 后端服务启动失败: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        print("🌐 启动前端服务...")
        
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            print("⚠️  未找到前端项目，跳过前端启动")
            return True
            
        try:
            process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=frontend_dir)
            
            self.processes['frontend'] = process
            
            # 等待前端服务启动
            print("⏳ 等待前端服务启动...")
            max_attempts = 30
            for i in range(max_attempts):
                try:
                    response = requests.get("http://localhost:3000", timeout=1)
                    if response.status_code == 200:
                        print("✅ 前端服务启动成功")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
                
            print("⚠️  前端服务可能正在启动中...")
            return True
            
        except Exception as e:
            print(f"❌ 前端服务启动失败: {e}")
            return False
    
    def start_browsers(self):
        """启动浏览器实例"""
        print("🌐 启动浏览器实例...")
        
        script_path = self.project_root / "scripts" / "start_multi_chrome.py"
        if not script_path.exists():
            print("⚠️  未找到浏览器启动脚本，跳过浏览器启动")
            return True
            
        try:
            # 使用复制配置的方式启动浏览器
            process = subprocess.Popen([
                sys.executable, str(script_path), "--copy-profile"
            ], cwd=self.project_root)
            
            self.processes['browsers'] = process
            
            # 等待浏览器启动
            print("⏳ 等待浏览器实例启动...")
            time.sleep(5)  # 给浏览器一些启动时间
            
            # 检查浏览器是否可访问
            for platform, port in [("Skywork", 9222), ("Manus", 9223)]:
                try:
                    response = requests.get(f"http://localhost:{port}/json/version", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {platform} 浏览器启动成功 (端口:{port})")
                except requests.exceptions.RequestException:
                    print(f"⚠️  {platform} 浏览器可能正在启动中...")
                    
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return False
    
    def print_access_info(self):
        """打印访问信息"""
        info = """
╔══════════════════════════════════════════════════════════════╗
║                        🎉 启动完成！                          ║
╠══════════════════════════════════════════════════════════════╣
║  📊 前端管理界面: http://localhost:3000                       ║
║  🔧 后端API文档: http://localhost:8000/docs                   ║
║  🌐 Skywork调试: http://localhost:9222                       ║
║  🌐 Manus调试:   http://localhost:9223                       ║
╠══════════════════════════════════════════════════════════════╣
║  💡 使用提示:                                                ║
║  1. 打开浏览器访问管理界面                                    ║
║  2. 在浏览器管理页面检查浏览器状态                             ║
║  3. 如需登录，请在对应浏览器窗口中登录账号                     ║
║  4. 登录后即可使用历史下载等功能                               ║
╠══════════════════════════════════════════════════════════════╣
║  ⛔ 停止系统: 按 Ctrl+C                                      ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(info)
    
    def stop_all_processes(self):
        """停止所有进程"""
        print("\n🛑 正在停止所有服务...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"⏹️  停止 {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                except Exception as e:
                    print(f"⚠️  停止 {name} 时出错: {e}")
        
        print("✅ 所有服务已停止")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.stop_all_processes()
        sys.exit(0)
    
    def run(self):
        """运行完整系统"""
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_banner()
        
        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败，请解决后重试")
            return False
        
        # 安装依赖
        if not self.install_python_dependencies():
            print("❌ Python依赖安装失败")
            return False
            
        if not self.install_frontend_dependencies():
            print("❌ 前端依赖安装失败")
            return False
        
        # 启动服务
        if not self.start_backend():
            print("❌ 后端启动失败")
            return False
            
        if not self.start_frontend():
            print("❌ 前端启动失败")
            return False
            
        if not self.start_browsers():
            print("❌ 浏览器启动失败")
            return False
        
        # 打印访问信息
        self.print_access_info()
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                for name, process in list(self.processes.items()):
                    if process and process.poll() is not None:
                        print(f"⚠️  {name} 进程已退出")
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_processes()
        
        return True


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
AgentHub 完整系统启动脚本

用法:
    python scripts/start_full_system.py

功能:
    - 自动检查和安装依赖
    - 启动后端 FastAPI 服务 (端口 8000)
    - 启动前端 Vue.js 应用 (端口 3000)
    - 启动多平台浏览器实例 (端口 9222, 9223)
    - 提供统一的管理界面

访问地址:
    - 前端管理界面: http://localhost:3000
    - 后端API文档: http://localhost:8000/docs
    - Skywork调试端口: http://localhost:9222
    - Manus调试端口: http://localhost:9223

停止系统:
    按 Ctrl+C 或发送 SIGTERM 信号
        """)
        return
    
    launcher = SystemLauncher()
    success = launcher.run()
    
    if success:
        print("✅ 系统启动成功")
    else:
        print("❌ 系统启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 