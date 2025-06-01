<template>
  <div class="task-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务详情</span>
          <div>
            <el-button 
              v-if="task.status === 'pending'" 
              type="success" 
              @click="executeTask"
            >
              执行任务
            </el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <div v-if="task" class="task-info">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
          <el-descriptions-item label="任务标题">{{ task.title }}</el-descriptions-item>
          <el-descriptions-item label="目标平台">
            <el-tag 
              v-for="platform in task.platforms" 
              :key="platform"
              :type="platform === 'skywork' ? 'primary' : 'success'"
              style="margin-right: 8px"
            >
              {{ platform }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusType(task.status)">
              {{ getStatusText(task.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-rate v-model="task.priority" disabled />
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ task.createdAt }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="task-content">
          <h3>任务内容</h3>
          <div class="content-box">
            {{ task.content }}
          </div>
        </div>

        <el-divider />

        <div v-if="task.results && task.results.length > 0" class="task-results">
          <h3>执行结果</h3>
          <el-table :data="task.results" style="width: 100%">
            <el-table-column prop="platform" label="平台" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="executedAt" label="执行时间" width="180" />
            <el-table-column prop="result" label="结果" show-overflow-tooltip />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewResult(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div v-else class="loading">
        <el-skeleton :rows="5" animated />
      </div>
    </el-card>

    <!-- 结果详情对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="执行结果详情"
      width="80%"
      max-height="70vh"
    >
      <div v-if="currentResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="平台">{{ currentResult.platform }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentResult.status)">
              {{ getStatusText(currentResult.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">{{ currentResult.executedAt }}</el-descriptions-item>
          <el-descriptions-item label="用时">{{ currentResult.duration }}ms</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="result-content">
          <h4>执行结果</h4>
          <pre>{{ currentResult.result }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const task = ref(null)
const resultDialogVisible = ref(false)
const currentResult = ref(null)

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const executeTask = () => {
  ElMessage.success(`开始执行任务: ${task.value.title}`)
  task.value.status = 'running'
  // 这里可以调用API执行任务
}

const viewResult = (result) => {
  currentResult.value = result
  resultDialogVisible.value = true
}

const goBack = () => {
  router.back()
}

const loadTask = () => {
  const taskId = route.params.id
  
  // 模拟加载任务数据
  setTimeout(() => {
    task.value = {
      id: taskId,
      title: '瑞幸咖啡AI智能点餐分析',
      platforms: ['skywork'],
      status: 'completed',
      priority: 3,
      createdAt: '2024-05-31 14:30:00',
      content: '分析瑞幸咖啡的AI智能点餐系统的技术实现和用户体验优化方案。需要从以下几个维度进行分析：\n1. 技术架构分析\n2. 算法优化策略\n3. 用户体验设计\n4. 业务价值评估\n5. 竞品对比分析',
      results: [
        {
          platform: 'skywork',
          status: 'completed',
          executedAt: '2024-05-31 14:35:00',
          duration: 1240,
          result: '通过对瑞幸咖啡AI智能点餐系统的深入分析，发现该系统在技术架构、算法优化、用户体验等方面都有显著的创新点...'
        }
      ]
    }
  }, 500)
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.task-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  margin-top: 20px;
}

.task-content {
  margin: 20px 0;
}

.content-box {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.task-results {
  margin: 20px 0;
}

.loading {
  padding: 20px;
}

.result-content pre {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.6;
}
</style> 