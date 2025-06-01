# Skywork平台使用指南

## 概述

Skywork平台集成模块支持通过浏览器自动化技术连接现有Chrome浏览器实例，自动输入命题、执行任务并获取结果。即使任务因各种原因中断，系统也会尝试获取中间产物。

## 前置条件

### 1. 环境准备
- 已安装Python 3.8+
- 已安装Playwright：`pip install playwright`
- 已安装Chromium：`playwright install chromium`

### 2. Chrome浏览器设置
需要在调试模式下启动Chrome浏览器才能进行自动化控制。

## 快速开始

### 1. 启动Chrome调试模式

使用项目提供的启动脚本：

```bash
python scripts/start_chrome_debug.py
```

或手动启动（macOS示例）：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="/Users/$(whoami)/chrome_debug_data" \
  --disable-web-security \
  --disable-features=VizDisplayCompositor \
  "https://skywork.ai"
```

### 2. 登录Skywork平台

1. Chrome启动后会自动打开Skywork.ai
2. 在浏览器中登录您的Skywork账号
3. 确保能够看到Skywork的主界面

### 3. 执行任务

使用skywork-task命令执行任务：

```bash
# 基本用法
python main.py skywork-task "您的研究命题"

# 带标题和自定义下载目录
python main.py skywork-task "企业级 Agent 可观测性体系" \
  --title "企业级Agent可观测性研究" \
  --download-dir "data/results/skywork_observability_$(date +%Y%m%d_%H%M%S)"

# 指定Chrome调试端口
python main.py skywork-task "您的命题" --debug-port 9222
```

## 命令详解

### skywork-task命令参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `topic` | 字符串 | ✅ | - | 研究命题内容 |
| `--title` | 字符串 | ❌ | None | 任务标题（可选） |
| `--download-dir` | 字符串 | ❌ | data/results | 结果下载目录 |
| `--debug-port` | 整数 | ❌ | 9222 | Chrome调试端口 |

### 使用示例

```bash
# 示例1：AI技术研究
python main.py skywork-task "大语言模型在代码生成中的应用与局限性分析"

# 示例2：商业分析
python main.py skywork-task "2024年全球SaaS市场趋势分析" \
  --title "SaaS市场研究" \
  --download-dir "data/results/saas_analysis"

# 示例3：技术架构
python main.py skywork-task "微服务架构下的服务网格技术选型与实践" \
  --title "服务网格技术研究"
```

## 功能特性

### ✅ 已实现功能

1. **自动浏览器连接** - 连接已登录Chrome实例
2. **智能元素定位** - 自动找到输入框和提交按钮
3. **任务状态监控** - 实时监控任务执行进度
4. **结果自动提取** - 提取任务完成后的结果内容
5. **中间结果获取** - 即使任务中断也能获取已生成内容
6. **文件自动下载** - 下载PDF、DOCX等结果文件
7. **页面内容保存** - 保存截图、HTML和文本结果
8. **错误处理机制** - 完善的异常处理和调试信息

### 🎯 核心优势

- **中断恢复能力** - 即使积分不足或网络中断，也能获取中间产物
- **智能内容识别** - 自动识别和提取多种格式的结果内容
- **完整记录保存** - 保存任务的完整执行记录和元数据
- **跨平台兼容** - 支持Windows、macOS、Linux系统

## 输出文件说明

每次任务执行都会在指定目录下生成以下文件：

### 核心结果文件
- `skywork_result_[task_id].txt` - 主要文本结果
- `skywork_metadata_[task_id].json` - 任务元数据
- `skywork_screenshot_[task_id].png` - 页面截图
- `skywork_page_[task_id].html` - 完整页面HTML

### 可能的附加文件
- 平台生成的文档文件（PDF、DOCX等）
- 其他下载的资源文件

### 元数据内容
```json
{
  "task_id": "skywork_1234567890",
  "timestamp": "2024-05-31 22:55:40",
  "page_url": "https://skywork.ai/chat/...",
  "page_title": "天工AI助手",
  "files_downloaded": 4,
  "download_attempted": true,
  "result_length": 2048
}
```

## 故障排除

### 常见问题

#### 1. Chrome连接失败
**问题**: `连接浏览器失败`
**解决方案**:
- 确保Chrome在调试模式下运行
- 检查端口9222是否被占用：`lsof -i :9222`
- 重启Chrome调试进程

#### 2. 找不到输入框
**问题**: `无法找到输入框`
**解决方案**:
- 确保已登录Skywork平台
- 检查页面是否完全加载
- 手动刷新页面后重试

#### 3. 任务提交失败
**问题**: `提交任务失败`
**解决方案**:
- 检查账号是否有足够的积分/额度
- 确认网络连接正常
- 检查命题内容是否符合平台要求

#### 4. 结果获取不完整
**问题**: 只获取到部分结果
**解决方案**:
- 增加等待时间（代码中的timeout配置）
- 手动检查页面确认结果是否已完全生成
- 使用中断恢复功能重新获取

### 调试模式

启用调试模式以获取更详细的日志信息：

```bash
python main.py --debug skywork-task "您的命题"
```

### 日志查看

查看详细的执行日志：

```bash
# 查看最新日志
tail -f logs/autocall_agent.log

# 查看特定时间的日志
grep "2024-05-31 22:" logs/autocall_agent.log
```

## 最佳实践

### 1. 命题设计
- 明确具体的研究问题
- 避免过于宽泛的主题
- 适当控制命题长度（建议200字以内）

### 2. 执行时机
- 选择网络状况良好的时段
- 确保账号有足够的使用额度
- 避免同时执行多个任务

### 3. 结果管理
- 定期清理旧的结果文件
- 使用有意义的目录名称
- 及时备份重要结果

### 4. 监控运行
- 关注任务执行日志
- 适时检查Chrome浏览器状态
- 必要时手动干预处理

## 技术架构

### 核心组件
- **SkyworkPlatform** - 主要平台实现类
- **Playwright** - 浏览器自动化引擎
- **TaskResult** - 结果数据模型
- **异常处理** - 完善的错误处理机制

### 执行流程
1. 连接Chrome调试实例
2. 导航到Skywork页面
3. 查找并填写输入框
4. 提交任务并监控状态
5. 提取结果内容
6. 下载相关文件
7. 保存执行记录

### 扩展性设计
- 插件式平台架构
- 统一的接口标准
- 可配置的选择器
- 灵活的结果处理

## 更新日志

### v1.0.0 (2024-05-31)
- ✅ 初始版本发布
- ✅ 基础自动化功能实现
- ✅ 中断恢复机制
- ✅ 完整文档编写

---

更多技术支持请查看项目README.md或提交Issue。 