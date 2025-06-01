# Manus平台自动化使用指南

## 🎯 功能概述

本功能可以连接到你当前已登录的Chrome浏览器实例，自动在Manus平台上输入命题、提交任务，并监控任务完成后自动下载结果文件。

## 📋 前置条件

1. **Chrome浏览器已安装并登录Manus**
   - 确保Chrome浏览器已安装
   - 在Chrome中访问 https://manus.ai 并完成登录
   - 保持Chrome浏览器运行

2. **Python环境已配置**
   - 已安装项目依赖：`pip install -r requirements.txt`
   - 已安装Playwright：`playwright install chromium`

## 🚀 快速开始

### 方法一：使用现有Chrome实例

如果你已经在Chrome中登录了Manus：

1. **启用Chrome调试模式** (如果尚未启用)
   ```bash
   # 方法1: 使用我们的脚本启动新的Chrome实例
   python scripts/start_chrome_debug.py
   
   # 方法2: 手动启动Chrome调试模式
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/chrome_debug \
     https://manus.ai
   ```

2. **执行Manus任务**
   ```bash
   python main.py manus-task "请分析当前AI技术的发展趋势和未来展望"
   ```

### 方法二：使用我们的启动脚本

1. **启动Chrome调试模式并访问Manus**
   ```bash
   python scripts/start_chrome_debug.py
   ```
   
2. **在弹出的Chrome窗口中登录Manus**

3. **在另一个终端执行任务**
   ```bash
   python main.py manus-task "你的研究命题" --title "研究标题"
   ```

## 📖 命令详解

### 基本语法
```bash
python main.py manus-task <命题内容> [选项]
```

### 参数说明

- **命题内容** (必填): 要研究的问题或命题
- **--title**: 任务标题 (可选)
- **-d, --download-dir**: 下载目录 (默认: data/results)
- **--debug-port**: Chrome调试端口 (默认: 9222)

### 使用示例

```bash
# 基本使用
python main.py manus-task "分析人工智能在医疗领域的应用"

# 指定标题和下载目录
python main.py manus-task "区块链技术发展趋势" \
  --title "区块链研究报告" \
  --download-dir "./downloads/blockchain"

# 使用自定义调试端口
python main.py manus-task "机器学习算法比较" --debug-port 9223
```

## 🔧 工作流程

1. **连接浏览器**: 连接到指定端口的Chrome调试实例
2. **查找Manus页面**: 自动定位Manus标签页或创建新页面
3. **输入命题**: 查找输入框并输入你的研究命题
4. **提交任务**: 点击提交按钮或按Enter键提交
5. **监控状态**: 定期检查任务执行状态
6. **获取结果**: 任务完成后提取结果内容
7. **下载文件**: 自动下载相关文件或保存页面内容

## 📁 输出文件

任务完成后，系统会尝试下载以下文件：

1. **直接下载文件**: PDF、DOCX、XLSX等格式的报告文件
2. **页面截图**: 完整的页面截图 (PNG格式)
3. **页面HTML**: 保存完整的页面源代码
4. **结果文本**: 提取的文本结果 (TXT格式)

## ⚠️ 注意事项

1. **登录状态**: 确保在Chrome中已登录Manus平台
2. **网络连接**: 保持稳定的网络连接
3. **页面元素**: 如果Manus界面更新，可能需要调整选择器
4. **调试端口**: 确保指定的调试端口未被其他程序占用
5. **权限问题**: 确保下载目录有写入权限

## 🐛 故障排除

### 常见问题

1. **无法连接到Chrome**
   ```
   错误: 无法连接到Chrome调试端口
   解决: 检查Chrome是否以调试模式启动，端口是否正确
   ```

2. **找不到Manus页面**
   ```
   解决: 手动在Chrome中打开 https://manus.ai
   ```

3. **无法找到输入框**
   ```
   解决: 检查是否已登录，页面是否完全加载
   ```

4. **任务提交失败**
   ```
   解决: 检查网络连接，确认Manus平台正常工作
   ```

### 调试选项

使用 `--debug` 标志获取详细日志：
```bash
python main.py --debug manus-task "你的命题"
```

### 查看调试截图

如果任务失败，系统会在 `data/temp/` 目录保存调试截图。

## 📊 高级用法

### 批量处理
```bash
# 创建命题列表文件
echo "AI在教育中的应用" > topics.txt
echo "区块链技术发展" >> topics.txt
echo "量子计算前景" >> topics.txt

# 批量执行 (需要自己编写脚本)
while IFS= read -r topic; do
  python main.py manus-task "$topic" --download-dir "./results/$(date +%Y%m%d)"
  sleep 60  # 等待1分钟避免过于频繁
done < topics.txt
```

### 定时执行
```bash
# 使用cron定时执行
# 编辑crontab: crontab -e
# 添加: 0 9 * * * cd /path/to/AgentHub && python main.py manus-task "每日AI趋势分析"
```

## 🔗 相关链接

- [Manus官网](https://manus.ai)
- [Playwright文档](https://playwright.dev)
- [Chrome调试协议](https://chromedevtools.github.io/devtools-protocol/) 