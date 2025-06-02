#!/bin/bash
# =============================================================================
# AgentHub GitHub 发布准备脚本
# =============================================================================

set -e  # 出错时退出

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

log_milestone() {
    echo -e "${BLUE}[MILESTONE]${NC} $1"
}

# 检查Git状态
check_git_status() {
    log_info "检查Git状态..."
    
    if [ ! -d ".git" ]; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_warn "检测到未提交的更改，请先提交或暂存更改"
        git status --porcelain
        echo ""
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "Git状态检查完成 ✅"
}

# 安全检查 - 扫描敏感信息
security_scan() {
    log_info "执行安全扫描，检查敏感信息..."
    
    local has_issues=false
    
    # 检查API密钥模式
    local api_key_patterns=(
        "sk-[a-zA-Z0-9]{32,}"
        "AIza[a-zA-Z0-9]{35}"
        "AKIA[a-zA-Z0-9]{16}"
        "[a-zA-Z0-9]{32,}"
    )
    
    for pattern in "${api_key_patterns[@]}"; do
        if git ls-files | xargs grep -l "$pattern" 2>/dev/null | grep -v ".gitignore\|prepare_release.sh\|dev_env_setup.sh"; then
            log_error "发现可能的API密钥: $pattern"
            has_issues=true
        fi
    done
    
    # 检查敏感文件
    local sensitive_files=(
        ".env"
        "configs/settings.yaml"
        "configs/*.secret.*"
        "configs/*.local.*"
        "*_private*"
        "*_secret*"
    )
    
    for file_pattern in "${sensitive_files[@]}"; do
        if git ls-files | grep -q "$file_pattern" 2>/dev/null; then
            log_error "敏感文件可能被追踪: $file_pattern"
            has_issues=true
        fi
    done
    
    if [ "$has_issues" = true ]; then
        log_error "发现安全问题，请修复后重试"
        exit 1
    fi
    
    log_info "安全扫描通过 ✅"
}

