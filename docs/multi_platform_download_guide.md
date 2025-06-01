# 多平台并发历史下载使用指南

## 概述

AgentHub v2.1 新增的多平台并发历史下载功能，允许用户同时打开两个浏览器实例，分别登录 Skywork 和 Manus 平台，并行下载所有历史任务的配套文件。

## 功能特性

### 🚀 核心能力
- **多浏览器管理**：同时管理多个Chrome调试实例
- **并发下载**：多平台历史任务并行处理
- **完整备份**：每个任务包含文本、截图、HTML、附件、元数据
- **智能容错**：网络异常、页面变化自动处理
- **详细报告**：生成多平台统计报告

### 📊 支持平台
- ✅ **Skywork平台** (端口 9222)
- ✅ **Manus平台** (端口 9223)
- 🔄 更多平台持续扩展中...

## 快速开始

### 1. 启动多Chrome实例

```bash
# 启动多个Chrome调试实例
python scripts/start_multi_chrome.py

# 自定义端口启动
python scripts/start_multi_chrome.py --skywork-port 9222 --manus-port 9223
```

启动后会看到：
```
🌟 开始启动多Chrome实例管理器...
============================================================

🚀 启动 SKYWORK Chrome实例...
   端口: 9222
   URL: https://skywork.ai
   用户数据目录: /Users/username/chrome_skywork_data
✅ SKYWORK Chrome进程已启动 (PID: 12345)
   调试地址: http://localhost:9222

🚀 启动 MANUS Chrome实例...
   端口: 9223
   URL: https://manus.ai
   用户数据目录: /Users/username/chrome_manus_data
✅ MANUS Chrome进程已启动 (PID: 12346)
   调试地址: http://localhost:9223

🎉 所有Chrome实例启动成功！
```

### 2. 分别登录两个平台

启动后会自动打开两个Chrome窗口：
- **Skywork窗口**：访问 https://skywork.ai，请登录您的账号
- **Manus窗口**：访问 https://manus.ai，请登录您的账号

⚠️ **重要**：确保两个平台都已成功登录并可以看到历史任务列表

### 3. 预览所有平台历史任务

```bash
# 快速预览两个平台的历史任务
python main.py list-multi-history

# 使用自定义端口
python main.py list-multi-history --skywork-port 9222 --manus-port 9223
```

预览结果示例：
```
📋 SKYWORK 平台 (共 15 个历史任务):
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 序号 ┃ 标题                                             ┃ 日期          ┃ 预览                                 ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ 人工智能发展趋势分析                             │ 2024-05-30    │ 本报告深入分析了当前人工智能技术...   │
│ 2    │ 区块链技术应用研究                               │ 2024-05-29    │ 区块链作为一种分布式账本技术...       │
└──────┴──────────────────────────────────────────────────┴───────────────┴──────────────────────────────────────┘

📋 MANUS 平台 (共 8 个历史任务):
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 序号 ┃ 标题                                             ┃ 日期          ┃ 预览                                 ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ 市场调研报告-用户行为分析                        │ 2024-05-30    │ 通过大数据分析用户购买行为模式...     │
│ 2    │ 竞品分析-AI助手对比研究                          │ 2024-05-28    │ 对市面上主流AI助手进行深度对比...     │
└──────┴──────────────────────────────────────────────────┴───────────────┴──────────────────────────────────────┘

📊 汇总统计:
   🏪 平台总数: 2
   📝 任务总数: 23
```

### 4. 执行多平台并发下载

```bash
# 开始多平台并发下载
python main.py download-multi-history

# 指定下载目录
python main.py download-multi-history --download-dir /path/to/downloads

# 仅预览不下载
python main.py download-multi-history --preview-only
```

