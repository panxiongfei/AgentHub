<template>
  <div class="dashboard" v-loading="loading">
    <!-- 概览卡片 -->
    <div class="overview-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#409EFF">
                  <Platform />
                </el-icon>
              </div>
              <div class="card-info">
                <div class="card-number">{{ stats.platforms }}</div>
                <div class="card-label">平台总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#67C23A">
                  <Document />
                </el-icon>
              </div>
              <div class="card-info">
                <div class="card-number">{{ stats.totalTasks }}</div>
                <div class="card-label">总任务数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#E6A23C">
                  <Clock />
                </el-icon>
              </div>
              <div class="card-info">
                <div class="card-number">{{ stats.runningTasks }}</div>
                <div class="card-label">运行中任务</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="overview-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#F56C6C">
                  <Download />
                </el-icon>
              </div>
              <div class="card-info">
                <div class="card-number">{{ stats.downloadedTasks }}</div>
                <div class="card-label">已下载任务</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 图表和数据 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- 任务执行趋势 -->
        <el-col :span="16">
          <el-card title="任务执行趋势">
            <template #header>
              <div class="card-header">
                <span>任务执行趋势</span>
                <el-button-group size="small">
                  <el-button @click="changeTimeRange('7d')" :type="timeRange === '7d' ? 'primary' : 'default'">7天</el-button>
                  <el-button @click="changeTimeRange('30d')" :type="timeRange === '30d' ? 'primary' : 'default'">30天</el-button>
                  <el-button @click="changeTimeRange('90d')" :type="timeRange === '90d' ? 'primary' : 'default'">90天</el-button>
                </el-button-group>
              </div>
            </template>
            <div class="chart-container">
              <v-chart :option="taskTrendOption" style="height: 300px;" />
            </div>
          </el-card>
        </el-col>

        <!-- 平台状态 -->
        <el-col :span="8">
          <el-card title="平台状态">
            <div class="platform-status">
              <div
                v-for="platform in platformStatus"
                :key="platform.name"
                class="platform-item"
              >
                <div class="platform-info">
                  <div class="platform-name">{{ platform.name }}</div>
                  <div class="platform-meta">
                    <span>任务: {{ platform.tasks }}</span>
                    <span>成功率: {{ platform.successRate }}%</span>
                  </div>
                </div>
                <div class="platform-status-badge">
                  <el-tag
                    :type="platform.status === 'active' ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ platform.status === 'active' ? '在线' : '离线' }}
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近任务和快速操作 -->
    <div class="bottom-section">
      <el-row :gutter="20">
        <!-- 最近任务 -->
        <el-col :span="16">
          <el-card title="最近任务">
            <template #header>
              <div class="card-header">
                <span>最近任务</span>
                <el-button size="small" @click="$router.push('/history')">
                  查看全部
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
            <el-table :data="recentTasks" style="width: 100%" v-if="recentTasks.length > 0">
              <el-table-column prop="title" label="任务标题" show-overflow-tooltip />
              <el-table-column prop="platform" label="平台" width="100">
                <template #default="{ row }">
                  <el-tag 
                    size="small" 
                    :type="getPlatformType(row.platformKey)"
                  >
                    {{ row.platform }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag
                    :type="getStatusType(row.status)"
                    size="small"
                  >
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.createdAt) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    @click="viewTaskDetail(row)"
                  >
                    查看
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty 
              v-else 
              description="暂无任务数据"
              :image-size="80"
            />
          </el-card>
        </el-col>

        <!-- 快速操作 -->
        <el-col :span="8">
          <el-card title="快速操作">
            <div class="quick-actions">
              <el-button
                type="primary"
                size="large"
                class="action-button"
                @click="$router.push('/tasks/create')"
              >
                <el-icon><Plus /></el-icon>
                创建新任务
              </el-button>
              
              <el-button
                type="success"
                size="large"
                class="action-button"
                @click="startBrowserManager"
              >
                <el-icon><Monitor /></el-icon>
                启动浏览器
              </el-button>
              
              <el-button
                type="warning"
                size="large"
                class="action-button"
                @click="$router.push('/history')"
              >
                <el-icon><Download /></el-icon>
                历史任务
              </el-button>
              
              <el-button
                type="info"
                size="large"
                class="action-button"
                @click="$router.push('/system')"
              >
                <el-icon><Document /></el-icon>
                系统状态
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import {
  Platform,
  Document,
  Clock,
  Download,
  ArrowRight,
  Plus,
  Monitor
} from '@element-plus/icons-vue'
import { apiGet } from '@/utils/api'
import dayjs from 'dayjs'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

