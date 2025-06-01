# AgentHub 项目开发规则 v2.1

## 项目概述
AgentHub 是一个企业级多平台 AI 代理服务自动化平台，支持智能浏览器操作、历史任务批量下载、定时调度等功能。通过增强版浏览器引擎和智能页面分析技术，实现了前所未有的自动化体验。

## 技术栈

### 核心框架
- **后端框架**: FastAPI (Web API)
- **浏览器自动化**: Playwright + Chromium
- **异步处理**: asyncio, aiohttp
- **任务调度**: APScheduler
- **数据存储**: SQLite + SQLAlchemy
- **配置管理**: Pydantic Settings + YAML
- **日志系统**: structlog (结构化日志)
- **加密安全**: cryptography
- **测试框架**: pytest + pytest-asyncio
- **代码质量**: black, flake8, mypy

### 新增技术组件
- **增强版浏览器引擎**: 智能页面分析和操作
- **历史任务下载器**: 批量数据备份和归档
- **置信度评分系统**: 多维度操作可靠性评估
- **自适应操作机制**: 智能容错和恢复

## 核心架构原则

### 1. 模块化设计
- **单一职责原则**: 每个模块专注特定功能
- **依赖注入**: 组件间松耦合设计
- **插件架构**: 支持平台和功能扩展
- **分层架构**: 明确的业务逻辑、数据访问、服务层分离

### 2. 智能化能力
- **智能页面分析**: 自动识别页面结构和交互元素
- **置信度评分**: 基于可见性、选择器特异性、文本相关性的多维评估
- **自适应操作**: 根据页面变化动态调整策略
- **容错恢复**: 网络异常、页面变更的自动处理

### 3. 数据安全
- **端到端加密**: 敏感配置和用户数据加密存储
- **本地优先**: 核心数据在本地处理，减少隐私泄露
- **权限控制**: 基于角色的访问控制
- **审计追踪**: 完整的操作历史记录

## 代码规范

### 1. Python编码规范
```python
# 导入顺序
import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Page
from app.core.logger import get_logger

# 类定义
@dataclass
class TaskResult:
    """任务结果数据类"""
    task_id: str
    success: bool
    content: str = ""
    files: List[Path] = field(default_factory=list)

# 异步函数
async def smart_page_operation(page: Page) -> OperationResult:
    """智能页面操作
    
    Args:
        page: Playwright页面对象
        
    Returns:
        操作结果
        
    Raises:
        OperationError: 操作失败时抛出
    """
    try:
        # 业务逻辑
        pass
    except Exception as e:
        logger.error(f"页面操作失败: {e}")
        raise OperationError(f"操作失败: {e}")
```

### 2. 命名约定
```python
# 文件命名: snake_case.py
browser_engine.py
history_downloader.py
enhanced_platform_base.py

# 类命名: PascalCase
class EnhancedBrowserEngine:
class HistoryDownloader:
class SkyworkPlatform:

# 函数/变量命名: snake_case
async def discover_history_tasks():
def calculate_confidence_score():
task_results = []

# 常量命名: UPPER_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
CONFIDENCE_THRESHOLD = 0.7

# 私有方法: _method_name
async def _parse_task_item():
def _calculate_element_confidence():
```

### 3. 类型标注
```python
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# 函数类型标注
async def download_task_content(
    task: HistoryTask, 
    download_dir: Path
) -> DownloadResult:
    """下载单个任务内容"""
    pass

# 复杂类型定义
SelectorConfig = Dict[str, List[str]]
OperationCallback = Callable[[OperationResult], Awaitable[None]]
```

## 项目结构规范

### 核心模块组织
```
app/
├── core/                           # 核心业务逻辑
│   ├── browser_engine.py         # 增强版浏览器引擎
│   ├── history_downloader.py     # 历史任务下载器
│   ├── task_executor.py          # 任务执行器
│   ├── logger.py                 # 结构化日志
│   └── exceptions.py             # 自定义异常
├── platforms/                     # 平台适配器
│   ├── base.py                   # 基础平台类
│   ├── enhanced_platform_base.py # 增强版基类
│   ├── skywork.py               # Skywork平台
│   └── manus.py                 # Manus平台
├── scheduler/                     # 任务调度
├── storage/                       # 数据存储
├── config/                        # 配置管理
├── utils/                         # 工具函数
└── api/                          # Web API
```

### 配置文件组织
```
configs/
├── settings.yaml                 # 主配置文件
├── platforms.yaml               # 平台配置
├── logging.yaml                 # 日志配置
└── security.yaml               # 安全配置
```

### 数据目录结构
```
data/
├── downloads/                    # 历史任务下载
│   └── {platform}_history_{timestamp}/
│       ├── task_{id}/
│       │   ├── content.txt
│       │   ├── screenshot.png
│       │   ├── page.html
│       │   ├── metadata.json
│       │   └── attachments/
│       └── download_report.json
├── results/                      # 任务执行结果
├── logs/                        # 运行日志
└── temp/                        # 临时文件
```

