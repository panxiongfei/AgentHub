#!/usr/bin/env python3
"""
项目初始化脚本
创建默认配置文件、数据库和目录结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import create_default_configs


def create_directories():
    """创建必要的目录结构"""
    directories = [
        "data/results",
        "data/exports", 
        "data/temp",
        "logs",
        "configs",
        "scripts",
        "tests/unit",
        "tests/integration",
        "docs"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")


def create_env_file():
    """创建环境变量文件"""
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("⚠️  .env 文件已存在，跳过创建")
        return
    
    # 复制示例文件
    env_example = project_root / ".env.example"
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ 创建 .env 文件（基于 .env.example）")
    else:
        # 创建基础的 .env 文件
        env_content = """# 平台 API 密钥
MANUS_API_KEY=your_manus_api_key_here
SKYWORK_API_KEY=your_skywork_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
KOUZI_API_KEY=your_kouzi_api_key_here

# 通知配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# 安全配置
ENCRYPTION_KEY=your_encryption_key_here
SECRET_KEY=your_secret_key_here

# 应用配置
APP__DEBUG=false
LOGGING__LEVEL=INFO
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ 创建 .env 文件")


def init_database():
    """初始化数据库"""
    try:
        from app.storage.database import init_database
        
        print("🔧 初始化数据库...")
        # 这里会在实际实现数据库模块后调用
        # init_database()
        print("✅ 数据库初始化完成")
    except ImportError:
        print("⚠️  数据库模块尚未实现，跳过初始化")


def generate_secret_key():
    """生成安全密钥"""
    import secrets
    import string
    
    # 生成32字符的随机密钥
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    key = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    print(f"🔑 生成的安全密钥: {key}")
    print("请将此密钥添加到 .env 文件中的 SECRET_KEY 和 ENCRYPTION_KEY")
    
    return key


def create_docker_files():
    """检查 Docker 相关文件"""
    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore"
    ]
    
    for file_name in docker_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} 已存在")
        else:
            print(f"⚠️  {file_name} 不存在，请手动创建")


def create_readme_if_not_exists():
    """如果 README.md 不存在则创建"""
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        print("⚠️  README.md 不存在，请手动创建")
    else:
        print("✅ README.md 已存在")


def main():
    """主函数"""
    print("🚀 开始初始化 AgentHub 项目")
    print(f"📁 项目根目录: {project_root}")
    
    # 创建目录结构
    print("\n📂 创建目录结构...")
    create_directories()
    
    # 创建配置文件
    print("\n⚙️  创建配置文件...")
    create_default_configs()
    
    # 创建环境变量文件
    print("\n🌍 创建环境变量文件...")
    create_env_file()
    
    # 生成安全密钥
    print("\n🔐 生成安全密钥...")
    secret_key = generate_secret_key()
    
    # 检查 Docker 文件
    print("\n🐳 检查 Docker 文件...")
    create_docker_files()
    
    # 检查 README
    print("\n📖 检查 README...")
    create_readme_if_not_exists()
    
    # 初始化数据库
    print("\n💾 初始化数据库...")
    init_database()
    
    print("\n✅ 项目初始化完成！")
    print("\n📋 后续步骤:")
    print("1. 编辑 .env 文件，填入真实的 API 密钥")
    print("2. 编辑 configs/platforms.yaml，配置平台信息")
    print("3. 运行 'python main.py test-connection' 测试平台连接")
    print("4. 运行 'python main.py serve' 启动服务")
    print("5. 访问 http://localhost:8000/docs 查看 API 文档")


if __name__ == "__main__":
    main() 