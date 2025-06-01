<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'

const systemStore = useSystemStore()

onMounted(() => {
  console.log('App.vue 组件已挂载')
  // 初始化系统状态 - 暂时延迟初始化，避免阻塞渲染
  setTimeout(async () => {
    try {
      await systemStore.initializeSystem()
      console.log('系统状态初始化完成')
    } catch (error) {
      console.error('系统状态初始化失败:', error)
    }
  }, 1000) // 延迟1秒初始化
})
</script>

<style scoped>
#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style> 