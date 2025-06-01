#!/bin/bash

# AgentHub 回归测试运行脚本
# 支持手动运行和定时调度

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_ENV="$PROJECT_ROOT/.venv"
REGRESSION_SCRIPT="$PROJECT_ROOT/regression_test.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查Python虚拟环境
    if [ ! -d "$PYTHON_ENV" ]; then
        log_error "Python虚拟环境未找到: $PYTHON_ENV"
        exit 1
    fi
    
    # 检查回归测试脚本
    if [ ! -f "$REGRESSION_SCRIPT" ]; then
        log_error "回归测试脚本未找到: $REGRESSION_SCRIPT"
        exit 1
    fi
    
    log_success "环境检查完成"
}

# 检查服务状态
check_services() {
    log_info "检查必要服务状态..."
    
    # 检查API服务
    if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
        log_success "API服务正在运行"
    else
        log_warning "API服务未运行，正在启动..."
        cd "$PROJECT_ROOT"
        source "$PYTHON_ENV/bin/activate"
        python main.py serve &
        API_PID=$!
        sleep 5
        
        if curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
            log_success "API服务启动成功"
        else
            log_error "API服务启动失败"
            exit 1
        fi
    fi
    
    # 检查前端服务
    if curl -s -f "http://localhost:3001" > /dev/null 2>&1; then
        log_success "前端服务正在运行"
    else
        log_warning "前端服务未运行，请手动启动: cd frontend && npm run dev"
    fi
    
    # 检查Chrome调试会话
    if curl -s -f "http://localhost:9222/json" > /dev/null 2>&1; then
        log_success "Chrome调试会话可用"
    else
        log_warning "Chrome调试会话未启动，请手动启动: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --no-first-run --no-default-browser-check &"
    fi
}

# 运行回归测试
run_regression_test() {
    log_info "开始执行回归测试..."
    
    cd "$PROJECT_ROOT"
    source "$PYTHON_ENV/bin/activate"
    
    # 设置环境变量
    export MODEL_GEMINI_API_KEY="AIzaSyD7ybqMdeZV3m44AXxXiEsf6l-2KT9XvYo"
    
    # 运行测试
    python "$REGRESSION_SCRIPT"
    test_exit_code=$?
    
    # 处理测试结果
    case $test_exit_code in
        0)
            log_success "回归测试完成 - 系统状态良好"
            return 0
            ;;
        1)
            log_warning "回归测试完成 - 发现问题，需要关注"
            return 1
            ;;
        2)
            log_error "回归测试执行失败"
            return 2
            ;;
        *)
            log_error "回归测试异常退出，退出码: $test_exit_code"
            return $test_exit_code
            ;;
    esac
}

# 生成测试报告摘要
generate_summary() {
    log_info "生成测试报告摘要..."
    
    local latest_result="$PROJECT_ROOT/data/regression_tests/latest_result.json"
    
    if [ -f "$latest_result" ]; then
        local success_rate=$(python3 -c "
import json
with open('$latest_result') as f:
    data = json.load(f)
    print(f\"{data['summary']['success_rate']:.1%}\")
")
        
        local total_tests=$(python3 -c "
import json
with open('$latest_result') as f:
    data = json.load(f)
    print(data['summary']['total_tests'])
")
        
        local failed_tests=$(python3 -c "
import json
with open('$latest_result') as f:
    data = json.load(f)
    print(data['summary']['failed_tests'])
")
        
        echo "=================================="
        echo "📊 回归测试摘要报告"
        echo "=================================="
        echo "🕐 执行时间: $(date)"
        echo "📈 成功率: $success_rate"
        echo "📊 总测试数: $total_tests"
        echo "❌ 失败数: $failed_tests"
        echo "📁 详细报告: $latest_result"
        echo "=================================="
    else
        log_warning "测试结果文件未找到"
    fi
}

# 发送通知（可扩展）
send_notification() {
    local status="$1"
    local message="$2"
    
    # 这里可以添加邮件、Slack、企业微信等通知
    log_info "通知: $status - $message"
    
    # 示例：写入系统日志
    logger "AgentHub回归测试: $status - $message"
}

# 清理函数
cleanup() {
    log_info "清理临时资源..."
    
    # 如果启动了API服务，则关闭
    if [ ! -z "$API_PID" ]; then
        log_info "关闭API服务 (PID: $API_PID)"
        kill $API_PID 2>/dev/null || true
    fi
}

# 主函数
main() {
    local mode="${1:-manual}"
    
    echo "🚀 AgentHub 回归测试系统"
    echo "执行模式: $mode"
    echo "开始时间: $(date)"
    echo "=================================="
    
    # 设置清理函数
    trap cleanup EXIT
    
    # 执行测试流程
    check_environment
    check_services
    
    if run_regression_test; then
        generate_summary
        send_notification "SUCCESS" "回归测试成功完成"
        exit 0
    else
        local exit_code=$?
        generate_summary
        send_notification "FAILURE" "回归测试失败，退出码: $exit_code"
        exit $exit_code
    fi
}

# 帮助信息
show_help() {
    echo "AgentHub 回归测试运行脚本"
    echo ""
    echo "用法:"
    echo "  $0 [模式]"
    echo ""
    echo "模式:"
    echo "  manual     手动执行（默认）"
    echo "  scheduled  定时执行"
    echo "  ci         CI/CD执行"
    echo ""
    echo "示例:"
    echo "  $0                # 手动执行"
    echo "  $0 scheduled      # 定时执行"
    echo "  $0 ci             # CI/CD执行"
    echo ""
    echo "环境要求:"
    echo "  - Python虚拟环境: .venv"
    echo "  - API服务端口: 8000"
    echo "  - 前端服务端口: 3001"
    echo "  - Chrome调试端口: 9222"
}

# 参数解析
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    "")
        main manual
        ;;
    *)
        main "$1"
        ;;
esac 