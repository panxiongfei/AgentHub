# 部署指南

本文档说明如何在不同环境中部署 AgentHub。

## 🐳 Docker 部署（推荐）

### 快速启动
```bash
# 克隆项目
git clone https://github.com/username/AgentHub.git
cd AgentHub

# 使用 Docker Compose 启动
docker-compose up -d
```

### 配置说明
编辑 `docker-compose.yml` 文件来自定义配置：
- 端口映射
- 环境变量
- 数据卷挂载

## 🔧 手动部署

### 系统要求
- Python 3.9+
- Node.js 18+
- Chrome 浏览器（用于浏览器自动化）

### 后端部署
```bash
# 1. 安装Python依赖
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. 配置环境变量
cp configs/settings.yaml.example configs/settings.yaml
# 编辑配置文件

# 3. 启动后端服务
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### 前端部署
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 构建生产版本
npm run build

# 3. 部署到Web服务器
# 将 dist/ 目录内容复制到 Nginx/Apache 等Web服务器
```

## ⚙️ 环境配置

### 环境变量
创建 `.env` 文件：
```env
# 基础配置
DEBUG=false
LOG_LEVEL=info

# 数据库配置
DATABASE_URL=sqlite:///./data/agenthub.db

# Chrome配置
CHROME_DEBUG_PORT=9222
```

### 配置文件
编辑 `configs/settings.yaml`：
```yaml
app:
  name: "AgentHub"
  debug: false
  log_level: "info"

platforms:
  manus:
    enabled: true
    base_url: "https://manus.com"
  
  skywork:
    enabled: true
    base_url: "https://skywork.com"
```

## 🔒 安全配置

### HTTPS 配置
生产环境建议使用 HTTPS：
```bash
# 使用 Let's Encrypt 获取证书
certbot --nginx -d yourdomain.com
```

### 防火墙配置
```bash
# 开放必要端口
ufw allow 80
ufw allow 443
ufw allow 8000  # API服务端口
```

## 📊 监控和日志

### 日志配置
日志文件位置：
- 应用日志: `logs/app.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

### 健康检查
访问健康检查端点：
- API健康状态: `http://your-domain:8000/health`
- 系统状态: `http://your-domain:8000/api/v1/system/status`

## 🔄 更新和维护

### 更新应用
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
pip install -r requirements.txt
cd frontend && npm install

# 3. 重启服务
docker-compose restart
# 或手动重启服务
```

### 数据备份
```bash
# 备份数据库
cp data/agenthub.db backups/agenthub_$(date +%Y%m%d).db

# 备份配置文件
tar -czf backups/configs_$(date +%Y%m%d).tar.gz configs/
```

## 🚨 故障排除

### 常见问题
1. **Chrome连接失败**
   - 检查Chrome是否运行在调试模式
   - 验证端口配置是否正确

2. **前端无法访问后端API**
   - 检查CORS配置
   - 验证API服务是否正常运行

3. **数据库连接错误**
   - 检查数据库文件权限
   - 验证数据库路径配置

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看Docker日志
docker-compose logs -f agenthub
```

## 📞 技术支持

如遇到部署问题，请：
1. 检查[故障排除](#故障排除)部分
2. 查看[Issues](../../issues)中的已知问题
3. 创建新的Issue描述问题 