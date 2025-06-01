<template>
  <div class="task-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button type="primary" :icon="Plus" @click="createTask">
            创建任务
          </el-button>
        </div>
      </template>

      <div class="filter-section">
        <el-form inline>
          <el-form-item label="平台">
            <el-select v-model="filters.platform" placeholder="选择平台" clearable>
              <el-option label="Skywork" value="skywork" />
              <el-option label="Manus" value="manus" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="选择状态" clearable>
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchTasks">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="title" label="任务标题" width="200" />
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="row.platform === 'skywork' ? 'primary' : 'success'">
              {{ row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column prop="content" label="任务内容" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewTask(row)">
              查看详情
            </el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              type="success" 
              size="small" 
              @click="executeTask(row)"
            >
              执行
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const filters = ref({
  platform: '',
  status: ''
})

const tasks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

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

const createTask = () => {
  router.push('/tasks/create')
}

const viewTask = (task) => {
  router.push(`/tasks/detail/${task.id}`)
}

const executeTask = (task) => {
  ElMessage.success(`开始执行任务: ${task.title}`)
  // 这里可以调用API执行任务
}

const searchTasks = () => {
  // 搜索任务逻辑
  loadTasks()
}

const resetFilters = () => {
  filters.value = {
    platform: '',
    status: ''
  }
  loadTasks()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadTasks()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadTasks()
}

const loadTasks = () => {
  // 模拟数据
  tasks.value = [
    {
      id: 1,
      title: '瑞幸咖啡AI智能点餐分析',
      platform: 'skywork',
      status: 'completed',
      createdAt: '2024-05-31 14:30:00',
      content: '分析瑞幸咖啡的AI智能点餐系统的技术实现和用户体验优化方案'
    },
    {
      id: 2,
      title: '电商推荐算法优化策略',
      platform: 'manus',
      status: 'pending',
      createdAt: '2024-05-31 15:20:00',
      content: '研究电商平台推荐算法的优化策略，提升用户转化率'
    },
    {
      id: 3,
      title: '自动驾驶技术发展趋势',
      platform: 'skywork',
      status: 'running',
      createdAt: '2024-05-31 16:10:00',
      content: '分析自动驾驶技术的最新发展趋势和未来应用场景'
    }
  ]
  total.value = tasks.value.length
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.task-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 