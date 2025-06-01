import { apiGet, apiPost, apiDelete } from './api'

// 平台相关的API服务
export const platformService = {
  // 获取所有平台信息
  async getAllPlatforms() {
    return await apiGet('/api/v1/platforms')
  },

  // 获取平台状态
  async getPlatformStatus(platformName) {
    return await apiGet(`/api/v1/platforms/${platformName}/status`)
  },

  // 测试平台连接
  async testPlatformConnection(platformName) {
    return await apiPost(`/api/v1/platforms/${platformName}/test`)
  }
}

// 历史任务相关的API服务
export const historyService = {
  // 获取历史任务列表
  async getHistoryTasks(filters = {}) {
    const params = new URLSearchParams()
    
    if (filters.platform) params.append('platform', filters.platform)
    if (filters.status) params.append('status', filters.status)
    if (filters.keyword) params.append('keyword', filters.keyword)
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.append('start_date', filters.dateRange[0])
      params.append('end_date', filters.dateRange[1])
    }
    if (filters.page) params.append('page', filters.page)
    if (filters.size) params.append('size', filters.size)

    return await apiGet(`/api/v1/history?${params}`)
  },

  // 获取单个任务详情
  async getTaskDetail(taskId) {
    return await apiGet(`/api/v1/history/${taskId}`)
  },

  // 生成AI总结
  async generateAISummary(taskId) {
    return await apiPost(`/api/v1/history/${taskId}/ai-summary`)
  },

  // 获取AI总结
  async getAISummary(taskId) {
    return await apiGet(`/api/v1/history/${taskId}/ai-summary`)
  },

  // 下载任务文件
  async downloadTaskFiles(taskId) {
    return await apiGet(`/api/v1/history/${taskId}/download`)
  },

  // 删除任务
  async deleteTask(taskId) {
    return await apiDelete(`/api/v1/history/${taskId}`)
  },

  // 批量下载
  async batchDownload(taskIds) {
    return await apiPost('/api/v1/history/batch-download', { task_ids: taskIds })
  },

  // 批量删除
  async batchDelete(taskIds) {
    return await apiPost('/api/v1/history/batch-delete', { task_ids: taskIds })
  }
}

// 系统统计相关的API服务
export const statsService = {
  // 获取系统信息
  async getSystemInfo() {
    return await apiGet('/api/v1/system/info')
  },

  // 获取健康状态
  async getHealthStatus() {
    return await apiGet('/health')
  },

  // 获取平台统计数据
  async getPlatformStats() {
    const platforms = ['skywork', 'manus', 'coze_space']
    const stats = {
      platforms: platforms.length,
      totalTasks: 0,
      successfulTasks: 0,
      failedTasks: 0
    }

    for (const platform of platforms) {
      try {
        const historyData = await historyService.getHistoryTasks({ platform })
        if (historyData && historyData.tasks) {
          stats.totalTasks += historyData.tasks.length
          stats.successfulTasks += historyData.tasks.filter(task => task.success).length
          stats.failedTasks += historyData.tasks.filter(task => !task.success).length
        }
      } catch (error) {
        console.warn(`获取 ${platform} 统计数据失败:`, error)
      }
    }

    return stats
  }
}

// 导出所有服务
export default {
  platform: platformService,
  history: historyService,
  stats: statsService
} 