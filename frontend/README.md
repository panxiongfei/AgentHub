# AgentHub 前端管理系统

AgentHub 的现代化 Web 管理界面，基于 Vue.js 3 + Element Plus 构建。

## 🌟 功能特性

### 📊 仪表盘
- **实时系统状态监控** - 显示平台运行状态、任务统计等
- **任务执行趋势图表** - ECharts 可视化展示
- **快速操作面板** - 一键启动浏览器、创建任务等

### 🖥️ 浏览器管理
- **多平台浏览器控制** - Skywork、Manus 等平台浏览器实例管理
- **登录状态复用** - 自动复用系统 Chrome 登录状态
- **实时状态监控** - 进程状态、内存使用、运行时长等
- **调试端口管理** - 直接访问 Chrome DevTools

### 📋 历史任务管理
- **任务列表展示** - 支持筛选、搜索、分页
- **内容预览** - 支持文本、图片、HTML、JSON 等多种格式
- **文件管理** - 查看、下载、批量操作
- **详情查看** - 完整的任务信息和文件内容展示

### 🎯 任务管理
- **任务创建** - 支持多平台任务创建
- **执行监控** - 实时查看任务执行状态
- **结果查看** - 详细的执行结果和错误信息

### ⚙️ 系统设置
- **平台配置管理** - API 密钥、调度设置等
- **系统日志查看** - 实时日志监控和历史查询

## 🛠️ 技术栈

- **框架**: Vue.js 3 (Composition API)
- **UI 组件库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **图表**: ECharts + vue-echarts
- **HTTP 客户端**: Axios
- **样式**: Tailwind CSS
- **时间处理**: Day.js
- **代码高亮**: highlight.js
- **Markdown**: marked

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

应用将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物将生成在 `dist` 目录。

### 预览生产构建

```bash
npm run preview
# 或
yarn preview
```

## 📁 项目结构

```
frontend/
├── public/                     # 静态资源
├── src/
│   ├── components/            # 通用组件
│   ├── layout/               # 布局组件
│   │   └── index.vue         # 主布局
│   ├── router/               # 路由配置
│   │   └── index.js          # 路由定义
│   ├── stores/               # 状态管理
│   │   └── system.js         # 系统状态
│   ├── utils/                # 工具函数
│   │   └── api.js            # API 请求封装
│   ├── views/                # 页面组件
│   │   ├── Dashboard/        # 仪表盘
│   │   │   └── index.vue
│   │   ├── History/          # 历史任务
│   │   │   ├── index.vue     # 任务列表
│   │   │   ├── Detail.vue    # 任务详情
│   │   │   └── Download.vue  # 批量下载
│   │   ├── Platforms/        # 平台管理
│   │   │   ├── index.vue     # 平台列表
│   │   │   └── BrowserManager.vue # 浏览器管理
│   │   ├── Tasks/            # 任务管理
│   │   ├── Schedule/         # 调度管理
│   │   └── System/           # 系统设置
│   ├── App.vue               # 根组件
│   ├── main.js               # 入口文件
│   └── style.css             # 全局样式
├── index.html                # HTML 模板
├── package.json              # 项目配置
├── vite.config.js            # Vite 配置
├── tailwind.config.js        # Tailwind 配置
└── README.md                 # 项目文档
```

## 🔧 配置说明

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 应用标题
VITE_APP_TITLE=AgentHub 管理系统
```

### API 代理配置

开发环境下，Vite 会自动将 `/api` 请求代理到后端服务（默认 `http://localhost:8000`）。

可在 `vite.config.js` 中修改代理配置：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## 📱 页面功能说明

### 仪表盘 (`/dashboard`)
- 显示系统概览统计
- 任务执行趋势图表
- 平台状态监控
- 最近任务列表
- 快速操作按钮

### 浏览器管理 (`/platforms/browser`)
- Skywork、Manus 浏览器实例管理
- 一键启动/停止浏览器
- 登录状态复用配置
- 调试端口访问
- 实时状态监控
- 日志查看和下载

### 历史任务 (`/history/list`)
- 已下载历史任务列表
- 多维度筛选和搜索
- 内容预览
- 批量操作（下载、删除）
- 统计信息展示

### 历史任务详情 (`/history/detail/:platform/:taskId`)
- 任务基本信息
- 文件列表和内容查看器
- 支持文本、图片、HTML、JSON 预览
- 文件下载和内容复制
- 分享功能

## 🔌 API 集成

前端通过 REST API 与后端通信，主要接口包括：

### 系统接口
- `GET /health` - 健康检查
- `GET /api/v1/system/info` - 系统信息

### 平台接口
- `GET /api/v1/platforms` - 获取平台列表
- `POST /api/v1/platforms/{platform}/start` - 启动浏览器
- `POST /api/v1/platforms/{platform}/stop` - 停止浏览器

### 历史任务接口
- `GET /api/v1/history` - 获取历史任务列表
- `GET /api/v1/history/{taskId}` - 获取任务详情
- `GET /api/v1/history/download/{taskId}` - 下载任务文件
- `DELETE /api/v1/history/{taskId}` - 删除任务

## 🎨 界面特性

- **响应式设计** - 适配桌面和移动端
- **深色模式支持** - 自动适应系统主题
- **国际化** - 支持中文界面
- **无障碍访问** - 符合 WCAG 标准
- **性能优化** - 懒加载、虚拟滚动等

## 🔐 安全特性

- **API 请求拦截** - 统一错误处理和认证
- **敏感信息脱敏** - 日志中隐藏敏感数据
- **CSRF 防护** - 跨站请求伪造防护
- **XSS 防护** - 内容安全策略

## 📝 开发指南

### 代码风格

- 使用 ESLint + Prettier 保证代码质量
- 遵循 Vue.js 官方风格指南
- 组件使用 PascalCase 命名
- 文件使用 kebab-case 命名

### 组件开发

- 优先使用 Composition API
- 响应式数据使用 ref/reactive
- 副作用使用 watchEffect/watch
- 组件通信使用 props/emit

### 状态管理

- 使用 Pinia 管理全局状态
- 按功能模块划分 store
- 异步操作封装在 actions 中

### 样式开发

- 优先使用 Tailwind CSS 工具类
- 组件样式使用 scoped
- 避免深度选择器，使用 :deep() 替代

## 🧪 测试

```bash
# 运行单元测试
npm run test:unit

# 运行端到端测试
npm run test:e2e

# 运行测试覆盖率
npm run test:coverage
```

## 📦 部署

### Docker 部署

```bash
# 构建镜像
docker build -t autocall-agent-frontend .

# 运行容器
docker run -p 3000:80 autocall-agent-frontend
```

### Nginx 部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持

如有问题或建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索现有 [Issues](https://github.com/your-repo/issues)
3. 创建新的 Issue
4. 联系开发团队

---

**AgentHub Frontend** - 为企业级 AI 代理服务自动化提供现代化管理界面 🚀 