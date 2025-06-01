# 历史任务批量下载功能使用指南

## 功能概述

历史任务批量下载功能允许您一键下载Skywork或Manus平台上的所有历史任务和结果文件，实现数据的完整备份和归档。

## 主要特性

### 🔍 智能任务发现
- **自动识别**：智能识别左侧历史任务栏的所有任务项
- **多选择器支持**：支持多种页面结构，适应不同版本的平台界面
- **任务解析**：自动提取任务标题、日期、预览内容等信息
- **去重处理**：智能去除重复任务，确保下载的准确性

### 📥 批量下载能力
- **逐一访问**：按顺序点击每个历史任务，等待内容加载完成
- **多格式保存**：支持文本内容、页面截图、HTML源码、附件文件等
- **完整备份**：每个任务都保存在独立文件夹中，便于管理
- **元数据记录**：记录下载时间、文件数量、内容长度等元信息

### 🧠 智能容错机制
- **优雅降级**：即使某些任务下载失败，也会继续处理其他任务
- **中断恢复**：支持下载过程中的中断恢复机制
- **错误报告**：详细记录每个任务的下载状态和错误信息
- **重试机制**：对网络错误等临时问题进行自动重试

## 前置条件

### 1. Chrome浏览器准备
首先启动Chrome调试模式：

```bash
# 启动Chrome调试模式
python scripts/start_chrome_debug.py
```

### 2. 平台登录
在Chrome中手动登录到对应平台：
- **Skywork平台**：https://skywork.ai
- **Manus平台**：https://manus.ai

确保能够看到左侧的历史任务列表。

## 使用方法

### 1. 快速预览历史任务

在下载之前，建议先预览任务列表：

```bash
# 预览Skywork历史任务
python main.py list-history --platform skywork

# 预览Manus历史任务  
python main.py list-history --platform manus
```

**输出示例**：
```
📋 共发现 15 个历史任务:

┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 序号 ┃ 标题                                                       ┃ 日期               ┃ 预览                                           ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ 企业级 Agent 可观测性体系                                 │ 2025-05-31 14:20   │ 构建企业级Agent可观测性体系需要从多个维度... │
│ 2    │ AI系统架构设计                                            │ 2025-05-30 16:45   │ 现代AI系统架构设计的核心原则包括...       │
│ 3    │ 微服务治理最佳实践                                        │ 2025-05-29 10:30   │ 微服务架构下的治理体系需要考虑...         │
│ ...  │ ...                                                       │ ...                │ ...                                          │
┗━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

💡 使用以下命令批量下载这些任务:
   python main.py download-history --platform skywork
```

### 2. 批量下载历史任务

#### 基础下载命令

```bash
# 下载Skywork历史任务
python main.py download-history --platform skywork

# 下载Manus历史任务
python main.py download-history --platform manus
```

#### 自定义下载目录

```bash
# 指定下载目录
python main.py download-history --platform skywork --download-dir /path/to/downloads

# 使用相对路径
python main.py download-history --platform skywork -d data/skywork_backup
```

#### 仅预览不下载

```bash
# 预览任务列表但不实际下载
python main.py download-history --platform skywork --preview-only
```

#### 自定义Chrome调试端口

```bash
# 使用不同的调试端口
python main.py download-history --platform skywork --debug-port 9223
```

### 3. 完整工作流程示例

```bash
# 1. 启动Chrome调试模式
python scripts/start_chrome_debug.py

# 2. 在浏览器中登录平台（手动操作）

# 3. 预览历史任务
python main.py list-history --platform skywork

# 4. 批量下载（带预览）
python main.py download-history --platform skywork --preview-only

# 5. 确认后执行实际下载
python main.py download-history --platform skywork --download-dir data/skywork_backup
```

## 下载结果结构

### 目录结构
```
data/history_downloads/
├── task_skywork_history_0_1748704321/
│   ├── content.txt           # 任务的主要内容
│   ├── screenshot.png        # 页面截图
│   ├── page.html            # 页面HTML源码
│   ├── metadata.json        # 任务元数据
│   └── *.pdf/*.docx         # 下载的附件文件（如有）
├── task_skywork_history_1_1748704322/
│   └── ...
├── task_skywork_history_2_1748704323/
│   └── ...
└── download_report.json     # 下载报告总结
```

### 文件说明

#### content.txt
包含任务的主要文本内容：
```
任务标题: 企业级 Agent 可观测性体系
任务日期: 2025-05-31 14:20
任务URL: https://skywork.ai/chat/xxx
下载时间: 2025-05-31 23:45:12
============================================================

[任务的详细内容...]
```

#### metadata.json
记录任务的详细元数据：
```json
{
  "task": {
    "id": "skywork_history_0_1748704321",
    "title": "企业级 Agent 可观测性体系",
    "date": "2025-05-31 14:20",
    "url": "https://skywork.ai/chat/xxx",
    "preview": "构建企业级Agent可观测性体系..."
  },
  "download": {
    "timestamp": "2025-05-31 23:45:12",
    "platform": "skywork",
    "files_count": 4,
    "content_length": 2048,
    "page_url": "https://skywork.ai/chat/xxx",
    "page_title": "企业级 Agent 可观测性体系 - Skywork"
  }
}
```

#### download_report.json
批量下载的总结报告：
```json
{
  "summary": {
    "total_tasks": 15,
    "successful": 13,
    "failed": 2,
    "success_rate": 0.867,
    "download_time": "2025-05-31 23:45:12",
    "platform": "skywork"
  },
  "successful_tasks": [...],
  "failed_tasks": [...]
}
```

