<template>
  <div class="system-logs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统日志</span>
          <el-button type="primary" @click="refreshLogs">刷新</el-button>
        </div>
      </template>
      
      <div class="log-container">
        <el-input
          v-model="logContent"
          type="textarea"
          :rows="20"
          readonly
          placeholder="日志加载中..."
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const logContent = ref('暂无日志数据')

const refreshLogs = () => {
  logContent.value = '日志刷新功能待实现...'
}

onMounted(() => {
  // TODO: 从后端API获取日志数据
  logContent.value = '[系统日志组件已加载]\n待实现：从后端获取实际日志数据'
})
</script>

<style scoped>
.system-logs {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  margin-top: 10px;
}
</style> 