下载过程示例：
```
🌟 多平台并发历史任务下载
🔌 正在连接多个Chrome实例...
   - Skywork: 端口 9222
   - Manus:   端口 9223
✅ 所有浏览器实例连接成功

📂 下载目录: data/multi_platform_downloads
🚀 开始多平台并发历史下载...

📊 多平台下载结果统计:
⏱️  总耗时: 45.2 秒
✅ 成功下载: 20 个任务
❌ 下载失败: 3 个任务
📈 总体成功率: 87.0%

🏪 各平台详细结果:
  SKYWORK:
    ✅ 成功: 13 个
    ❌ 失败: 2 个
    📈 成功率: 86.7%
  MANUS:
    ✅ 成功: 7 个
    ❌ 失败: 1 个
    📈 成功率: 87.5%

📁 所有文件已保存到: /path/to/downloads/multi_platform_history_20240531_143022
📋 详细报告: multi_platform_download_report.json
```

## 下载结果结构

### 目录组织

```
data/multi_platform_downloads/
└── multi_platform_history_20240531_143022/
    ├── skywork/                           # Skywork平台下载
    │   ├── skywork_history_20240531_143025/
    │   │   ├── task_skywork_history_0_1748703416/
    │   │   │   ├── content.txt            # 📄 文本内容
    │   │   │   ├── screenshot.png         # 📸 页面截图
    │   │   │   ├── page.html             # 🌐 HTML源码
    │   │   │   ├── metadata.json         # 📊 元数据
    │   │   │   └── attachments/          # 📎 附件文件
    │   │   ├── task_skywork_history_1_1748703420/
    │   │   └── download_report.json      # Skywork平台报告
    ├── manus/                             # Manus平台下载
    │   ├── manus_history_20240531_143030/
    │   │   ├── task_manus_research_0_1748703425/
    │   │   └── download_report.json      # Manus平台报告
    └── multi_platform_download_report.json  # 📋 多平台总报告
```

### 多平台总报告示例

```json
{
  "timestamp": "2024-05-31 14:30:35",
  "download_dir": "/path/to/downloads/multi_platform_history_20240531_143022",
  "platforms": {
    "skywork": {
      "total_tasks": 15,
      "successful": 13,
      "failed": 2,
      "success_rate": 0.867,
      "tasks": [
        {
          "task_id": "skywork_history_0_1748703416",
          "task_title": "人工智能发展趋势分析",
          "success": true,
          "files_count": 4,
          "error": null
        }
      ]
    },
    "manus": {
      "total_tasks": 8,
      "successful": 7,
      "failed": 1,
      "success_rate": 0.875,
      "tasks": [
        {
          "task_id": "manus_research_0_1748703425",
          "task_title": "市场调研报告-用户行为分析",
          "success": true,
          "files_count": 5,
          "error": null
        }
      ]
    }
  },
  "summary": {
    "total_platforms": 2,
    "total_tasks": 23,
    "total_successful": 20,
    "total_failed": 3,
    "success_rate": 0.87
  }
}
```

## 高级用法

### 自定义端口配置

```bash
# 启动时指定不同端口
python scripts/start_multi_chrome.py --skywork-port 9224 --manus-port 9225

# 下载时匹配对应端口
python main.py download-multi-history --skywork-port 9224 --manus-port 9225
```

### 仅下载特定平台

如果只需要单平台下载，可以使用原有命令：

```bash
# 仅下载Skywork
python main.py download-history --platform skywork --debug-port 9222

# 仅下载Manus  
python main.py download-history --platform manus --debug-port 9223
```

### 批处理脚本

创建 `batch_download.sh` 脚本：

```bash
#!/bin/bash

echo "🚀 开始多平台历史下载流程"

# 1. 启动多Chrome实例
echo "📋 步骤1: 启动Chrome实例"
python scripts/start_multi_chrome.py &
CHROME_PID=$!

# 等待用户登录
echo "⏰ 请在两个Chrome窗口中登录平台，完成后按Enter继续..."
read

# 2. 预览历史任务
echo "📋 步骤2: 预览历史任务"
python main.py list-multi-history

# 3. 确认下载
echo "🤔 是否开始下载？(y/n)"
read CONFIRM

if [ "$CONFIRM" = "y" ]; then
    echo "📥 步骤3: 开始下载"
    python main.py download-multi-history
    echo "✅ 下载完成"
else
    echo "❌ 取消下载"
fi

# 4. 清理Chrome进程
echo "🧹 清理Chrome进程"
kill $CHROME_PID

echo "👋 流程结束"
```

