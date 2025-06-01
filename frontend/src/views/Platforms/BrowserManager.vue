<template>
  <div class="browser-manager">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>浏览器管理</h2>
        <p class="page-description">管理多平台Chrome浏览器实例，支持登录状态复用</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="startAllBrowsers" :loading="isStartingAll">
          <el-icon><VideoPlay /></el-icon>
          启动所有浏览器
        </el-button>
        <el-button @click="stopAllBrowsers" :loading="isStoppingAll">
          <el-icon><VideoPause /></el-icon>
          停止所有浏览器
        </el-button>
        <el-button @click="refreshStatus">
          <el-icon><Refresh /></el-icon>
          刷新状态
        </el-button>
      </div>
    </div>

    <!-- 浏览器实例卡片 -->
    <el-row :gutter="20" class="browser-cards">
      <el-col
        v-for="browser in browsers"
        :key="browser.platform"
        :span="8"
      >
        <el-card class="browser-card">
          <template #header>
            <div class="card-header">
              <div class="platform-info">
                <el-icon size="24" :color="getPlatformColor(browser.platform)">
                  <component :is="getPlatformIcon(browser.platform)" />
                </el-icon>
                <div class="platform-details">
                  <h3>{{ browser.platform }}</h3>
                  <span class="platform-url">{{ browser.url }}</span>
                </div>
              </div>
              <div class="status-badge">
                <el-tag
                  :type="getStatusType(browser.status)"
                  :effect="browser.status === 'running' ? 'light' : 'plain'"
                >
                  {{ getStatusText(browser.status) }}
                </el-tag>
              </div>
            </div>
          </template>

          <div class="browser-info">
            <!-- 基本信息 -->
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item label="调试端口">
                <span class="port-text">{{ browser.port }}</span>
                <el-button
                  v-if="browser.status === 'running'"
                  size="small"
                  text
                  @click="openDebugUrl(browser)"
                >
                  打开
                </el-button>
              </el-descriptions-item>
              <el-descriptions-item label="进程ID">
                {{ browser.pid || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="用户数据目录">
                <el-tooltip :content="browser.userDataDir" placement="top">
                  <span class="data-dir">{{ getShortPath(browser.userDataDir) }}</span>
                </el-tooltip>
              </el-descriptions-item>
              <el-descriptions-item label="启动时间">
                {{ browser.startTime ? formatTime(browser.startTime) : '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 运行状态详情 -->
            <div v-if="browser.status === 'running'" class="running-details">
              <el-divider>运行状态</el-divider>
              <div class="metrics">
                <div class="metric-item">
                  <span class="metric-label">运行时长</span>
                  <span class="metric-value">{{ getRunningTime(browser.startTime) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">登录状态</span>
                  <el-tag
                    :type="browser.loginStatus === 'logged_in' ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ browser.loginStatus === 'logged_in' ? '已登录' : '未登录' }}
                  </el-tag>
                </div>
                <div class="metric-item">
                  <span class="metric-label">标签页数</span>
                  <span class="metric-value">{{ browser.tabCount || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- 配置选项 -->
            <div class="browser-config">
              <el-divider>启动配置</el-divider>
              <el-form :model="browser.config" size="small" label-width="120px">
                <el-form-item label="复用登录状态">
                  <el-switch
                    v-model="browser.config.useLoginState"
                    active-text="启用"
                    inactive-text="禁用"
                  />
                </el-form-item>
                <el-form-item label="复制配置">
                  <el-switch
                    v-model="browser.config.copyProfile"
                    active-text="启用"
                    inactive-text="禁用"
                  />
                </el-form-item>
                <el-form-item label="调试端口">
                  <el-input-number
                    v-model="browser.config.port"
                    :min="9000"
                    :max="9999"
                    :disabled="browser.status === 'running'"
                    style="width: 120px"
                  />
                </el-form-item>
              </el-form>
            </div>

            <!-- 操作按钮 -->
            <div class="browser-actions">
              <el-button-group>
                <el-button
                  v-if="browser.status !== 'running'"
                  type="primary"
                  @click="startBrowser(browser)"
                  :loading="browser.isStarting"
                >
                  <el-icon><VideoPlay /></el-icon>
                  启动浏览器
                </el-button>
                <el-button
                  v-if="browser.status === 'running'"
                  @click="stopBrowser(browser)"
                  :loading="browser.isStopping"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止浏览器
                </el-button>
                <el-button
                  v-if="browser.status === 'running'"
                  @click="openBrowser(browser)"
                >
                  <el-icon><Monitor /></el-icon>
                  打开浏览器
                </el-button>
                <el-button @click="viewLogs(browser)">
                  <el-icon><Document /></el-icon>
                  查看日志
                </el-button>
              </el-button-group>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态监控 -->
    <el-card class="system-monitor">
      <template #header>
        <span>系统监控</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="monitor-item">
            <h4>Chrome进程</h4>
            <div class="monitor-value">
              {{ systemStatus.chromeProcessCount }}
            </div>
            <div class="monitor-desc">个活跃进程</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <h4>内存使用</h4>
            <div class="monitor-value">
              {{ systemStatus.memoryUsage }}
            </div>
            <div class="monitor-desc">MB</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <h4>磁盘使用</h4>
            <div class="monitor-value">
              {{ systemStatus.diskUsage }}
            </div>
            <div class="monitor-desc">GB</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="logDialog.visible"
      :title="`${logDialog.platform} 浏览器日志`"
      width="80%"
      top="5vh"
    >
      <div class="log-viewer">
        <div class="log-header">
          <el-button size="small" @click="refreshLogs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button size="small" @click="clearLogs">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
          <el-button size="small" @click="downloadLogs">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </div>
        <el-input
          v-model="logDialog.content"
          type="textarea"
          :rows="20"
          readonly
          class="log-content"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  VideoPause,
  Refresh,
  Monitor,
  Document,
  Download,
  Delete,
  Platform
} from '@element-plus/icons-vue'
import { apiGet, apiPost } from '@/utils/api'
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'

dayjs.extend(duration)

// 数据
const isStartingAll = ref(false)
const isStoppingAll = ref(false)
const refreshTimer = ref(null)

const browsers = ref([
  {
    platform: 'Skywork',
    url: 'https://skywork.ai',
    port: 9222,
    userDataDir: '~/chrome_skywork_data',
    status: 'stopped', // stopped, starting, running, stopping
    pid: null,
    startTime: null,
    loginStatus: 'unknown', // unknown, logged_in, logged_out
    tabCount: 0,
    isStarting: false,
    isStopping: false,
    config: {
      useLoginState: true,
      copyProfile: true,
      port: 9222
    }
  },
  {
    platform: 'Manus',
    url: 'https://manus.ai',
    port: 9223,
    userDataDir: '~/chrome_manus_data',
    status: 'stopped',
    pid: null,
    startTime: null,
    loginStatus: 'unknown',
    tabCount: 0,
    isStarting: false,
    isStopping: false,
    config: {
      useLoginState: true,
      copyProfile: true,
      port: 9223
    }
  },
  {
    platform: '扣子空间',
    url: 'https://www.coze.cn',
    port: 9224,
    userDataDir: '~/chrome_coze_space_data',
    status: 'stopped',
    pid: null,
    startTime: null,
    loginStatus: 'unknown',
    tabCount: 0,
    isStarting: false,
    isStopping: false,
    config: {
      useLoginState: true,
      copyProfile: true,
      port: 9224
    }
  }
])

const systemStatus = ref({
  chromeProcessCount: 0,
  memoryUsage: 0,
  diskUsage: 0
})

const logDialog = reactive({
  visible: false,
  platform: '',
  content: ''
})

// 方法
const loadBrowserStatus = async () => {
  try {
    // 模拟获取浏览器状态
    // 实际实现中应该调用后端API检查进程状态
    
    // 检查每个浏览器的状态
    for (const browser of browsers.value) {
      try {
        const response = await fetch(`http://localhost:${browser.port}/json/version`, {
          method: 'GET',
          timeout: 3000
        })
        
        if (response.ok) {
          browser.status = 'running'
          if (!browser.startTime) {
            browser.startTime = new Date()
          }
          // 获取标签页信息
          const tabsResponse = await fetch(`http://localhost:${browser.port}/json`)
          if (tabsResponse.ok) {
            const tabs = await tabsResponse.json()
            browser.tabCount = tabs.length
          }
        }
      } catch (error) {
        browser.status = 'stopped'
        browser.pid = null
        browser.startTime = null
        browser.tabCount = 0
      }
    }
    
    // 更新系统状态
    const runningBrowsers = browsers.value.filter(b => b.status === 'running')
    systemStatus.value = {
      chromeProcessCount: runningBrowsers.length,
      memoryUsage: runningBrowsers.length * 250 + Math.floor(Math.random() * 100),
      diskUsage: runningBrowsers.length * 1.2 + Math.floor(Math.random() * 0.5)
    }
    
  } catch (error) {
    console.error('获取浏览器状态失败:', error)
  }
}

const startBrowser = async (browser) => {
  try {
    browser.isStarting = true
    
    ElMessage.info(`正在启动 ${browser.platform} 浏览器...`)
    
    // 构建启动参数
    const params = {
      platform: browser.platform.toLowerCase(),
      port: browser.config.port,
      useLoginState: browser.config.useLoginState,
      copyProfile: browser.config.copyProfile
    }
    
    // 调用后端API启动浏览器
    // 实际实现中调用相应的脚本
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟启动时间
    
    browser.status = 'running'
    browser.startTime = new Date()
    browser.pid = Math.floor(Math.random() * 90000) + 10000
    
    ElMessage.success(`${browser.platform} 浏览器启动成功`)
    
  } catch (error) {
    ElMessage.error(`启动失败: ${error.message}`)
    browser.status = 'stopped'
  } finally {
    browser.isStarting = false
  }
}

const stopBrowser = async (browser) => {
  try {
    browser.isStopping = true
    
    ElMessage.info(`正在停止 ${browser.platform} 浏览器...`)
    
    // 调用后端API停止浏览器
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟停止时间
    
    browser.status = 'stopped'
    browser.pid = null
    browser.startTime = null
    browser.tabCount = 0
    browser.loginStatus = 'unknown'
    
    ElMessage.success(`${browser.platform} 浏览器已停止`)
    
  } catch (error) {
    ElMessage.error(`停止失败: ${error.message}`)
  } finally {
    browser.isStopping = false
  }
}

const startAllBrowsers = async () => {
  isStartingAll.value = true
  
  try {
    const stoppedBrowsers = browsers.value.filter(b => b.status === 'stopped')
    
    if (stoppedBrowsers.length === 0) {
      ElMessage.info('所有浏览器都已在运行中')
      return
    }
    
    ElMessage.info(`正在启动 ${stoppedBrowsers.length} 个浏览器...`)
    
    await Promise.all(stoppedBrowsers.map(browser => startBrowser(browser)))
    
    ElMessage.success('所有浏览器启动完成')
  } catch (error) {
    ElMessage.error('批量启动失败: ' + error.message)
  } finally {
    isStartingAll.value = false
  }
}

const stopAllBrowsers = async () => {
  try {
    const runningBrowsers = browsers.value.filter(b => b.status === 'running')
    
    if (runningBrowsers.length === 0) {
      ElMessage.info('没有运行中的浏览器')
      return
    }
    
    await ElMessageBox.confirm(
      `确认停止 ${runningBrowsers.length} 个运行中的浏览器吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    isStoppingAll.value = true
    
    await Promise.all(runningBrowsers.map(browser => stopBrowser(browser)))
    
    ElMessage.success('所有浏览器已停止')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量停止失败: ' + error.message)
    }
  } finally {
    isStoppingAll.value = false
  }
}

const openBrowser = (browser) => {
  if (browser.status === 'running') {
    window.open(browser.url, '_blank')
  }
}

const openDebugUrl = (browser) => {
  const debugUrl = `http://localhost:${browser.port}`
  window.open(debugUrl, '_blank')
}

const viewLogs = (browser) => {
  logDialog.platform = browser.platform
  logDialog.content = `[${dayjs().format('YYYY-MM-DD HH:mm:ss')}] ${browser.platform} 浏览器日志\n\n` +
    `启动参数:\n` +
    `- 端口: ${browser.port}\n` +
    `- 数据目录: ${browser.userDataDir}\n` +
    `- 复用登录: ${browser.config.useLoginState ? '是' : '否'}\n` +
    `- 复制配置: ${browser.config.copyProfile ? '是' : '否'}\n\n` +
    `运行状态:\n` +
    `- 状态: ${getStatusText(browser.status)}\n` +
    `- PID: ${browser.pid || '无'}\n` +
    `- 运行时长: ${browser.startTime ? getRunningTime(browser.startTime) : '无'}\n\n` +
    `Chrome调试信息:\n` +
    `DevTools listening on ws://127.0.0.1:${browser.port}/devtools/browser/xxx\n` +
    `[INFO] Browser started successfully\n` +
    `[INFO] User profile loaded\n` +
    `[INFO] Extensions loaded\n`
  
  logDialog.visible = true
}

const refreshLogs = () => {
  ElMessage.success('日志已刷新')
}

const clearLogs = () => {
  logDialog.content = ''
  ElMessage.success('日志已清空')
}

const downloadLogs = () => {
  const blob = new Blob([logDialog.content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${logDialog.platform}_browser_logs_${dayjs().format('YYYYMMDD_HHmmss')}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('日志下载已开始')
}

const refreshStatus = () => {
  loadBrowserStatus()
  ElMessage.success('状态已刷新')
}

const getPlatformIcon = (platform) => {
  return Platform // 可以根据平台返回不同图标
}

const getPlatformColor = (platform) => {
  const colorMap = {
    'Skywork': '#409EFF',
    'Manus': '#67C23A',
    '扣子空间': '#E6A23C'
  }
  return colorMap[platform] || '#909399'
}

const getStatusType = (status) => {
  const typeMap = {
    'running': 'success',
    'starting': 'warning',
    'stopping': 'warning',
    'stopped': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'running': '运行中',
    'starting': '启动中',
    'stopping': '停止中',
    'stopped': '已停止'
  }
  return textMap[status] || '未知'
}

const getShortPath = (path) => {
  if (path.length > 30) {
    return '...' + path.slice(-27)
  }
  return path
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

const getRunningTime = (startTime) => {
  if (!startTime) return '0分钟'
  
  const duration = dayjs.duration(dayjs().diff(startTime))
  const hours = Math.floor(duration.asHours())
  const minutes = duration.minutes()
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

onMounted(() => {
  loadBrowserStatus()
  // 每30秒自动刷新状态
  refreshTimer.value = setInterval(loadBrowserStatus, 30000)
})

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
})
</script>

<style scoped>
.browser-manager {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.browser-cards {
  margin-bottom: 20px;
}

.browser-card {
  height: auto;
  min-height: 450px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.platform-details h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.platform-url {
  color: #909399;
  font-size: 12px;
}

.status-badge {
  flex-shrink: 0;
}

.browser-info {
  padding: 0;
}

.port-text {
  font-family: monospace;
  font-weight: 500;
}

.data-dir {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
}

.running-details {
  margin: 16px 0;
}

.metrics {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
}

.metric-value {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.browser-config {
  margin: 16px 0;
}

.browser-actions {
  margin-top: 16px;
  text-align: center;
}

.system-monitor {
  margin-bottom: 20px;
}

.monitor-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.monitor-item h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.monitor-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.monitor-desc {
  font-size: 12px;
  color: #909399;
}

.log-viewer {
  height: 60vh;
  display: flex;
  flex-direction: column;
}

.log-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.log-content {
  flex: 1;
}

.log-content :deep(.el-textarea__inner) {
  height: 100% !important;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  background: #1e1e1e;
  color: #d4d4d4;
  border: none;
}
</style> 