<template>
  <div class="platform-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI平台管理</span>
          <div class="header-actions">
            <el-button type="primary" :icon="Plus" @click="addPlatform">
              添加平台
            </el-button>
            <el-button @click="refreshPlatforms">
              <el-icon><Refresh /></el-icon>
              刷新状态
            </el-button>
          </div>
        </div>
      </template>

      <!-- 平台统计概览 -->
      <div class="platform-stats">
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ platformStats.total }}</div>
                <div class="stat-label">总平台数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number success">{{ platformStats.active }}</div>
                <div class="stat-label">活跃平台</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number info">{{ platformStats.totalTasks }}</div>
                <div class="stat-label">历史任务</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number warning">{{ platformStats.totalFiles }}</div>
                <div class="stat-label">下载文件</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 平台列表 -->
      <el-table :data="platforms" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="平台名称" width="150">
          <template #default="{ row }">
            <div class="platform-name">
              <img :src="row.icon" :alt="row.name" class="platform-icon" />
              <span>{{ row.displayName }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="url" label="平台地址" min-width="200">
          <template #default="{ row }">
            <el-link :href="row.url" target="_blank" type="primary">
              {{ row.url }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="连接状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="debugPort" label="调试端口" width="100" />
        
        <el-table-column prop="tasks" label="历史任务" width="100">
          <template #default="{ row }">
            <span class="task-count">{{ row.taskCount || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="lastActivity" label="最后活动" width="180">
          <template #default="{ row }">
            <span v-if="row.lastActivity">{{ formatTime(row.lastActivity) }}</span>
            <span v-else class="text-muted">暂无活动</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="capabilities" label="平台能力" min-width="200">
          <template #default="{ row }">
            <div class="capabilities">
              <el-tag v-for="capability in row.capabilities" :key="capability" size="small" class="capability-tag">
                {{ capability }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button type="primary" @click="manageBrowser(row)">
                <el-icon><Monitor /></el-icon>
                管理浏览器
              </el-button>
              <el-button type="success" @click="viewHistory(row)">
                <el-icon><Clock /></el-icon>
                查看历史
              </el-button>
              <el-button type="info" @click="testConnection(row)">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 平台详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="平台详情" width="600px">
      <div v-if="selectedPlatform" class="platform-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="平台名称">{{ selectedPlatform.displayName }}</el-descriptions-item>
          <el-descriptions-item label="平台代码">{{ selectedPlatform.name }}</el-descriptions-item>
          <el-descriptions-item label="平台地址">{{ selectedPlatform.url }}</el-descriptions-item>
          <el-descriptions-item label="调试端口">{{ selectedPlatform.debugPort }}</el-descriptions-item>
          <el-descriptions-item label="连接状态">
            <el-tag :type="getStatusType(selectedPlatform.status)">
              {{ getStatusText(selectedPlatform.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="历史任务数">{{ selectedPlatform.taskCount || 0 }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="platform-description">
          <h4>平台描述</h4>
          <p>{{ selectedPlatform.description }}</p>
        </div>
        
        <div class="platform-capabilities">
          <h4>平台能力</h4>
          <el-tag v-for="capability in selectedPlatform.capabilities" :key="capability" class="capability-tag">
            {{ capability }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Refresh, Monitor, Clock, Connection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiGet } from '@/utils/api'

const router = useRouter()

const loading = ref(false)
const showDetailDialog = ref(false)
const selectedPlatform = ref(null)

// 平台数据
const platforms = ref([
  {
    id: 1,
    name: 'skywork',
    displayName: 'Skywork AI',
    url: 'https://skywork.ai',
    status: 'active',
    debugPort: 9222,
    description: 'Skywork AI平台 - 专业的AI助手和智能分析平台',
    taskCount: 0,
    lastActivity: null,
    icon: '/icons/skywork.png',
    capabilities: ['对话问答', '文档分析', '代码生成', '智能推理']
  },
  {
    id: 2,
    name: 'manus',
    displayName: 'Manus AI',
    url: 'https://manus.ai',
    status: 'active',
    debugPort: 9223,
    description: 'Manus AI平台 - 智能研究和内容生成助手',
    taskCount: 0,
    lastActivity: null,
    icon: '/icons/manus.png',
    capabilities: ['研究分析', '内容生成', '数据处理', '报告撰写']
  },
  {
    id: 3,
    name: 'coze_space',
    displayName: '扣子空间',
    url: 'https://space.coze.cn',
    status: 'active',
    debugPort: 9224,
    description: '扣子空间平台 - 多模态AI工作流和协作平台',
    taskCount: 0,
    lastActivity: null,
    icon: '/icons/coze.png',
    capabilities: ['工作流自动化', '多模态处理', '协作空间', '智能对话']
  }
])

// 计算平台统计
const platformStats = computed(() => {
  const total = platforms.value.length
  const active = platforms.value.filter(p => p.status === 'active').length
  const totalTasks = platforms.value.reduce((sum, p) => sum + (p.taskCount || 0), 0)
  const totalFiles = platforms.value.reduce((sum, p) => sum + (p.fileCount || 0), 0)
  
  return { total, active, totalTasks, totalFiles }
})

// 获取状态类型
const getStatusType = (status) => {
  const statusMap = {
    'active': 'success',
    'inactive': 'info',
    'error': 'danger',
    'connecting': 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    'active': '在线',
    'inactive': '离线',
    'error': '错误',
    'connecting': '连接中'
  }
  return statusMap[status] || '未知'
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '暂无'
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 管理浏览器
const manageBrowser = (platform) => {
  router.push(`/platforms/browser?platform=${platform.name}`)
}

// 查看历史
const viewHistory = (platform) => {
  router.push(`/history/list?platform=${platform.name}`)
}

// 测试连接
const testConnection = async (platform) => {
  try {
    loading.value = true
    ElMessage.info(`正在测试 ${platform.displayName} 连接...`)
    
    // 调用API测试连接
    // 这里可以添加实际的连接测试逻辑
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟延迟
    
    platform.status = 'active'
    platform.lastActivity = new Date().toISOString()
    ElMessage.success(`${platform.displayName} 连接测试成功`)
  } catch (error) {
    platform.status = 'error'
    ElMessage.error(`${platform.displayName} 连接测试失败`)
  } finally {
    loading.value = false
  }
}

// 添加平台
const addPlatform = () => {
  ElMessage.info('添加平台功能开发中...')
}

// 刷新平台状态
const refreshPlatforms = async () => {
  try {
    loading.value = true
    
    // 获取平台信息
    const platformsData = await apiGet('/api/v1/platforms')
    
    // 获取历史任务统计
    for (const platform of platforms.value) {
      try {
        const historyData = await apiGet('/api/v1/history', { platform: platform.name })
        platform.taskCount = historyData.items?.length || 0
        platform.status = 'active'
        platform.lastActivity = new Date().toISOString()
      } catch (error) {
        platform.status = 'error'
        console.warn(`获取 ${platform.name} 历史数据失败:`, error)
      }
    }
    
    ElMessage.success('平台状态已刷新')
  } catch (error) {
    ElMessage.error('刷新平台状态失败')
  } finally {
    loading.value = false
  }
}

// 页面加载时的逻辑
onMounted(() => {
  refreshPlatforms()
})
</script>

<style scoped>
.platform-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.platform-stats {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-number.success {
  color: #67c23a;
}

.stat-number.info {
  color: #409eff;
}

.stat-number.warning {
  color: #e6a23c;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.platform-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.task-count {
  font-weight: bold;
  color: #409eff;
}

.text-muted {
  color: #999;
}

.capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.capability-tag {
  margin-right: 5px;
  margin-bottom: 3px;
}

.platform-detail {
  margin-top: 20px;
}

.platform-description,
.platform-capabilities {
  margin-top: 20px;
}

.platform-description h4,
.platform-capabilities h4 {
  margin-bottom: 10px;
  color: #333;
}

.platform-description p {
  color: #666;
  line-height: 1.6;
}
</style> 