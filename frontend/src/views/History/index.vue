<template>
  <div class="history-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>历史任务管理</h2>
        <p class="page-description">查看和管理已下载的历史任务内容</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="$router.push('/history/download')">
          <el-icon><Download /></el-icon>
          批量下载
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" :inline="true">
        <el-form-item label="平台">
          <el-select v-model="filters.platform" placeholder="选择平台" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="Skywork" value="skywork" />
            <el-option label="Manus" value="manus" />
            <el-option label="扣子空间" value="coze_space" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="下载状态" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="下载成功" value="success" />
            <el-option label="下载失败" value="failed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 300px"
          />
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索任务标题或内容"
            clearable
            style="width: 250px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="searchTasks">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.total }}</div>
            <div class="stat-label">总任务数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number success">{{ stats.successful }}</div>
            <div class="stat-label">下载成功</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number error">{{ stats.failed }}</div>
            <div class="stat-label">下载失败</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number info">{{ stats.file_count }}</div>
            <div class="stat-label">文件总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务列表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>历史任务列表</span>
          <div class="header-actions">
            <el-tooltip content="导出列表">
              <el-button size="small" @click="exportTasks">
                <el-icon><Download /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="taskList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        @row-click="handleRowClick"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="title" label="任务标题" min-width="200">
          <template #default="{ row }">
            <div class="task-title">
              <el-tooltip :content="row.title" placement="top">
                <span class="title-text">{{ row.title }}</span>
              </el-tooltip>
              <div class="task-meta">
                <el-tag size="small" :type="getPlatformType(row.platform)">
                  {{ row.platform }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="下载状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.success ? 'success' : 'danger'"
              size="small"
            >
              {{ row.success ? '下载成功' : '下载失败' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="filesCount" label="文件数量" width="100">
          <template #default="{ row }">
            <span class="file-count">{{ row.files_count || 0 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="contentPreview" label="内容预览" min-width="300">
          <template #default="{ row }">
            <div class="content-preview">
              <p v-if="row.contentPreview">{{ row.contentPreview }}</p>
              <span v-else class="no-content">暂无内容预览</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="downloadTime" label="下载时间" width="180">
          <template #default="{ row }">
            <div class="time-info">
              <div>{{ formatTime(row.downloadTime) }}</div>
              <div class="time-ago">{{ formatTimeAgo(row.downloadTime) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button @click="viewTaskDetail(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              <el-button @click="downloadFiles(row)" :disabled="!row.success">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button @click="deleteTask(row)" type="danger">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 批量操作栏 -->
    <el-card v-if="selectedTasks.length > 0" class="batch-actions">
      <div class="batch-info">
        <span>已选择 {{ selectedTasks.length }} 个任务</span>
      </div>
      <div class="batch-buttons">
        <el-button @click="batchDownload" :disabled="!hasSuccessfulTasks">
          <el-icon><Download /></el-icon>
          批量下载
        </el-button>
        <el-button @click="batchDelete" type="danger">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button @click="clearSelection">清除选择</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Refresh,
  Search,
  View,
  Delete
} from '@element-plus/icons-vue'
import { apiGet, apiPost, apiDelete } from '@/utils/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const router = useRouter()

// 数据
const loading = ref(false)
const taskList = ref([])
const selectedTasks = ref([])

const filters = reactive({
  platform: '',
  status: '',
  dateRange: null,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const stats = ref({
  total: 0,
  successful: 0,
  failed: 0,
  file_count: 0
})

// 计算属性
const hasSuccessfulTasks = computed(() => {
  return selectedTasks.value.some(task => task.success)
})

// 方法
const loadHistoryTasks = async () => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params = new URLSearchParams()
    if (filters.platform) params.append('platform', filters.platform)
    if (filters.status) params.append('status', filters.status)
    params.append('page', pagination.page.toString())
    params.append('size', pagination.size.toString())
    
    // 调用实际API
    const response = await apiGet(`/api/v1/history?${params}`)
    
    taskList.value = response.tasks || []
    stats.value = response.stats || { total: 0, successful: 0, failed: 0, file_count: 0 }
    
    if (response.pagination) {
      pagination.total = response.pagination.total
    }
    
  } catch (error) {
    console.error('加载历史任务失败:', error)
    ElMessage.error('加载历史任务失败: ' + (error.message || '网络错误'))
    
    // 如果API调用失败，显示错误提示
    taskList.value = []
    stats.value = { total: 0, successful: 0, failed: 0, file_count: 0 }
  } finally {
    loading.value = false
  }
}

const loadMockHistoryData = async () => {
  // 此方法已被移除，现在使用实际API
  return {
    tasks: [],
    stats: { total: 0, successful: 0, failed: 0, file_count: 0 },
    total: 0
  }
}

const searchTasks = () => {
  // 应用筛选条件重新加载数据
  pagination.page = 1
  loadHistoryTasks()
}

const resetFilters = () => {
  Object.assign(filters, {
    platform: '',
    status: '',
    dateRange: null,
    keyword: ''
  })
  searchTasks()
}

const refreshData = () => {
  loadHistoryTasks()
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const handleRowClick = (row) => {
  viewTaskDetail(row)
}

const handleSizeChange = (size) => {
  pagination.size = size
  loadHistoryTasks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadHistoryTasks()
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
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const formatTimeAgo = (time) => {
  return dayjs(time).locale('zh-cn').fromNow()
}

const viewTaskDetail = (task) => {
  router.push(`/history/detail/${task.platform.toLowerCase()}/${task.id}`)
}

const downloadFiles = async (task) => {
  try {
    ElMessage.success(`开始下载任务 "${task.title}" 的文件`)
    
    // 调用后端API下载文件
    const downloadUrl = `/api/v1/history/download/${task.id}`
    
    // 创建临时链接下载文件
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `${task.id}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败: ' + (error.message || '网络错误'))
  }
}

const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      `确认删除任务 "${task.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除API
    await apiDelete(`/api/v1/history/${task.id}`)
    
    ElMessage.success('删除成功')
    loadHistoryTasks()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败: ' + (error.message || '网络错误'))
    }
  }
}

const batchDownload = async () => {
  const successfulTasks = selectedTasks.value.filter(task => task.success)
  
  if (successfulTasks.length === 0) {
    ElMessage.warning('请选择至少一个下载成功的任务')
    return
  }
  
  try {
    ElMessage.success(`开始批量下载 ${successfulTasks.length} 个任务`)
    
    // 调用后端API批量下载
    const taskIds = successfulTasks.map(task => task.id)
    
    const response = await fetch('/api/v1/history/batch-download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ task_ids: taskIds })
    })
    
    if (!response.ok) {
      throw new Error('批量下载请求失败')
    }
    
    // 下载返回的zip文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `batch_download_${Date.now()}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('批量下载失败:', error)
    ElMessage.error('批量下载失败: ' + (error.message || '网络错误'))
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确认删除选中的 ${selectedTasks.value.length} 个任务吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const taskIds = selectedTasks.value.map(task => task.id)
    const response = await apiPost('/api/v1/history/batch-delete', { task_ids: taskIds })
    
    ElMessage.success(`成功删除 ${response.successful?.length || 0} 个任务`)
    
    if (response.failed && response.failed.length > 0) {
      ElMessage.warning(`${response.failed.length} 个任务删除失败`)
    }
    
    clearSelection()
    loadHistoryTasks()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + (error.message || '网络错误'))
    }
  }
}

const clearSelection = () => {
  selectedTasks.value = []
}

const exportTasks = () => {
  // 导出任务列表
  ElMessage.info('导出功能开发中...')
}

onMounted(() => {
  loadHistoryTasks()
})
</script>

<style scoped>
.history-page {
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

.filter-card {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-number.success {
  color: #67C23A;
}

.stat-number.error {
  color: #F56C6C;
}

.stat-number.info {
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.task-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-text {
  font-weight: 500;
  color: #303133;
  cursor: pointer;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.title-text:hover {
  color: #409EFF;
}

.task-meta {
  display: flex;
  gap: 4px;
}

.file-count {
  font-weight: 500;
  color: #409EFF;
}

.content-preview {
  max-height: 60px;
  overflow: hidden;
}

.content-preview p {
  margin: 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.no-content {
  color: #C0C4CC;
  font-style: italic;
  font-size: 12px;
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-info div:first-child {
  font-size: 13px;
  color: #303133;
}

.time-ago {
  font-size: 11px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 400px;
}

.batch-info {
  font-size: 14px;
  color: #606266;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}
</style> 