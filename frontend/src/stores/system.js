import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiRequest } from '@/utils/api'

export const useSystemStore = defineStore('system', () => {
  // 状态
  const isLoading = ref(false)
  const systemStatus = ref('unknown')
  const platforms = ref([])
  const systemInfo = ref({})
  const error = ref(null)
  
  // 计算属性
  const isOnline = computed(() => systemStatus.value === 'healthy')
  const activePlatforms = computed(() => platforms.value.filter(p => p.status === 'active'))
  
  // 操作
  const initializeSystem = async () => {
    if (isLoading.value) return // 防止重复初始化
    
    try {
      isLoading.value = true
      error.value = null
      
      // 串行执行，避免并发太多请求
      await fetchSystemStatus()
      await fetchPlatforms()
      await fetchSystemInfo()
      
    } catch (err) {
      console.error('系统初始化失败:', err)
      error.value = err.message || '系统初始化失败'
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchSystemStatus = async () => {
    try {
      const response = await apiRequest('/health')
      systemStatus.value = response.status === 'healthy' ? 'healthy' : 'error'
    } catch (err) {
      systemStatus.value = 'error'
      throw err
    }
  }
  
  const fetchPlatforms = async () => {
    try {
      const response = await apiRequest('/api/v1/platforms')
      platforms.value = response.platforms || []
    } catch (err) {
      platforms.value = []
      throw err
    }
  }
  
  const fetchSystemInfo = async () => {
    try {
      const response = await apiRequest('/api/v1/system/info')
      systemInfo.value = response
    } catch (err) {
      systemInfo.value = {}
      throw err
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    // 状态
    isLoading,
    systemStatus,
    platforms,
    systemInfo,
    error,
    // 计算属性
    isOnline,
    activePlatforms,
    // 操作
    initializeSystem,
    fetchSystemStatus,
    fetchPlatforms,
    fetchSystemInfo,
    clearError
  }
}) 