// 数据
const loading = ref(false)
const timeRange = ref('7d')
const stats = ref({
  platforms: 0,
  totalTasks: 0,
  runningTasks: 0,
  downloadedTasks: 0
})

const platformStatus = ref([])
const recentTasks = ref([])

// 图表数据
const chartData = ref({
  dates: [],
  successful: [],
  failed: []
})

// 图表配置
const taskTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: function(params) {
      let result = `${params[0].axisValue}<br/>`
      params.forEach(param => {
        result += `${param.marker}${param.seriesName}: ${param.value}<br/>`
      })
      return result
    }
  },
  legend: {
    data: ['成功任务', '失败任务']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.value.dates.length > 0 ? chartData.value.dates : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    minInterval: 1
  },
  series: [
    {
      name: '成功任务',
      type: 'line',
      data: chartData.value.successful.length > 0 ? chartData.value.successful : [8, 0, 0, 0, 0, 0, 8],
      smooth: true,
      itemStyle: { color: '#67C23A' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(103, 194, 58, 0.3)'
          }, {
            offset: 1, color: 'rgba(103, 194, 58, 0.1)'
          }]
        }
      }
    },
    {
      name: '失败任务',
      type: 'line',
      data: chartData.value.failed.length > 0 ? chartData.value.failed : [0, 0, 0, 0, 0, 0, 0],
      smooth: true,
      itemStyle: { color: '#F56C6C' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(245, 108, 108, 0.3)'
          }, {
            offset: 1, color: 'rgba(245, 108, 108, 0.1)'
          }]
        }
      }
    }
  ]
}))