## 开发工作流

### 1. 功能开发流程
```bash
# 1. 创建功能分支
git checkout -b feature/history-batch-download

# 2. 开发功能
# - 编写核心逻辑
# - 添加测试用例
# - 更新文档

# 3. 代码质量检查
black app/                        # 代码格式化
flake8 app/                      # 代码检查
mypy app/                        # 类型检查

# 4. 运行测试
pytest tests/ -v --cov=app      # 测试覆盖率

# 5. 提交代码
git commit -m "feat: 添加历史任务批量下载功能"

# 6. 创建Pull Request
```

### 2. 提交信息规范
```bash
# 功能开发
feat: 添加历史任务批量下载功能
feat(browser): 实现智能页面分析

# 修复问题
fix: 修复置信度评分计算错误
fix(download): 解决大文件下载超时问题

# 文档更新
docs: 更新历史下载使用指南
docs(api): 完善API接口文档

# 性能优化
perf: 优化浏览器引擎内存使用
perf(download): 提升批量下载速度

# 重构代码
refactor: 重构平台适配器基类
refactor(core): 简化任务执行逻辑

# 测试相关
test: 添加历史下载器单元测试
test(integration): 完善集成测试用例
```

## 错误处理规范

### 1. 异常设计
```python
# 自定义异常体系
class AgentHubError(Exception):
    """基础异常类"""
    pass

class BrowserEngineError(AgentHubError):
    """浏览器引擎异常"""
    pass

class HistoryDownloadError(AgentHubError):
    """历史下载异常"""
    pass

class PlatformError(AgentHubError):
    """平台相关异常"""
    pass

# 使用示例
try:
    result = await browser_engine.smart_extract_content()
except BrowserEngineError as e:
    logger.error(f"浏览器操作失败: {e}")
    return OperationResult(success=False, error=str(e))
```

### 2. 错误日志记录
```python
import structlog

logger = structlog.get_logger("history_downloader")

# 结构化日志
logger.info(
    "开始下载历史任务",
    platform="skywork",
    task_count=15,
    download_dir="/data/downloads"
)

logger.error(
    "任务下载失败",
    task_id="skywork_001",
    error="网络连接超时",
    retry_count=3
)
```

### 3. 容错处理策略
```python
async def robust_operation(max_retries: int = 3) -> OperationResult:
    """具有容错能力的操作"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            result = await perform_operation()
            return OperationResult(success=True, result=result)
        except RetryableError as e:
            last_error = e
            logger.warning(f"操作失败，第{attempt + 1}次重试: {e}")
            await asyncio.sleep(2 ** attempt)  # 指数退避
        except FatalError as e:
            logger.error(f"致命错误，停止重试: {e}")
            return OperationResult(success=False, error=str(e))
    
    return OperationResult(success=False, error=f"重试{max_retries}次后失败: {last_error}")
```

## 安全开发规范

### 1. 敏感信息处理
```python
# 配置文件加密
from app.utils.encryption import encrypt_config, decrypt_config

# 环境变量优先
import os
from app.config.settings import Settings

settings = Settings(
    skywork_username=os.getenv("SKYWORK_USERNAME"),
    skywork_password=os.getenv("SKYWORK_PASSWORD"),
    encryption_key=os.getenv("ENCRYPTION_KEY")
)

# 日志脱敏
logger.info(
    "用户登录成功",
    username=mask_username(username),  # peter*** -> pet***
    platform="skywork"
)
```

### 2. 数据验证
```python
from pydantic import BaseModel, validator

class TaskRequest(BaseModel):
    """任务请求模型"""
    content: str
    platform: str
    timeout: int = 60
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('任务内容不能为空')
        return v
    
    @validator('platform')
    def platform_must_be_supported(cls, v):
        if v not in ['skywork', 'manus']:
            raise ValueError('不支持的平台')
        return v
```

## 测试规范

### 1. 测试组织结构
```
tests/
├── unit/                         # 单元测试
│   ├── test_browser_engine.py
│   ├── test_history_downloader.py
│   └── test_platforms.py
├── integration/                  # 集成测试
│   ├── test_skywork_integration.py
│   └── test_download_workflow.py
├── fixtures/                     # 测试数据
│   ├── sample_pages/
│   └── mock_responses/
└── conftest.py                  # pytest配置
```

### 2. 测试用例编写
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_smart_extract_content():
    """测试智能内容提取"""
    # Arrange
    mock_page = AsyncMock()
    mock_page.locator.return_value.all.return_value = [mock_element]
    
    browser_engine = EnhancedBrowserEngine(mock_page)
    
    # Act
    result = await browser_engine.smart_extract_content()
    
    # Assert
    assert result.success is True
    assert len(result.result) > 0

