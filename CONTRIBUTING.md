# 贡献指南

感谢您对 AgentHub 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
- 使用 [Issues](../../issues) 报告 bug 或建议新功能
- 搜索现有 issues 避免重复
- 提供详细的问题描述和复现步骤

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📋 开发规范

### 代码风格
- Python: 遵循 PEP 8，使用 black 格式化
- JavaScript/Vue: 使用 ESLint + Prettier
- 添加类型注解和文档字符串
- 编写单元测试

### 提交信息格式
```
feat: 添加新功能
fix: 修复问题  
docs: 更新文档
style: 代码格式化
refactor: 重构代码
test: 添加测试
chore: 更新构建脚本
```

### 分支命名
- `feature/功能描述` - 新功能
- `fix/问题描述` - 修复问题
- `docs/文档描述` - 文档更新

## 🧪 测试

运行测试前请安装依赖：
```bash
pip install -r requirements.txt
cd frontend && npm install
```

运行测试：
```bash
# 后端测试
pytest

# 前端测试
cd frontend && npm run test
```

## 📞 联系方式

如有问题，请通过以下方式联系：
- 创建 [Issue](../../issues)
- 发起 [Discussion](../../discussions)

再次感谢您的贡献！ 🎉 