// 方法
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // 并行加载所有数据
    await Promise.all([
      loadStats(),
      loadRecentTasks(),
      loadPlatformStatus(),
      loadChartData()
    ])
  } catch (error) {
    console.error('加载Dashboard数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    // 获取平台列表
    const platformsData = await apiGet('/api/v1/platforms')
    const availablePlatforms = platformsData.platforms || []
    
    // 获取总体统计数据
    const historyData = await apiGet('/api/v1/history')
    const historyStats = historyData.stats || {}
    
    stats.value = {
      platforms: availablePlatforms.length,
      totalTasks: historyStats.total || 0,
      runningTasks: 0, // 目前没有运行中任务的API
      downloadedTasks: historyStats.successful || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用默认值
    stats.value = {
      platforms: 3,
      totalTasks: 0,
      runningTasks: 0,
      downloadedTasks: 0
    }
  }
}

const loadRecentTasks = async () => {
  try {
    // 加载最近的5个任务
    const recentTasksData = await apiGet('/api/v1/history', { size: 5 })
    
    if (recentTasksData && recentTasksData.tasks) {
      recentTasks.value = recentTasksData.tasks.map(task => ({
        id: task.id,
        title: task.title,
        platformKey: task.platform,
        platform: {
          'skywork': 'Skywork',
          'manus': 'Manus',
          'coze_space': '扣子空间'
        }[task.platform] || task.platform,
        status: task.success ? 'completed' : 'failed',
        createdAt: new Date(task.download_time || task.timestamp || Date.now())
      }))
    } else {
      recentTasks.value = []
    }
  } catch (error) {
    console.error('加载最近任务失败:', error)
    recentTasks.value = []
  }
}

const loadPlatformStatus = async () => {
  try {
    const platformsData = await apiGet('/api/v1/platforms')
    const availablePlatforms = platformsData.platforms || []
    
    // 初始化平台状态
    const platforms = availablePlatforms.map(p => ({
      name: p.display_name || p.name,
      key: p.name,
      status: p.enabled ? 'active' : 'offline',
      tasks: 0,
      successRate: 0
    }))
    
    // 获取各平台的历史任务数据
    for (const platform of platforms) {
      try {
        const historyData = await apiGet('/api/v1/history', { platform: platform.key })
        
        if (historyData && historyData.stats) {
          platform.tasks = historyData.stats.total || 0
          platform.successRate = platform.tasks > 0 
            ? Math.round(((historyData.stats.successful || 0) / platform.tasks) * 100) 
            : 0
        }
      } catch (error) {
        console.warn(`获取 ${platform.name} 数据失败:`, error)
        platform.status = 'offline'
      }
    }
    
    platformStatus.value = platforms
  } catch (error) {
    console.error('加载平台状态失败:', error)
    // 使用默认数据
    platformStatus.value = [
      { name: 'Manus', key: 'manus', status: 'offline', tasks: 0, successRate: 0 },
      { name: 'Skywork', key: 'skywork', status: 'offline', tasks: 0, successRate: 0 },
      { name: '扣子空间', key: 'coze_space', status: 'offline', tasks: 0, successRate: 0 }
    ]
  }
}

const loadChartData = async () => {
  try {
    // 使用默认数据（暂时移除API调用）
    const dates = []
    const successful = []
    const failed = []
    
    const days = timeRange.value === '7d' ? 7 : timeRange.value === '30d' ? 30 : 90
    
    for (let i = days - 1; i >= 0; i--) {
      const date = dayjs().subtract(i, 'day')
      dates.push(date.format('MM-DD'))
      successful.push(Math.floor(Math.random() * 3)) // 模拟数据
      failed.push(Math.floor(Math.random() * 1))
    }
    
    chartData.value = { dates, successful, failed }
  } catch (error) {
    console.error('加载图表数据失败:', error)
    // 使用默认数据
    const dates = []
    const successful = []
    const failed = []
    
    for (let i = 6; i >= 0; i--) {
      const date = dayjs().subtract(i, 'day')
      dates.push(date.format('MM-DD'))
      successful.push(0)
      failed.push(0)
    }
    
    chartData.value = { dates, successful, failed }
  }
}

const changeTimeRange = (range) => {
  timeRange.value = range
  // 重新加载图表数据
  loadChartData()
}

const getStatusType = (status) => {
  const typeMap = {
    completed: 'success',
    running: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    pending: '等待中'
  }
  return textMap[status] || '未知'
}

const getPlatformType = (platform) => {
  const typeMap = {
    'skywork': 'primary',
    'manus': 'success',
    'coze_space': 'warning'
  }
  return typeMap[platform] || 'info'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const viewTaskDetail = (task) => {
  router.push(`/history/detail/${task.platformKey}/${task.id}`)
}

const startBrowserManager = () => {
  // 检测Chrome调试端口是否可用
  ElMessage.info('正在启动浏览器管理器...')
  // 实际应该检查Chrome调试端口状态
  router.push('/platforms')
}

onMounted(() => {
  loadDashboardData()
  
  // 定时刷新数据（每30秒）
  const refreshInterval = setInterval(() => {
    loadStats()
    loadPlatformStatus()
  }, 30000)
  
  // 组件卸载时清除定时器
  const stopWatching = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }
  }
  
  // 组件卸载时清除定时器
  onBeforeUnmount(stopWatching)
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-card {
  height: 120px;
}

.card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.card-icon {
  flex-shrink: 0;
}

.card-info {
  text-align: right;
  flex: 1;
}

.card-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.card-label {
  font-size: 14px;
  color: #909399;
}

.charts-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.platform-status {
  padding: 10px 0;
}

.platform-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.platform-item:last-child {
  border-bottom: none;
}

.platform-info {
  flex: 1;
}

.platform-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.platform-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 12px;
}

.platform-status-badge {
  flex-shrink: 0;
}

.bottom-section {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 10px 0;
}

.action-button {
  width: 100%;
  height: 50px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-button .el-icon {
  font-size: 16px;
}
</style> 