@pytest.fixture
async def browser_engine():
    """浏览器引擎测试夹具"""
    mock_page = AsyncMock()
    return EnhancedBrowserEngine(mock_page)
```

### 3. 集成测试
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_download_workflow():
    """测试完整下载工作流"""
    # 需要真实的Chrome实例
    async with launch_browser() as browser:
        page = await browser.new_page()
        downloader = HistoryDownloader("skywork", page)
        
        tasks = await downloader.discover_history_tasks()
        assert len(tasks) > 0
        
        results = await downloader.batch_download_all(test_dir)
        assert all(r.success for r in results)
```

## 性能优化

### 1. 异步并发
```python
import asyncio
from typing import List

async def batch_process_tasks(tasks: List[Task]) -> List[Result]:
    """批量并发处理任务"""
    semaphore = asyncio.Semaphore(5)  # 限制并发数
    
    async def process_single_task(task: Task) -> Result:
        async with semaphore:
            return await process_task(task)
    
    results = await asyncio.gather(
        *[process_single_task(task) for task in tasks],
        return_exceptions=True
    )
    
    return [r for r in results if not isinstance(r, Exception)]
```

### 2. 缓存机制
```python
from functools import lru_cache
import asyncio

class ElementConfidenceCache:
    """元素置信度缓存"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, float] = {}
        self._max_size = max_size
    
    async def get_confidence(self, element_key: str) -> Optional[float]:
        return self._cache.get(element_key)
    
    async def set_confidence(self, element_key: str, confidence: float):
        if len(self._cache) >= self._max_size:
            # LRU清理
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[element_key] = confidence
```

### 3. 资源管理
```python
async def smart_resource_management():
    """智能资源管理"""
    async with resource_pool.acquire() as resource:
        try:
            result = await use_resource(resource)
            return result
        finally:
            await resource.cleanup()
```

## 监控和可观测性

### 1. 指标收集
```python
from app.core.metrics import Counter, Timer, Gauge

download_counter = Counter("history_downloads_total", ["platform", "status"])
download_duration = Timer("history_download_duration_seconds", ["platform"])
active_downloads = Gauge("active_downloads_count")

async def download_with_metrics(task: HistoryTask):
    """带指标收集的下载"""
    active_downloads.inc()
    start_time = time.time()
    
    try:
        result = await download_task_content(task)
        download_counter.labels(platform=task.platform, status="success").inc()
        return result
    except Exception as e:
        download_counter.labels(platform=task.platform, status="error").inc()
        raise
    finally:
        download_duration.labels(platform=task.platform).observe(time.time() - start_time)
        active_downloads.dec()
```

### 2. 健康检查
```python
async def health_check() -> HealthStatus:
    """系统健康检查"""
    checks = {
        "database": await check_database_connection(),
        "browser": await check_browser_availability(),
        "storage": await check_storage_space(),
        "platforms": await check_platform_connectivity()
    }
    
    overall_healthy = all(checks.values())
    return HealthStatus(healthy=overall_healthy, checks=checks)
```

## 版本管理和发布

### 1. 语义版本控制
```
v2.1.0 - 主要功能更新 (历史下载)
v2.0.1 - 补丁修复
v2.0.0 - 重大更新 (增强版浏览器引擎)
```

### 2. 变更日志
```markdown
## [2.1.0] - 2024-05-31

### Added
- 历史任务智能发现和批量下载功能
- 多格式数据备份（文本、截图、HTML、附件）
- 详细下载报告和统计分析
- 容错处理和中断恢复机制

### Changed
- 优化置信度评分算法
- 改进浏览器引擎性能
- 增强API接口功能

### Fixed
- 修复大文件下载超时问题
- 解决页面元素定位偶发失败
```

## 部署和运维

### 1. 环境配置
```yaml
# production.yaml
app:
  environment: "production"
  debug: false
  log_level: "INFO"

browser:
  headless: true
  timeout: 30000
  user_data_dir: "/data/chrome"

security:
  encryption_enabled: true
  api_rate_limit: 100
  max_download_size: "1GB"
```

### 2. Docker部署
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 复制应用代码
COPY app/ /app/app/
COPY main.py /app/
COPY configs/ /app/configs/

WORKDIR /app
EXPOSE 8000

CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

## 文档维护

### 1. 代码文档
- 所有公共API必须有详细的docstring
- 使用Google风格的文档格式
- 包含参数、返回值、异常说明
- 提供使用示例

### 2. 用户文档
- 功能使用指南
- API接口文档
- 故障排除指南
- 最佳实践说明

### 3. 开发文档
- 架构设计文档
- 代码贡献指南
- 测试规范说明
- 部署运维手册

---

本开发规则文档将随着项目发展持续更新，确保团队开发的一致性和代码质量。 