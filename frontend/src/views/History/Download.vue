<template>
  <div class="history-download">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>批量下载历史任务</h2>
        <p class="page-description">批量下载各平台的历史任务内容</p>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/history/list')">
          <el-icon><ArrowLeft /></el-icon>
          返回任务列表
        </el-button>
      </div>
    </div>

    <!-- 平台选择卡片 -->
    <el-row :gutter="20" class="platform-cards">
      <el-col :span="8" v-for="platform in platforms" :key="platform.name">
        <el-card class="platform-card" :class="{ active: selectedPlatform === platform.name }">
          <template #header>
            <div class="card-header">
              <div class="platform-info">
                <div :class="['platform-icon', platform.name]">
                  {{ platform.name === 'coze_space' ? '扣子' : platform.displayName.charAt(0) }}
                </div>
                <div>
                  <h4>{{ platform.displayName }}</h4>
                  <p class="platform-desc">{{ platform.description }}</p>
                </div>
              </div>
              <el-radio-group v-model="selectedPlatform">
                <el-radio :label="platform.name">选择</el-radio>
              </el-radio-group>
            </div>
          </template>
          
          <div class="platform-stats">
            <el-statistic
              title="可下载任务数"
              :value="platform.taskCount"
              :loading="platform.loading"
            />
            <el-statistic
              title="成功率"
              :value="platform.successRate"
              suffix="%"
              :loading="platform.loading"
            />
          </div>
          
          <div class="platform-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="selectPlatform(platform.name)"
              :disabled="platform.taskCount === 0"
            >
              选择此平台
            </el-button>
            <el-button 
              size="small"
              @click="refreshPlatform(platform.name)"
              :loading="platform.loading"
            >
              刷新状态
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 下载配置 -->
    <el-card v-if="selectedPlatform" class="download-config">
      <template #header>
        <span>下载配置 - {{ getPlatformDisplayName(selectedPlatform) }}</span>
      </template>
      
      <el-form :model="downloadConfig" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="下载模式">
              <el-select v-model="downloadConfig.mode" placeholder="选择下载模式">
                <el-option label="快速下载" value="quick" />
                <el-option label="完整下载" value="full" />
                <el-option label="自定义数量" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="文件类型" v-if="downloadConfig.mode !== 'quick'">
              <el-checkbox-group v-model="downloadConfig.fileTypes">
                <el-checkbox label="content">对话内容</el-checkbox>
                <el-checkbox label="metadata">元数据</el-checkbox>
                <el-checkbox label="screenshot">截图</el-checkbox>
                <el-checkbox label="html">页面HTML</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" v-if="downloadConfig.mode === 'custom'">
          <el-col :span="12">
            <el-form-item label="下载数量">
              <el-input-number 
                v-model="downloadConfig.count" 
                :min="1" 
                :max="50" 
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="downloadConfig.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="保存路径">
          <el-input v-model="downloadConfig.savePath" placeholder="留空使用默认路径" />
          <div class="path-note">
            <el-text type="info" size="small">
              默认路径：data/history_downloads/{{ selectedPlatform }}_{{ getCurrentTimestamp() }}
            </el-text>
          </div>
        </el-form-item>
        
        <el-form-item label="其他选项">
          <el-checkbox v-model="downloadConfig.includeAI">包含AI分析</el-checkbox>
          <el-checkbox v-model="downloadConfig.createZip">创建ZIP压缩包</el-checkbox>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 下载预览 -->
    <el-card v-if="selectedPlatform" class="download-preview">
      <template #header>
        <div class="preview-header">
          <span>下载预览</span>
          <el-button size="small" @click="refreshPreview" :loading="previewLoading">
            <el-icon><Refresh /></el-icon>
            刷新预览
          </el-button>
        </div>
      </template>
      
      <div v-if="previewLoading" class="preview-loading">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="previewTasks.length > 0" class="preview-content">
        <div class="preview-summary">
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="预计下载任务">{{ previewTasks.length }}</el-descriptions-item>
            <el-descriptions-item label="估计文件数">{{ estimatedFiles }}</el-descriptions-item>
            <el-descriptions-item label="预计大小">{{ estimatedSize }}</el-descriptions-item>
            <el-descriptions-item label="预计耗时">{{ estimatedTime }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="preview-tasks">
          <h4>任务列表预览</h4>
          <el-table :data="previewTasks.slice(0, 5)" size="small" border>
            <el-table-column prop="title" label="任务标题" min-width="200" />
            <el-table-column prop="createdTime" label="创建时间" width="150">
              <template #default="{ row }">
                {{ formatTime(row.createdTime) }}
              </template>
            </el-table-column>
            <el-table-column prop="filesCount" label="文件数" width="80" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.success ? 'success' : 'danger'" size="small">
                  {{ row.success ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="previewTasks.length > 5" class="more-tasks">
            <el-text type="info">
              还有 {{ previewTasks.length - 5 }} 个任务未显示...
            </el-text>
          </div>
        </div>
      </div>
      
      <div v-else class="no-preview">
        <el-empty description="暂无可下载的任务" />
      </div>
    </el-card>

    <!-- 下载操作 -->
    <div v-if="selectedPlatform && previewTasks.length > 0" class="download-actions">
      <el-card>
        <div class="action-buttons">
          <el-button
            type="primary"
            size="large"
            @click="startDownload"
            :loading="downloading"
            :disabled="downloading || previewTasks.length === 0"
          >
            <el-icon><Download /></el-icon>
            {{ downloading ? '下载中...' : '开始下载' }}
          </el-button>
          
          <el-button
            size="large"
            @click="resetConfig"
            :disabled="downloading"
          >
            <el-icon><Refresh /></el-icon>
            重置配置
          </el-button>
        </div>
        
        <!-- 下载进度 -->
        <div v-if="downloading" class="download-progress">
          <el-progress
            :percentage="downloadProgress.percentage"
            :status="downloadProgress.status"
            striped
            striped-flow
          />
          <div class="progress-info">
            <span>{{ downloadProgress.current }} / {{ downloadProgress.total }}</span>
            <span>{{ downloadProgress.message }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 下载结果 -->
    <el-card v-if="downloadResult" class="download-result">
      <template #header>
        <span>下载结果</span>
      </template>
      
      <div class="result-summary">
        <el-alert
          :title="downloadResult.success ? '下载完成' : '下载失败'"
          :type="downloadResult.success ? 'success' : 'error'"
          show-icon
          :closable="false"
        >
          <template #default>
            <p>{{ downloadResult.message }}</p>
            <div v-if="downloadResult.success" class="success-info">
              <p>成功下载：{{ downloadResult.successCount }} 个任务</p>
              <p>保存路径：{{ downloadResult.savePath }}</p>
              <p>总文件数：{{ downloadResult.totalFiles }}</p>
            </div>
          </template>
        </el-alert>
      </div>
      
      <div v-if="downloadResult.success" class="result-actions">
        <el-button type="primary" @click="openDownloadFolder">
          <el-icon><FolderOpened /></el-icon>
          打开下载文件夹
        </el-button>
        <el-button @click="downloadAgain">
          <el-icon><Download /></el-icon>
          再次下载
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Download,
  Refresh,
  FolderOpened
} from '@element-plus/icons-vue'
import { historyService } from '@/utils/services'

const router = useRouter()

// 响应式数据
const selectedPlatform = ref('')
const downloading = ref(false)
const previewLoading = ref(false)

const platforms = ref([
  {
    name: 'skywork',
    displayName: 'Skywork AI',
    description: '专业的AI助手和智能分析平台',
    taskCount: 0,
    successRate: 0,
    loading: false
  },
  {
    name: 'manus',
    displayName: 'Manus AI',
    description: '智能研究和内容生成助手',
    taskCount: 0,
    successRate: 0,
    loading: false
  },
  {
    name: 'coze_space',
    displayName: '扣子空间',
    description: '多模态AI工作流和协作平台',
    taskCount: 0,
    successRate: 0,
    loading: false
  }
])

const downloadConfig = reactive({
  mode: 'quick',
  fileTypes: ['content', 'metadata', 'screenshot'],
  count: 10,
  dateRange: null,
  savePath: '',
  includeAI: true,
  createZip: true
})

const downloadProgress = reactive({
  percentage: 0,
  current: 0,
  total: 0,
  status: '',
  message: ''
})

const downloadResult = ref(null)
const previewTasks = ref([])

// 计算属性
const estimatedFiles = computed(() => {
  return previewTasks.value.length * downloadConfig.fileTypes.length
})

const estimatedSize = computed(() => {
  const avgSize = 2.5 // MB per task
  return `约 ${(previewTasks.value.length * avgSize).toFixed(1)} MB`
})

const estimatedTime = computed(() => {
  const timePerTask = 3 // seconds
  const totalSeconds = previewTasks.value.length * timePerTask
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return minutes > 0 ? `约 ${minutes}分${seconds}秒` : `约 ${seconds}秒`
})

// 方法
const getCurrentTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
}

const getPlatformDisplayName = (platformName) => {
  const platform = platforms.value.find(p => p.name === platformName)
  return platform?.displayName || platformName
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN')
}

const loadPlatformStats = async () => {
  for (const platform of platforms.value) {
    try {
      platform.loading = true
      const historyData = await historyService.getHistoryTasks({ platform: platform.name })
      
      if (historyData && historyData.tasks) {
        platform.taskCount = historyData.tasks.length
        const successfulTasks = historyData.tasks.filter(task => task.success)
        platform.successRate = platform.taskCount > 0 
          ? Math.round((successfulTasks.length / platform.taskCount) * 100) 
          : 0
      }
    } catch (error) {
      console.error(`加载 ${platform.name} 统计失败:`, error)
      platform.taskCount = 0
      platform.successRate = 0
    } finally {
      platform.loading = false
    }
  }
}

const refreshPlatform = async (platformName) => {
  const platform = platforms.value.find(p => p.name === platformName)
  if (!platform) return
  
  try {
    platform.loading = true
    const historyData = await historyService.getHistoryTasks({ platform: platformName })
    
    if (historyData && historyData.tasks) {
      platform.taskCount = historyData.tasks.length
      const successfulTasks = historyData.tasks.filter(task => task.success)
      platform.successRate = platform.taskCount > 0 
        ? Math.round((successfulTasks.length / platform.taskCount) * 100) 
        : 0
    }
    
    ElMessage.success(`${platform.displayName} 状态已刷新`)
  } catch (error) {
    ElMessage.error(`刷新 ${platform.displayName} 状态失败`)
  } finally {
    platform.loading = false
  }
}

const selectPlatform = (platformName) => {
  selectedPlatform.value = platformName
  refreshPreview()
}

const refreshPreview = async () => {
  if (!selectedPlatform.value) return
  
  try {
    previewLoading.value = true
    
    const filters = { platform: selectedPlatform.value }
    
    if (downloadConfig.mode === 'custom') {
      if (downloadConfig.dateRange && downloadConfig.dateRange.length === 2) {
        filters.dateRange = downloadConfig.dateRange
      }
    }
    
    const historyData = await historyService.getHistoryTasks(filters)
    
    if (historyData && historyData.tasks) {
      let tasks = historyData.tasks.filter(task => task.success)
      
      if (downloadConfig.mode === 'quick') {
        tasks = tasks.slice(0, 5)
      } else if (downloadConfig.mode === 'custom') {
        tasks = tasks.slice(0, downloadConfig.count)
      }
      
      previewTasks.value = tasks
    } else {
      previewTasks.value = []
    }
  } catch (error) {
    ElMessage.error('获取预览数据失败')
    previewTasks.value = []
  } finally {
    previewLoading.value = false
  }
}

const startDownload = async () => {
  try {
    await ElMessageBox.confirm(
      `确认下载 ${previewTasks.value.length} 个任务吗？`,
      '确认下载',
      { type: 'warning' }
    )
    
    downloading.value = true
    downloadProgress.percentage = 0
    downloadProgress.current = 0
    downloadProgress.total = previewTasks.value.length
    downloadProgress.status = 'active'
    downloadProgress.message = '开始下载...'
    
    // 模拟下载过程
    for (let i = 0; i < previewTasks.value.length; i++) {
      downloadProgress.current = i + 1
      downloadProgress.percentage = Math.round(((i + 1) / previewTasks.value.length) * 100)
      downloadProgress.message = `正在下载第 ${i + 1} 个任务...`
      
      // 模拟下载延迟
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
    
    downloadProgress.status = 'success'
    downloadProgress.message = '下载完成'
    
    downloadResult.value = {
      success: true,
      message: '所有任务下载完成',
      successCount: previewTasks.value.length,
      savePath: downloadConfig.savePath || `data/history_downloads/${selectedPlatform.value}_${getCurrentTimestamp()}`,
      totalFiles: estimatedFiles.value
    }
    
    ElMessage.success('下载完成！')
    
  } catch (error) {
    if (error !== 'cancel') {
      downloadProgress.status = 'exception'
      downloadProgress.message = '下载失败'
      ElMessage.error('下载失败：' + error.message)
    }
  } finally {
    downloading.value = false
  }
}

const resetConfig = () => {
  Object.assign(downloadConfig, {
    mode: 'quick',
    fileTypes: ['content', 'metadata', 'screenshot'],
    count: 10,
    dateRange: null,
    savePath: '',
    includeAI: true,
    createZip: true
  })
  downloadResult.value = null
  previewTasks.value = []
}

const openDownloadFolder = () => {
  ElMessage.info('打开文件夹功能需要在实际环境中实现')
}

const downloadAgain = () => {
  downloadResult.value = null
  downloadProgress.percentage = 0
  downloadProgress.current = 0
  downloadProgress.total = 0
}

// 生命周期
onMounted(() => {
  loadPlatformStats()
})
</script>

<style scoped>
@import '@/assets/platform-icons.css';
.history-download {
  padding: 20px;
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

.platform-cards {
  margin-bottom: 20px;
}

.platform-card {
  transition: all 0.3s;
  cursor: pointer;
}

.platform-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.platform-card.active {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
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

.platform-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.platform-info h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.platform-desc {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

.platform-stats {
  display: flex;
  justify-content: space-between;
  margin: 16px 0;
}

.platform-actions {
  display: flex;
  gap: 8px;
}

.download-config {
  margin-bottom: 20px;
}

.path-note {
  margin-top: 8px;
}

.download-preview {
  margin-bottom: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-loading {
  padding: 20px;
}

.preview-summary {
  margin-bottom: 20px;
}

.preview-tasks h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.more-tasks {
  text-align: center;
  margin-top: 12px;
}

.download-actions {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.download-progress {
  margin-top: 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.download-result {
  margin-bottom: 20px;
}

.success-info {
  margin-top: 12px;
}

.success-info p {
  margin: 4px 0;
  color: #67C23A;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}

.no-preview {
  padding: 40px;
  text-align: center;
}
</style> 