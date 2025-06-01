<template>
  <div class="task-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="title-section">
          <h2>{{ task.title }}</h2>
          <div class="task-meta">
            <el-tag :type="getPlatformType(task.platform)" size="small">
              {{ task.platform }}
            </el-tag>
            <el-tag
              :type="task.success ? 'success' : 'danger'"
              size="small"
            >
              {{ task.success ? '下载成功' : '下载失败' }}
            </el-tag>
            <span class="download-time">
              {{ formatTime(task.downloadTime) }}
            </span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button v-if="task.success" @click="downloadAllFiles">
          <el-icon><Download /></el-icon>
          下载所有文件
        </el-button>
        <el-button @click="shareTask">
          <el-icon><Share /></el-icon>
          分享
        </el-button>
      </div>
    </div>

    <!-- 任务基本信息 -->
    <el-card class="info-card" v-if="task.success">
      <template #header>
        <span>任务信息</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
        <el-descriptions-item label="平台">{{ task.platform }}</el-descriptions-item>
        <el-descriptions-item label="文件数量">{{ task.filesCount }}</el-descriptions-item>
        <el-descriptions-item label="下载时间">{{ formatTime(task.downloadTime) }}</el-descriptions-item>
        <el-descriptions-item label="下载目录">{{ task.downloadDir }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="task.success ? 'success' : 'danger'" size="small">
            {{ task.success ? '下载成功' : '下载失败' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- AI智能总结 -->
    <el-card class="ai-summary-card" v-if="task.success">
      <template #header>
        <div class="ai-summary-header">
          <div class="header-left">
            <el-icon class="ai-icon"><Cpu /></el-icon>
            <span>AI智能总结</span>
            <el-tag v-if="aiSummary && aiSummary.cached" type="info" size="small">缓存</el-tag>
          </div>
          <div class="header-right">
            <el-button 
              size="small" 
              :loading="summaryLoading"
              @click="generateAISummary"
              :disabled="summaryLoading"
            >
              <el-icon><Refresh /></el-icon>
              {{ aiSummary ? '重新生成' : '生成总结' }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="summaryLoading" class="summary-loading">
        <el-skeleton :rows="3" animated />
        <p class="loading-text">AI正在分析任务内容，请稍候...</p>
      </div>

      <div v-else-if="aiSummary" class="ai-summary-content">
        <!-- 总体总结 -->
        <div class="summary-section">
          <h4 class="section-title">📄 总体概述</h4>
          <p class="summary-text">{{ aiSummary.overall_summary }}</p>
        </div>

        <!-- 关键发现 -->
        <div class="summary-section" v-if="aiSummary.key_findings && aiSummary.key_findings.length > 0">
          <h4 class="section-title">🔍 关键发现</h4>
          <ul class="findings-list">
            <li v-for="finding in aiSummary.key_findings" :key="finding">{{ finding }}</li>
          </ul>
        </div>

        <!-- 主要话题 -->
        <div class="summary-section" v-if="aiSummary.main_topics && aiSummary.main_topics.length > 0">
          <h4 class="section-title">🏷️ 主要话题</h4>
          <div class="topics-tags">
            <el-tag 
              v-for="topic in aiSummary.main_topics" 
              :key="topic" 
              type="primary" 
              size="small"
              class="topic-tag"
            >
              {{ topic }}
            </el-tag>
          </div>
        </div>

        <!-- 文件分析摘要 -->
        <div class="summary-section" v-if="aiSummary.file_analysis && aiSummary.file_analysis.length > 0">
          <h4 class="section-title">📁 文件分析</h4>
          <div class="file-analysis-list">
            <div 
              v-for="fileAnalysis in aiSummary.file_analysis" 
              :key="fileAnalysis.filename"
              class="file-analysis-item"
            >
              <div class="file-header">
                <el-icon class="file-icon">
                  <component :is="getFileIcon(fileAnalysis.file_type)" />
                </el-icon>
                <span class="filename">{{ fileAnalysis.filename }}</span>
                <el-tag size="small" :type="getConfidenceType(fileAnalysis.confidence)">
                  置信度: {{ Math.round(fileAnalysis.confidence * 100) }}%
                </el-tag>
              </div>
              <p class="file-summary">{{ fileAnalysis.summary }}</p>
              <div v-if="fileAnalysis.key_info && fileAnalysis.key_info.length > 0" class="key-info">
                <span class="key-info-label">关键信息：</span>
                <span class="key-info-text">{{ fileAnalysis.key_info.join(', ') }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分析统计 -->
        <div class="summary-stats">
          <el-descriptions :column="4" size="small" border>
            <el-descriptions-item label="总文件数">{{ aiSummary.total_files }}</el-descriptions-item>
            <el-descriptions-item label="已分析">{{ aiSummary.analyzed_files }}</el-descriptions-item>
            <el-descriptions-item label="分析置信度">
              <el-tag :type="getConfidenceType(aiSummary.confidence_score)" size="small">
                {{ Math.round(aiSummary.confidence_score * 100) }}%
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="内容质量">
              <el-tag :type="getQualityType(aiSummary.content_quality)" size="small">
                {{ aiSummary.content_quality }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <p class="generated-time">
            生成时间：{{ formatTime(aiSummary.generated_at) }}
          </p>
        </div>
      </div>

      <div v-else class="no-summary">
        <el-empty description="暂无AI总结">
          <el-button type="primary" @click="generateAISummary" :loading="summaryLoading">
            <el-icon><Cpu /></el-icon>
            生成AI总结
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 失败信息 -->
    <el-card class="error-card" v-if="!task.success">
      <template #header>
        <span>错误信息</span>
      </template>
      <el-alert
        :title="task.error"
        type="error"
        show-icon
        :closable="false"
      >
        <template #default>
          <p>任务下载失败，可能的原因：</p>
          <ul>
            <li>任务链接失效或需要特殊权限</li>
            <li>页面结构变化导致无法识别</li>
            <li>网络请求超时或被拦截</li>
          </ul>
        </template>
      </el-alert>
    </el-card>

    <!-- 文件内容展示 -->
    <div v-if="task.success" class="content-section">
      <el-row :gutter="20">
        <!-- 左侧：文件列表 -->
        <el-col :span="6">
          <el-card class="file-list-card">
            <template #header>
              <span>文件列表</span>
            </template>
            <div class="file-tree">
              <div
                v-for="file in files"
                :key="file.name"
                :class="['file-item', { active: activeFile === file.name }]"
                @click="selectFile(file)"
              >
                <el-icon class="file-icon">
                  <component :is="getFileIcon(file.type)" />
                </el-icon>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：文件内容 -->
        <el-col :span="18">
          <el-card class="content-card">
            <template #header>
              <div class="content-header">
                <span>{{ currentFile?.name || '选择文件查看内容' }}</span>
                <div class="content-actions" v-if="currentFile">
                  <el-button size="small" @click="downloadCurrentFile">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                  <el-button size="small" @click="copyContent" v-if="currentFile.type === 'text'">
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                </div>
              </div>
            </template>

            <div class="file-viewer" v-if="currentFile">
              <!-- 文本内容 -->
              <div v-if="currentFile.type === 'text'" class="text-content">
                <el-input
                  v-model="currentFile.content"
                  type="textarea"
                  :rows="20"
                  readonly
                  class="content-textarea"
                />
              </div>

              <!-- 图片内容 -->
              <div v-else-if="currentFile.type === 'image'" class="image-content">
                <el-image
                  :src="currentFile.content"
                  fit="contain"
                  class="content-image"
                  :preview-src-list="[currentFile.content]"
                />
                <div class="image-info">
                  <p>点击图片可以放大查看</p>
                </div>
              </div>

              <!-- HTML内容 -->
              <div v-else-if="currentFile.type === 'html'" class="html-content">
                <el-tabs v-model="htmlViewMode" class="html-tabs">
                  <el-tab-pane label="预览" name="preview">
                    <div class="html-preview">
                      <iframe
                        :srcdoc="currentFile.content"
                        frameborder="0"
                        class="html-iframe"
                      ></iframe>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="源码" name="source">
                    <div class="html-source">
                      <pre><code v-html="highlightedHtml"></code></pre>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>

              <!-- JSON内容 -->
              <div v-else-if="currentFile.type === 'json'" class="json-content">
                <pre class="json-viewer"><code>{{ formatJson(currentFile.content) }}</code></pre>
              </div>

              <!-- 其他文件类型 -->
              <div v-else class="unsupported-content">
                <el-empty description="不支持预览此文件类型">
                  <el-button @click="downloadCurrentFile">
                    <el-icon><Download /></el-icon>
                    下载文件
                  </el-button>
                </el-empty>
              </div>
            </div>

            <div v-else class="empty-viewer">
              <el-empty description="请从左侧选择文件查看内容" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Download,
  Share,
  DocumentCopy,
  Document,
  Picture,
  Folder,
  Cpu,
  Refresh
} from '@element-plus/icons-vue'
import { apiGet } from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const task = ref({})
const files = ref([])
const activeFile = ref('')
const currentFile = ref(null)
const htmlViewMode = ref('preview')

// AI总结相关数据
const aiSummary = ref(null)
const summaryLoading = ref(false)

// 获取路由参数
const { platform, taskId } = route.params

// 计算属性
const highlightedHtml = computed(() => {
  if (currentFile.value?.type === 'html') {
    // 这里可以使用 highlight.js 来高亮HTML代码
    return currentFile.value.content
  }
  return ''
})

// 方法
const loadTaskDetail = async () => {
  try {
    loading.value = true
    
    // 调用实际API获取任务详情
    const response = await apiGet(`/api/v1/history/${taskId}`)
    
    if (response.error) {
      throw new Error(response.error)
    }
    
    // 处理API返回的数据
    const taskInfo = response.task || {}
    const downloadInfo = response.download || {}
    const filesArray = response.files || []
    
    task.value = {
      id: taskInfo.id || taskId,
      title: taskInfo.title || '未知任务',
      platform: platform,
      success: filesArray.length > 0 && !response.error,
      filesCount: filesArray.length,
      downloadTime: downloadInfo.timestamp ? new Date(downloadInfo.timestamp) : new Date(),
      downloadDir: response.task_dir || '',
      taskDate: taskInfo.date || '',
      taskUrl: taskInfo.url || '',
      pageUrl: downloadInfo.page_url || '',
      pageTitle: downloadInfo.page_title || '',
      contentLength: downloadInfo.content_length || 0
    }
    
    files.value = response.files || []
    
    // 默认选择第一个文件
    if (files.value.length > 0) {
      selectFile(files.value[0])
    }
    
  } catch (error) {
    console.error('加载任务详情失败:', error)
    ElMessage.error('加载任务详情失败: ' + (error.message || '网络错误'))
    
    // 设置错误状态
    task.value = {
      id: taskId,
      title: '任务不存在',
      platform: platform,
      success: false,
      error: error.message || '任务不存在或已被删除'
    }
    files.value = []
  } finally {
    loading.value = false
  }
}

const loadMockTaskDetail = async () => {
  // 此方法已被移除，现在使用实际API
  return {
    task: {
      id: taskId,
      title: '任务不存在',
      platform: platform,
      success: false,
      error: '任务不存在或已被删除'
    },
    files: []
  }
}

const selectFile = (file) => {
  activeFile.value = file.name
  currentFile.value = file
}

const getPlatformType = (platform) => {
  const typeMap = {
    'skywork': 'primary',
    'manus': 'success',
    'coze_space': 'warning'
  }
  return typeMap[platform] || 'info'
}

const getFileIcon = (type) => {
  const iconMap = {
    'text': Document,
    'image': Picture,
    'html': Document,
    'json': Document
  }
  return iconMap[type] || Folder
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const formatJson = (obj) => {
  return JSON.stringify(obj, null, 2)
}

const goBack = () => {
  router.go(-1)
}

const downloadAllFiles = () => {
  ElMessage.success('开始下载所有文件')
  // 实际实现中调用下载API
  const downloadUrl = `/api/v1/history/download/${task.value.id}`
  window.open(downloadUrl, '_blank')
}

const downloadCurrentFile = () => {
  if (currentFile.value) {
    ElMessage.success(`开始下载 ${currentFile.value.name}`)
    const downloadUrl = `/api/v1/history/file/${task.value.id}/${currentFile.value.name}`
    window.open(downloadUrl, '_blank')
  }
}

const copyContent = async () => {
  if (currentFile.value?.type === 'text') {
    try {
      await navigator.clipboard.writeText(currentFile.value.content)
      ElMessage.success('内容已复制到剪贴板')
    } catch (error) {
      ElMessage.error('复制失败')
    }
  }
}

const shareTask = () => {
  // 实现分享功能
  ElMessage.info('分享功能开发中...')
}

// AI总结相关方法
const loadAISummary = async () => {
  try {
    const response = await apiGet(`/api/v1/history/${taskId}/ai-summary`)
    
    if (response.success && response.summary) {
      aiSummary.value = response.summary
    } else {
      aiSummary.value = null
    }
  } catch (error) {
    console.warn('加载AI总结失败:', error)
    aiSummary.value = null
  }
}

const generateAISummary = async () => {
  try {
    summaryLoading.value = true
    
    const response = await fetch(`/api/v1/history/${taskId}/ai-summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    const result = await response.json()
    
    if (result.success && result.summary) {
      aiSummary.value = result.summary
      ElMessage.success('AI总结生成成功')
    } else {
      ElMessage.error(result.error || 'AI总结生成失败')
    }
  } catch (error) {
    console.error('生成AI总结失败:', error)
    ElMessage.error('生成AI总结失败: ' + (error.message || '网络错误'))
  } finally {
    summaryLoading.value = false
  }
}

const getConfidenceType = (confidence) => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning' 
  return 'danger'
}

const getQualityType = (quality) => {
  if (quality === 'high') return 'success'
  if (quality === 'medium') return 'warning'
  return 'info'
}

onMounted(async () => {
  await loadTaskDetail()
  
  // 如果任务加载成功，尝试加载AI总结
  if (task.value.success) {
    await loadAISummary()
  }
})
</script>

<style scoped>
.task-detail {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.back-button {
  margin-top: 4px;
}

.title-section h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 20px;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.download-time {
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.info-card {
  margin-bottom: 20px;
}

.error-card {
  margin-bottom: 20px;
}

.content-section {
  margin-top: 20px;
}

.file-list-card {
  height: 600px;
}

.file-tree {
  max-height: 520px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 12px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  gap: 8px;
}

.file-item:hover {
  background-color: #f5f7fa;
}

.file-item.active {
  background-color: #e6f4ff;
  border: 1px solid #91caff;
}

.file-icon {
  flex-shrink: 0;
  color: #606266;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.content-card {
  height: 600px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-actions {
  display: flex;
  gap: 8px;
}

.file-viewer {
  height: 520px;
  overflow: hidden;
}

.text-content {
  height: 100%;
}

.content-textarea {
  height: 100%;
}

.content-textarea :deep(.el-textarea__inner) {
  height: 100% !important;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.image-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.content-image {
  max-height: 480px;
  max-width: 100%;
}

.image-info {
  margin-top: 12px;
  color: #909399;
  font-size: 12px;
}

.html-content {
  height: 100%;
}

.html-tabs {
  height: 100%;
}

.html-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
}

.html-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.html-preview {
  height: 100%;
}

.html-iframe {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}

.html-source {
  height: 100%;
  overflow: auto;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 16px;
}

.html-source pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #24292e;
}

.json-content {
  height: 100%;
  overflow: auto;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 16px;
}

.json-viewer {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #24292e;
}

.unsupported-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-viewer {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* AI总结相关样式 */
.ai-summary-card {
  margin-bottom: 20px;
}

.ai-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-icon {
  color: #409eff;
}

.summary-loading {
  padding: 20px;
  text-align: center;
}

.loading-text {
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}

.ai-summary-content {
  padding: 0;
}

.summary-section {
  margin-bottom: 24px;
}

.summary-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-text {
  margin: 0;
  line-height: 1.6;
  color: #606266;
  font-size: 14px;
}

.findings-list {
  margin: 0;
  padding-left: 20px;
  line-height: 1.6;
}

.findings-list li {
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}

.topics-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-tag {
  margin: 0;
}

.file-analysis-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-analysis-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.file-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.file-header .file-icon {
  color: #606266;
}

.filename {
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.file-summary {
  margin: 0 0 8px 0;
  line-height: 1.5;
  color: #606266;
  font-size: 14px;
}

.key-info {
  font-size: 13px;
}

.key-info-label {
  font-weight: 500;
  color: #409eff;
}

.key-info-text {
  color: #606266;
}

.summary-stats {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.generated-time {
  margin: 12px 0 0 0;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.no-summary {
  padding: 40px 20px;
  text-align: center;
}
</style> 