## 输出示例

### 下载过程输出
```
📚 批量下载skywork平台历史任务
🔌 连接Chrome调试端口: 9222
📂 下载目录: data/history_downloads

📋 发现 15 个历史任务:

[任务列表表格...]

🤔 即将下载 15 个历史任务，这可能需要较长时间

📊 下载结果统计:
✅ 成功下载: 13 个任务
❌ 下载失败: 2 个任务
📈 成功率: 86.7%

🎉 成功下载的任务:
  1. 企业级 Agent 可观测性体系...
     📁 文件数: 4
  2. AI系统架构设计...
     📁 文件数: 3
  ...

📂 所有文件已保存到: /path/to/data/history_downloads
📋 详细报告: download_report.json
```

## 高级功能

### 1. 智能任务识别

系统支持多种任务项选择器，能够适应不同版本的平台界面：

**Skywork平台选择器**：
- `.conversation-item`, `.chat-item`, `.history-item`
- `[data-conversation-id]`, `[data-chat-id]`
- `a[href*='/chat/']`, `a[href*='/conversation/']`

**Manus平台选择器**：
- `.project-item`, `.research-item`, `.history-item`
- `[data-project-id]`, `[data-research-id]`
- `a[href*='/project/']`, `a[href*='/research/']`

### 2. 多文件类型支持

自动识别和下载多种文件类型：
- **文档类**：PDF, DOCX, DOC, TXT
- **表格类**：XLSX, XLS, CSV
- **演示类**：PPTX, PPT
- **压缩类**：ZIP, RAR
- **通用类**：带`download`属性的链接

### 3. 容错和重试机制

- **网络超时**：自动重试网络请求
- **元素定位失败**：尝试多种选择器策略
- **下载失败**：记录错误但继续处理其他任务
- **页面加载异常**：智能等待和重新加载

## 故障排除

### 常见问题

#### 1. 未发现历史任务
**问题**：显示"📭 未发现任何历史任务"

**解决方案**：
- 确保已登录平台且能看到历史任务
- 检查页面是否完全加载
- 尝试手动刷新页面后重试
- 确认平台界面未发生重大变化

#### 2. 连接Chrome失败
**问题**：无法连接到Chrome调试端口

**解决方案**：
- 确保Chrome以调试模式启动
- 检查端口9222是否被占用
- 尝试重启Chrome调试模式
- 使用`--debug-port`参数指定其他端口

#### 3. 下载失败率高
**问题**：大量任务下载失败

**解决方案**：
- 检查网络连接稳定性
- 确保有足够的磁盘空间
- 减慢下载速度（任务间间隔）
- 手动检查失败的任务页面

#### 4. 内容提取不完整
**问题**：下载的内容不完整或为空

**解决方案**：
- 等待页面完全加载后再执行
- 检查页面是否需要特殊交互（如点击"展开"）
- 确认内容区域的CSS选择器是否正确
- 尝试使用页面截图备份

### 调试方法

#### 启用详细日志
```bash
# 启用调试模式
python main.py download-history --platform skywork --debug
```

#### 逐个任务测试
```bash
# 先预览任务列表
python main.py list-history --platform skywork

# 仅预览不下载，检查识别是否正确
python main.py download-history --platform skywork --preview-only
```

#### 检查页面分析
```bash
# 使用页面分析工具
python main.py analyze-page --platform skywork
```

## 最佳实践

### 1. 下载策略
- **定期备份**：建议每周或每月进行一次完整备份
- **增量下载**：对于新增的历史任务，可以通过预览功能确认后再下载
- **分批处理**：如果历史任务很多，可以分批下载避免浏览器负载过重

### 2. 存储管理
- **目录规划**：为不同平台和时间段创建独立的下载目录
- **清理策略**：定期清理旧的备份文件，保留重要内容
- **压缩存档**：对于长期存储的备份，可以压缩以节省空间

### 3. 安全考虑
- **敏感内容**：注意下载内容中可能包含的敏感信息
- **访问控制**：确保下载目录的访问权限设置合理
- **数据加密**：对于重要的备份文件，考虑进行加密存储

### 4. 监控和维护
- **下载报告**：定期查看下载报告，关注失败率和错误模式
- **平台更新**：关注平台界面更新，及时调整选择器配置
- **功能测试**：在大批量下载前，先测试小规模下载确保功能正常

## 技术架构

### 核心组件

1. **HistoryDownloader**：历史任务批量下载器
   - 智能任务发现和解析
   - 批量下载协调和管理
   - 错误处理和报告生成

2. **EnhancedBrowserEngine**：增强版浏览器引擎
   - 页面智能分析和元素定位
   - 内容提取和文件下载
   - 操作历史记录和性能监控

3. **PlatformSelector**：平台特定选择器
   - 不同平台的界面适配
   - 多种选择器策略支持
   - 动态选择器生成

### 扩展能力

系统设计具有良好的扩展性：

- **新平台支持**：通过配置选择器策略即可支持新平台
- **自定义过滤**：可以扩展任务过滤和筛选逻辑
- **格式转换**：支持将下载内容转换为其他格式
- **API集成**：可以集成到其他系统作为服务使用

---

## 总结

历史任务批量下载功能为用户提供了强大的数据备份和归档能力，通过智能化的任务识别和稳定的下载机制，确保重要的AI助手对话历史得到完整保存。结合增强版浏览器引擎的智能分析能力，这一功能在复杂的Web环境下仍能保持高效和稳定的运行。 