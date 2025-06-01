# AgentHub - 多平台 AI 代理服务自动化平台

<div align="center">

![AgentHub Logo](https://img.shields.io/badge/AgentHub-v2.1.2-blue?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D?style=for-the-badge&logo=vue.js)](https://vuejs.org/)

**🚀 企业级多平台 AI 代理服务自动化平台**

*一个功能强大的 AI 平台统一入口，支持智能浏览器操作、任务自动化、AI增强分析、历史数据批量下载*

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [技术架构](#-技术架构) • [回归测试](#-回归测试系统) • [部署指南](docs/DEPLOYMENT.md) • [贡献指南](CONTRIBUTING.md)

</div>

## 📖 项目简介

AgentHub 是一个企业级的 AI 代理服务自动化平台，作为多个 AI 平台的统一入口和自动化枢纽。通过智能浏览器引擎和 AI 模型集成，实现与现有Chrome会话的无缝集成，避免重复登录，支持多平台任务自动化执行、AI增强分析和历史数据完整备份。

### 🎯 核心价值

- **🔗 统一入口**: 一个平台管理多个AI服务，统一界面，统一操作
- **🤖 AI增强自动化**: 基于大模型的智能浏览器引擎，自动分析页面结构和操作策略
- **🔄 免登录操作**: 连接现有Chrome会话，避免重复认证流程
- **📚 智能文件处理**: AI驱动的文件分析、预览生成、内容总结
- **📋 完整备份**: 自动保存任务结果、页面截图、HTML源码等完整数据
- **🎛️ 可视化管理**: Vue.js构建的现代化Web管理界面

## ✨ 功能特性

### 🧠 AI模型集成 (NEW)
- **多模型支持**: Google Gemini 2.5 Flash、OpenAI、Anthropic等
- **智能页面分析**: AI自动分析页面结构，识别最佳操作元素
- **智能文件处理**: 自动生成文件预览、摘要、分析报告
- **操作策略生成**: AI生成最优的浏览器操作策略
- **多模态分析**: 支持文本、图像的综合分析

### 🤖 智能浏览器引擎
- **Chrome会话集成**: 直接连接现有浏览器，免登录操作
- **AI驱动的页面分析**: 自动识别页面结构和交互元素
- **智能元素定位**: 多策略组合，置信度评分系统
- **自适应操作机制**: 智能输入、提交、等待、内容提取
- **完整容错恢复**: 网络异常、页面变化自动适应

### 📊 多平台支持
- **Manus平台**: 深度集成，支持研究分析、调研报告、知识挖掘
- **Skywork平台**: 智能对话、内容生成、深度分析
- **可扩展架构**: 插件化设计，快速接入新平台

### 📚 历史任务管理
- **智能任务发现**: 自动识别平台历史任务，支持多种页面结构
- **批量下载处理**: 一键下载所有历史对话和结果文件
- **AI增强分析**: 自动生成任务摘要、分析报告、文件预览
- **完整数据备份**: 文本、截图、HTML、附件、元数据全覆盖
- **详细下载报告**: 成功率统计、错误分析、文件清单

### 🔧 回归测试系统 (NEW)
- **全面测试覆盖**: 后台服务、前台应用、AI功能、浏览器操作
- **自动扩展检测**: 新功能自动添加对应测试项
- **定时健康检查**: 定期执行，确保系统稳定运行
- **详细测试报告**: JSON格式报告，成功率统计，失败分析

### 🎛️ Web管理界面
- **系统概览**: 实时状态监控、平台连接状态、AI模型状态
- **平台管理**: 支持的平台列表和配置
- **任务管理**: 任务创建和状态查看，AI增强分析
- **系统监控**: 资源使用情况、性能指标、测试结果
- **系统日志**: 运行日志查看和分析

## 🏗️ 技术架构

### 核心技术栈
- **前端**: Vue.js 3 + Element Plus + Pinia + Vue Router
- **后端**: FastAPI + SQLAlchemy + Structlog + APScheduler
- **AI集成**: Google Gemini 2.5 Flash + 多提供商支持
- **浏览器自动化**: Playwright + Chrome DevTools Protocol
- **数据存储**: SQLite + SQLAlchemy
- **任务调度**: APScheduler
- **测试框架**: pytest + 自定义回归测试系统
- **日志系统**: Structlog (结构化日志)

### 架构设计
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js 前端   │    │  FastAPI 后端   │    │  Chrome 浏览器  │
│                 │    │                 │    │                 │
│ • 管理界面      │◄──►│ • RESTful API   │◄──►│ • 调试模式      │
│ • 状态监控      │    │ • 任务调度      │    │ • 现有会话      │
│ • 配置管理      │    │ • 数据存储      │    │ • 平台操作      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  AI增强引擎     │
                    │                 │
                    │ • 智能页面分析  │◄──► Google Gemini
                    │ • 元素定位      │     OpenAI, etc.
                    │ • 操作执行      │
                    │ • 文件分析      │
                    │ • 结果总结      │
                    └─────────────────┘
```

## 🚀 快速开始

### 📋 环境要求
- **Python 3.9+**
- **Node.js 18+**
- **Chrome浏览器** (用于调试模式)
- **AI模型API密钥** (Google Gemini等)

### 📦 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/AgentHub.git
   cd AgentHub
   ```

2. **后端环境设置**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

3. **前端环境设置**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **配置AI模型**
   ```bash
   # 设置环境变量
   export MODEL_GEMINI_API_KEY="your_gemini_api_key"
   # 或编辑 configs/settings.yaml
   ```

5. **初始化项目**
   ```bash
   python main.py init
   ```

### 🎮 使用方式

#### 方式一：Web管理界面（推荐）

1. **启动后端服务**
   ```bash
   python main.py serve
   ```

2. **启动前端开发服务**（开发模式）
   ```bash
   cd frontend
   npm run dev
   ```

3. **访问管理界面**
   - 前端界面: http://localhost:3001
   - 后端API: http://localhost:8000/docs

#### 方式二：命令行工具

```bash
# 查看系统状态
python main.py status

# 运行回归测试
python regression_test.py
# 或使用包装脚本
./scripts/run_regression_test.sh

# 测试AI模型功能
python test_model_client.py

# 测试AI增强浏览器引擎
python test_ai_browser_engine.py

# 启动Chrome调试模式（需要手动操作）
# 然后执行Manus任务
python main.py manus-task "AI技术发展趋势研究"

# 批量下载历史任务
python main.py download-history --platform manus
```

## 🔧 回归测试系统

### 快速测试
```bash
# 运行完整回归测试
python regression_test.py

# 使用包装脚本（推荐）
./scripts/run_regression_test.sh

# 查看测试配置
cat configs/regression_test_config.yaml

# 查看测试结果
ls data/regression_tests/
```

### 测试覆盖范围
- ✅ **后台测试**: 服务启动、AI模型调用、API端点、浏览器任务、历史数据
- ✅ **前台测试**: 应用访问、页面导航、系统状态、历史显示
- ✅ **自动扩展**: 新功能自动添加测试覆盖
- ✅ **定时执行**: 每天8点和20点自动运行

详细文档: [回归测试系统](docs/regression_testing.md)

## 📚 使用指南

### 🔧 Chrome调试模式设置

在使用浏览器自动化功能前，需要启动Chrome调试模式：

**macOS/Linux:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --no-first-run --no-default-browser-check &
```

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

### 📋 基本工作流程

1. **设置AI模型API密钥**
2. **启动Chrome调试模式**并登录目标平台
3. **启动AgentHub服务**
4. **运行回归测试确保系统正常**
5. **通过Web界面或CLI执行任务**
6. **查看AI增强的分析结果和下载文件**

### 🎯 支持的操作

- ✅ AI驱动的页面结构分析
- ✅ 智能元素定位和操作
- ✅ 自动输入研究命题
- ✅ 智能提交任务
- ✅ 等待任务完成
- ✅ AI增强的内容提取和总结
- ✅ 下载相关文件并生成预览
- ✅ 保存页面截图
- ✅ 备份HTML源码

## 📁 项目结构

```
AgentHub/
├── app/                    # 应用核心
│   ├── api/               # Web API
│   ├── core/              # 核心业务逻辑
│   │   ├── model_client.py        # AI模型客户端
│   │   ├── browser_engine.py      # AI增强浏览器引擎
│   │   ├── ai_file_processor.py   # AI文件处理器
│   │   └── chrome_connector.py    # Chrome连接模块
│   ├── platforms/         # 平台适配器
│   ├── scheduler/         # 任务调度
│   ├── storage/           # 数据存储
│   ├── config/            # 配置管理
│   └── utils/             # 工具函数
├── frontend/              # Vue.js 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   ├── stores/        # 状态管理
│   │   └── router/        # 路由配置
│   └── package.json
├── tests/                 # 测试用例
├── docs/                  # 项目文档
│   └── regression_testing.md     # 回归测试文档
├── scripts/               # 工具脚本
│   └── run_regression_test.sh    # 回归测试脚本
├── configs/               # 配置文件
│   └── regression_test_config.yaml  # 回归测试配置
├── regression_test.py     # 主回归测试脚本
├── test_*.py             # 功能测试脚本
└── requirements.txt       # Python依赖
```

## 🔧 配置说明

### 环境变量
创建 `.env` 文件：
```env
DEBUG=false
LOG_LEVEL=info
CHROME_DEBUG_PORT=9222

# AI模型配置
MODEL_GEMINI_API_KEY=your_gemini_api_key
MODEL_OPENAI_API_KEY=your_openai_api_key
MODEL_ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 配置文件
编辑 `configs/settings.yaml`：
```yaml
app:
  name: "AgentHub"
  version: "2.1.2"
  debug: false
  log_level: "info"

# AI模型配置
model:
  default_provider: "gemini"
  default_model: "gemini-2.0-flash-exp"
  gemini:
    api_key: "${MODEL_GEMINI_API_KEY}"
    model: "gemini-2.0-flash-exp"
  openai:
    api_key: "${MODEL_OPENAI_API_KEY}"
    model: "gpt-4"

platforms:
  manus:
    enabled: true
    base_url: "https://manus.chat"
  
  skywork:
    enabled: true
    base_url: "https://skywork.metaso.cn"
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

### 开发流程
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. **运行回归测试** (`python regression_test.py`)
4. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 创建 Pull Request

### 代码规范
- Python: 遵循 PEP 8，使用 black 格式化
- JavaScript/Vue: 使用 ESLint + Prettier
- 添加类型注解和文档字符串
- 编写单元测试
- **每次代码变更后必须运行回归测试**

## 📊 质量保证

### 测试覆盖
- ✅ 单元测试覆盖率 > 85%
- ✅ 回归测试覆盖率 100%
- ✅ AI功能专项测试
- ✅ 浏览器操作测试
- ✅ 端到端集成测试

### 持续监控
- 🔄 定时回归测试
- 📊 性能指标监控
- 🚨 异常告警机制
- 📈 成功率统计

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 🙏 致谢

- [Google Gemini](https://ai.google.dev/) - 强大的多模态AI模型
- [Playwright](https://playwright.dev/) - 现代化浏览器自动化
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Element Plus](https://element-plus.org/) - Vue 3组件库

## 📞 支持与反馈

- 🐛 [报告问题](../../issues)
- 💡 [功能建议](../../issues)
- 📖 [查看文档](docs/)
- 💬 [参与讨论](../../discussions)
- 🧪 [回归测试文档](docs/regression_testing.md)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

Made with ❤️ by AgentHub Team

</div> 