# 清理开发文件
cleanup_dev_files() {
    log_info "清理开发环境文件..."
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    
    # 清理临时文件
    rm -rf temp/* tmp/* 2>/dev/null || true
    rm -rf data/local/* data/temp/* data/cache/* 2>/dev/null || true
    rm -rf logs/local/* 2>/dev/null || true
    rm -rf screenshots/local/* 2>/dev/null || true
    
    # 清理IDE文件
    rm -rf .vscode/settings.json .vscode/launch.json 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true
    
    # 清理前端构建缓存
    if [ -d "frontend" ]; then
        rm -rf frontend/.vite frontend/dist frontend/node_modules/.cache 2>/dev/null || true
    fi
    
    log_info "开发文件清理完成 ✅"
}

# 验证配置模板
verify_config_templates() {
    log_info "验证配置模板文件..."
    
    local required_templates=(
        "configs/settings.yaml.sample"
        "configs/settings.local.yaml.sample"
    )
    
    for template in "${required_templates[@]}"; do
        if [ ! -f "$template" ]; then
            log_error "缺少配置模板: $template"
            exit 1
        fi
        
        # 检查模板中是否包含占位符
        if grep -q "your-.*-key-here\|placeholder\|example" "$template"; then
            log_info "配置模板验证通过: $template"
        else
            log_warn "配置模板可能包含真实密钥: $template"
        fi
    done
    
    log_info "配置模板验证完成 ✅"
}

# 更新文档
update_documentation() {
    log_info "更新文档..."
    
    # 更新README中的版本信息
    if [ -f "README.md" ]; then
        # 获取当前版本
        local version=$(grep -o 'version.*[0-9]\+\.[0-9]\+\.[0-9]\+' configs/settings.yaml.sample | head -1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "2.1.2")
        log_info "当前版本: $version"
    fi
    
    # 检查CHANGELOG是否为最新
    if [ -f "CHANGELOG.md" ]; then
        local last_change=$(head -20 CHANGELOG.md | grep -o "[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" | head -1)
        local today=$(date +%Y-%m-%d)
        
        if [ "$last_change" != "$today" ]; then
            log_warn "CHANGELOG.md 可能需要更新（最后更新: $last_change）"
        fi
    fi
    
    log_info "文档检查完成 ✅"
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."
    
    # 激活虚拟环境
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # 运行回归测试
    if [ -f "regression_test.py" ]; then
        log_info "运行回归测试..."
        if ! python regression_test.py; then
            log_error "回归测试失败"
            exit 1
        fi
    fi
    
    # 运行单元测试（如果存在）
    if [ -d "tests" ]; then
        log_info "运行单元测试..."
        if ! python -m pytest tests/ -v --tb=short; then
            log_error "单元测试失败"
            exit 1
        fi
    fi
    
    log_info "测试完成 ✅"
}

# 创建发布信息
create_release_info() {
    local version=${1:-"$(date +%Y%m%d)"}
    local tag="v$version"
    
    log_milestone "准备创建发布版本: $tag"
    
    # 创建发布说明
    cat > RELEASE_NOTES.md << EOF
# AgentHub Release $tag

## 🎉 发布信息
- 发布日期: $(date +%Y-%m-%d)
- 版本号: $version
- 提交: $(git rev-parse --short HEAD)

## 📋 主要特性
- 多平台AI代理自动化 (Manus, Skywork, Coze Space)
- 浏览器自动化和会话管理
- Web管理界面
- 完整的配置管理系统
- 安全的密钥管理

## 🚀 快速开始
1. 克隆仓库: \`git clone https://github.com/panxiongfei/AgentHub.git\`
2. 设置环境: \`bash scripts/dev_env_setup.sh\`
3. 配置密钥: 编辑 \`.env\` 文件
4. 启动服务: \`./local_scripts/start_services.sh\`

## 📁 重要文件
- 配置模板: \`configs/settings.yaml.sample\`
- 开发环境: \`configs/settings.local.yaml.sample\`
- 设置脚本: \`scripts/dev_env_setup.sh\`
- 发布脚本: \`scripts/prepare_release.sh\`

## ⚠️ 安全提醒
- 请勿提交包含真实API密钥的配置文件
- 使用 \`.env\` 文件管理本地密钥
- 生产部署前请修改默认密钥

EOF

    log_info "发布说明已创建: RELEASE_NOTES.md"
}

# 显示发布清单
show_release_checklist() {
    echo ""
    log_milestone "📋 发布前检查清单"
    echo ""
    echo "✅ Git状态检查"
    echo "✅ 安全扫描通过"
    echo "✅ 开发文件清理"
    echo "✅ 配置模板验证"
    echo "✅ 文档检查"
    echo "✅ 测试套件通过"
    echo ""
    echo "📦 准备提交的文件:"
    git ls-files | grep -E '\.(py|md|yaml|json|txt|sh|js|vue|html|css)$' | head -20
    echo "... (更多文件)"
    echo ""
    echo "🚫 被忽略的敏感文件:"
    echo "  • .env"
    echo "  • configs/settings.yaml"
    echo "  • data/local/*"
    echo "  • logs/*"
    echo "  • local_scripts/*"
    echo ""
}

# 主函数
main() {
    local version=${1:-""}
    
    echo "🚀 开始准备 AgentHub GitHub 发布..."
    echo ""
    
    check_git_status
    security_scan
    cleanup_dev_files
    verify_config_templates
    update_documentation
    run_tests
    
    if [ -n "$version" ]; then
        create_release_info "$version"
    fi
    
    show_release_checklist
    
    echo ""
    log_milestone "🎉 发布准备完成！"
    echo ""
    echo "📝 下一步操作:"
    echo "  1. 检查 git status 确认要提交的文件"
    echo "  2. 提交更改: git add . && git commit -m 'feat: milestone release'"
    echo "  3. 创建标签: git tag v$version"
    echo "  4. 推送到GitHub: git push origin main --tags"
    echo ""
    echo "🔗 GitHub仓库: https://github.com/panxiongfei/AgentHub"
}

# 显示使用说明
usage() {
    echo "用法: $0 [版本号]"
    echo ""
    echo "示例:"
    echo "  $0           # 使用当前日期作为版本号"
    echo "  $0 2.2.0     # 使用指定版本号"
    echo ""
    echo "此脚本会:"
    echo "  • 检查Git状态和安全性"
    echo "  • 清理开发环境文件"
    echo "  • 验证配置模板"
    echo "  • 运行测试套件"
    echo "  • 准备发布文档"
}

# 处理命令行参数
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 