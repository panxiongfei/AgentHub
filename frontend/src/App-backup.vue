<template>
  <div id="app">
    <div style="padding: 20px; text-align: center;">
      <h1>🚀 AgentHub 管理系统</h1>
      <p>系统正在加载中...</p>
      <el-button type="primary" @click="testClick">测试按钮</el-button>
    </div>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'

const systemStore = useSystemStore()

const testClick = () => {
  console.log('按钮点击测试成功!')
  alert('Vue应用正常工作!')
}

onMounted(() => {
  console.log('App.vue 组件已挂载')
  // 初始化系统状态
  try {
    systemStore.initializeSystem()
    console.log('系统状态初始化完成')
  } catch (error) {
    console.error('系统状态初始化失败:', error)
  }
})
</script>

<style scoped>
#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style> 