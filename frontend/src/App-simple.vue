<template>
  <div id="app">
    <div style="padding: 20px; text-align: center;">
      <h1>🚀 AgentHub 管理系统</h1>
      <p>{{ message }}</p>
      <el-button type="primary" @click="testClick">测试按钮</el-button>
      <el-button type="success" @click="goToLayout">测试布局</el-button>
      <div style="margin-top: 20px;">
        <el-tag>Vue 正常工作</el-tag>
        <el-tag type="success">Element Plus 正常工作</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const message = ref('Vue应用已成功加载!')

const testClick = () => {
  console.log('按钮点击测试成功!')
  alert('Vue应用正常工作!')
  message.value = '按钮点击测试成功! ' + new Date().toLocaleTimeString()
}

const goToLayout = () => {
  router.push('/')
}
</script>

<style scoped>
#app {
  height: 100vh;
  width: 100vw;
}
</style> 