#!/bin/bash

# AgentHub 发布准备脚本
# 用于在发布前进行所有必要的检查和清理

set -e

echo "🚀 AgentHub 发布准备脚本"
echo "========================"

# 检查是否在正确的目录
if [ ! -f "main.py" ] || [ ! -d "app" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 步骤 1: 清理临时文件和缓存"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
echo "✅ 临时文件清理完成"

echo "📋 步骤 2: 清理前端构建产物"
if [ -d "frontend" ]; then
    cd frontend
    rm -rf node_modules dist .vite coverage 2>/dev/null || true
    cd ..
fi
echo "✅ 前端清理完成"

echo "📋 步骤 3: 检查敏感信息"
if grep -r "sk-[a-zA-Z0-9]\{32,\}" configs/ --include="*.yaml" --include="*.yml" 2>/dev/null; then
    echo "❌ 错误: 配置文件中发现API密钥，请清理后再发布"
    exit 1
fi
if grep -r "password.*:.*[^n][^u][^l][^l]" configs/ --include="*.yaml" --include="*.yml" | grep -v "your-.*-password" 2>/dev/null; then
    echo "❌ 错误: 配置文件中发现密码，请清理后再发布"
    exit 1
fi
echo "✅ 敏感信息检查通过"

echo "📋 步骤 4: 检查必要文件"
required_files=("README.md" "LICENSE" "requirements.txt" ".gitignore" "CONTRIBUTING.md")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 缺少必要文件: $file"
        exit 1
    fi
done
echo "✅ 必要文件检查通过"

echo "📋 步骤 5: 生成项目统计信息"
echo "项目文件统计:"
python_files=$(find . -name "*.py" -not -path "./.*" -not -path "./dev_scripts/*" | wc -l)
vue_files=$(find frontend -name "*.vue" 2>/dev/null | wc -l)
config_files=$(find configs -name "*.yaml" -o -name "*.yml" 2>/dev/null | wc -l)
doc_files=$(find docs -name "*.md" 2>/dev/null | wc -l)
echo "- Python文件: $python_files"
echo "- Vue文件: $vue_files"
echo "- 配置文件: $config_files"
echo "- 文档文件: $doc_files"

echo "📋 步骤 6: 检查Git状态"
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Git工作目录不干净，有未提交的更改:"
        git status --short
    else
        echo "✅ Git工作目录干净"
    fi
else
    echo "⚠️  这不是一个Git仓库"
fi

echo ""
echo "🎉 发布准备完成！"
echo ""
echo "📝 发布前检查清单:"
echo "[ ] 版本号已更新 (main.py, package.json)"
echo "[ ] CHANGELOG.md 已更新"
echo "[ ] 所有测试通过 (python regression_test.py)"
echo "[ ] 文档已更新"
echo "[ ] 敏感信息已清理"
echo "[ ] 代码已提交到Git"
echo ""
echo "🚀 准备就绪，可以推送到GitHub!"
echo "   git add ."
echo "   git commit -m 'chore: prepare for release'"
echo "   git push origin main" 