## 故障排除

### 常见问题

#### 1. Chrome实例连接失败

**问题**：`初始化浏览器实例失败`

**解决方案**：
```bash
# 检查Chrome进程
ps aux | grep chrome

# 检查端口占用
lsof -i :9222
lsof -i :9223

# 重启Chrome实例
python scripts/start_multi_chrome.py
```

#### 2. 平台登录状态丢失

**问题**：下载时提示未登录

**解决方案**：
- 确保在Chrome调试窗口中重新登录
- 检查cookie和会话状态
- 刷新页面后重试

#### 3. 部分任务下载失败

**问题**：某些任务无法下载

**解决方案**：
- 查看 `download_report.json` 中的错误信息
- 检查网络连接是否稳定
- 手动访问失败的任务页面确认可访问性

#### 4. 内存使用过高

**问题**：长时间运行后内存占用过多

**解决方案**：
```bash
# 定期重启Chrome实例
python scripts/start_multi_chrome.py

# 限制并发下载数量
# 在代码中修改 semaphore 参数
```

### 调试模式

启用详细日志：

```bash
# 设置调试级别
export LOG_LEVEL=DEBUG

# 运行下载命令
python main.py download-multi-history --debug
```

## 性能优化建议

### 1. 硬件要求
- **内存**：建议至少 8GB RAM
- **网络**：稳定的网络连接
- **存储**：足够的磁盘空间（每个任务约10-50MB）

### 2. 优化设置
```python
# 调整并发数量
CONCURRENT_DOWNLOADS = 3  # 默认5，可根据性能调整

# 超时设置
DOWNLOAD_TIMEOUT = 120    # 默认60秒，大文件可适当增加

# 重试次数
MAX_RETRIES = 2          # 默认3次，网络不稳定时可减少
```

### 3. 监控指标
- 下载成功率
- 平均下载时间
- 内存使用情况
- 网络带宽利用率

## 扩展开发

### 添加新平台支持

1. **在MultiBrowserManager中添加平台配置**：
```python
self.platform_configs = {
    "skywork": {"port": 9222, "url": "https://skywork.ai"},
    "manus": {"port": 9223, "url": "https://manus.ai"},
    "new_platform": {"port": 9224, "url": "https://newplatform.com"}  # 新增
}
```

2. **创建平台适配器**：
```python
# app/platforms/new_platform.py
class NewPlatformAdapter(EnhancedPlatformBase):
    async def discover_history_tasks(self):
        # 实现历史任务发现逻辑
        pass
```

3. **更新历史下载器选择器**：
```python
# app/core/history_downloader.py
elif self.platform == "new_platform":
    return {
        "sidebar": [...],
        "task_items": [...],
        # 添加平台特定选择器
    }
```

## 最佳实践

### 1. 使用前准备
- ✅ 确保Chrome浏览器已安装
- ✅ 检查网络连接稳定性
- ✅ 预留足够的磁盘空间
- ✅ 关闭不必要的Chrome标签页

### 2. 下载流程
- ✅ 先使用预览模式确认任务列表
- ✅ 分批下载，避免一次下载过多任务
- ✅ 定期检查下载报告
- ✅ 备份重要的下载结果

### 3. 资源管理
- ✅ 及时清理临时文件
- ✅ 定期重启Chrome实例
- ✅ 监控系统资源使用情况
- ✅ 设置合理的并发限制

---

**AgentHub** - 让多平台AI历史数据管理变得简单高效！🚀 