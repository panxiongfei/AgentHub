#!/bin/bash
# =============================================================================
# AgentHub 开发环境自动设置脚本
# =============================================================================

set -e  # 出错时退出

echo "🚀 正在设置 AgentHub 开发环境..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的命令
check_requirements() {
    log_info "检查系统要求..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_warn "Node.js 未安装，前端功能可能无法使用"
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装，请先安装 Git"
        exit 1
    fi
    
    log_info "系统要求检查完成 ✅"
}

# 创建开发目录结构
create_dev_directories() {
    log_info "创建开发环境目录结构..."
    
    # 创建本地开发专用目录
    mkdir -p {
        data/local,
        data/dev,
        data/temp,
        data/cache,
        data/experiments,
        logs/local,
        screenshots/local,
        downloads/local,
        temp/local,
        experiments,
        local_scripts,
        sandbox
    }
    
    # 创建 .gitkeep 文件保持目录结构
    touch data/local/.gitkeep
    touch logs/local/.gitkeep
    touch screenshots/local/.gitkeep
    
    log_info "目录结构创建完成 ✅"
}

# 设置配置文件
setup_config_files() {
    log_info "设置配置文件..."
    
    # 复制配置模板
    if [ ! -f "configs/settings.local.yaml" ]; then
        if [ -f "configs/settings.local.yaml.sample" ]; then
            cp configs/settings.local.yaml.sample configs/settings.local.yaml
            log_info "已创建本地配置文件: configs/settings.local.yaml"
        else
            log_warn "配置模板文件不存在，请手动创建配置文件"
        fi
    else
        log_warn "本地配置文件已存在，跳过创建"
    fi
    
    # 创建环境变量文件
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# AgentHub 本地开发环境变量
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
API_PORT=8001
FRONTEND_PORT=3001
DEEPSEEK_API_KEY=your-api-key-here
SECRET_KEY=local-dev-secret-2024
CHROME_DEBUG_PORT=9223
BROWSER_HEADLESS=false
EOF
        log_info "已创建环境变量文件: .env"
        log_warn "请编辑 .env 文件并设置您的 API 密钥"
    else
        log_warn "环境变量文件已存在，跳过创建"
    fi
    
    log_info "配置文件设置完成 ✅"
}

# 设置 Python 虚拟环境
setup_python_env() {
    log_info "设置 Python 虚拟环境..."
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        log_info "已创建虚拟环境"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境并安装依赖
    source .venv/bin/activate
    
    log_info "安装 Python 依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 安装开发依赖
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    log_info "Python 环境设置完成 ✅"
}

# 设置前端环境
setup_frontend_env() {
    if [ -d "frontend" ] && command -v npm &> /dev/null; then
        log_info "设置前端环境..."
        
        cd frontend
        npm install
        cd ..
        
        log_info "前端环境设置完成 ✅"
    else
        log_warn "跳过前端环境设置（目录不存在或 npm 未安装）"
    fi
}

# 初始化数据库
init_database() {
    log_info "初始化开发数据库..."
    
    source .venv/bin/activate
    
    # 使用本地配置初始化数据库
    python main.py init --config configs/settings.local.yaml
    
    log_info "数据库初始化完成 ✅"
}

# 创建开发脚本
create_dev_scripts() {
    log_info "创建开发脚本..."
    
    # 本地服务启动脚本
    cat > local_scripts/start_services.sh << 'EOF'
#!/bin/bash
# 启动 AgentHub 本地开发服务

echo "🚀 启动 AgentHub 开发环境..."

# 启动后端服务
echo "启动后端服务..."
source .venv/bin/activate
python main.py serve --config configs/settings.local.yaml --port 8001 &
BACKEND_PID=$!

# 启动前端服务
if [ -d "frontend" ]; then
    echo "启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
fi

echo "✅ 服务已启动:"
echo "   后端: http://localhost:8001"
echo "   前端: http://localhost:3001"
echo "   PID: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"

# 等待用户中断
echo "按 Ctrl+C 停止所有服务..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
EOF

    # 本地测试脚本
    cat > local_scripts/run_tests.sh << 'EOF'
#!/bin/bash
# 运行本地测试

echo "🧪 运行 AgentHub 本地测试..."

source .venv/bin/activate

# 运行单元测试
echo "运行单元测试..."
python -m pytest tests/ -v

# 运行回归测试
echo "运行回归测试..."
python regression_test.py

echo "✅ 测试完成"
EOF

    # 开发工具脚本
    cat > local_scripts/dev_tools.sh << 'EOF'
#!/bin/bash
# 开发工具集合

case "$1" in
    "format")
        echo "🎨 格式化代码..."
        source .venv/bin/activate
        black app/ tests/
        ;;
    "lint")
        echo "🔍 代码检查..."
        source .venv/bin/activate
        flake8 app/ tests/
        mypy app/
        ;;
    "clean")
        echo "🧹 清理临时文件..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete
        rm -rf data/local/* logs/local/* temp/local/* 2>/dev/null || true
        ;;
    "reset")
        echo "🔄 重置开发环境..."
        rm -f data/autocall_local.db
        rm -rf logs/local/*
        python main.py init --config configs/settings.local.yaml
        ;;
    *)
        echo "使用方法: $0 {format|lint|clean|reset}"
        echo "  format - 格式化代码"
        echo "  lint   - 代码检查"
        echo "  clean  - 清理临时文件"
        echo "  reset  - 重置开发环境"
        ;;
esac
EOF

    # 设置可执行权限
    chmod +x local_scripts/*.sh
    
    log_info "开发脚本创建完成 ✅"
}

# 显示使用说明
show_usage() {
    log_info "🎉 开发环境设置完成！"
    echo ""
    echo "📚 快速开始:"
    echo "  1. 编辑配置文件: vim configs/settings.local.yaml"
    echo "  2. 设置 API 密钥: vim .env"
    echo "  3. 启动服务: ./local_scripts/start_services.sh"
    echo "  4. 运行测试: ./local_scripts/run_tests.sh"
    echo ""
    echo "🛠️  开发工具:"
    echo "  • 代码格式化: ./local_scripts/dev_tools.sh format"
    echo "  • 代码检查: ./local_scripts/dev_tools.sh lint"
    echo "  • 清理文件: ./local_scripts/dev_tools.sh clean"
    echo "  • 重置环境: ./local_scripts/dev_tools.sh reset"
    echo ""
    echo "📁 重要文件:"
    echo "  • 本地配置: configs/settings.local.yaml"
    echo "  • 环境变量: .env"
    echo "  • 开发脚本: local_scripts/"
    echo "  • 开发数据: data/local/"
    echo ""
    echo "⚠️  注意: 请确保在提交代码前运行 git status 检查，避免提交敏感文件"
}

# 主函数
main() {
    check_requirements
    create_dev_directories
    setup_config_files
    setup_python_env
    setup_frontend_env
    init_database
    create_dev_scripts
    show_usage
}

# 执行主函数
main "$@" 