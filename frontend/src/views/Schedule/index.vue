<template>
  <div class="schedule-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>调度管理</span>
          <el-button type="primary" :icon="Plus" @click="createSchedule">
            创建调度
          </el-button>
        </div>
      </template>

      <div class="filter-section">
        <el-form inline>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="选择状态" clearable>
              <el-option label="启用" value="enabled" />
              <el-option label="禁用" value="disabled" />
              <el-option label="暂停" value="paused" />
            </el-select>
          </el-form-item>
          <el-form-item label="平台">
            <el-select v-model="filters.platform" placeholder="选择平台" clearable>
              <el-option label="Skywork" value="skywork" />
              <el-option label="Manus" value="manus" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchSchedules">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="schedules" style="width: 100%">
        <el-table-column prop="name" label="调度名称" width="200" />
        <el-table-column prop="cronExpression" label="Cron表达式" width="150" />
        <el-table-column prop="nextRunTime" label="下次执行时间" width="180" />
        <el-table-column prop="platform" label="目标平台" width="120">
          <template #default="{ row }">
            <el-tag 
              v-for="platform in row.platform" 
              :key="platform"
              :type="platform === 'skywork' ? 'primary' : 'success'"
              style="margin-right: 4px"
            >
              {{ platform }}
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
        <el-table-column prop="lastRunTime" label="上次执行" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'disabled'" 
              type="success" 
              size="small" 
              @click="enableSchedule(row)"
            >
              启用
            </el-button>
            <el-button 
              v-else 
              type="warning" 
              size="small" 
              @click="disableSchedule(row)"
            >
              禁用
            </el-button>
            <el-button type="primary" size="small" @click="editSchedule(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteSchedule(row)">
              删除
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

    <!-- 创建/编辑调度对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingSchedule ? '编辑调度' : '创建调度'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="scheduleForm"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="调度名称" prop="name">
          <el-input v-model="scheduleForm.name" placeholder="请输入调度名称" />
        </el-form-item>

        <el-form-item label="Cron表达式" prop="cronExpression">
          <el-input v-model="scheduleForm.cronExpression" placeholder="例如: 0 9 * * *" />
          <div class="form-tip">
            常用表达式：每天9点 (0 9 * * *)，每小时 (0 * * * *)，每30分钟 (*/30 * * * *)
          </div>
        </el-form-item>

        <el-form-item label="目标平台" prop="platform">
          <el-checkbox-group v-model="scheduleForm.platform">
            <el-checkbox label="skywork">Skywork</el-checkbox>
            <el-checkbox label="manus">Manus</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="任务内容" prop="taskContent">
          <el-input
            v-model="scheduleForm.taskContent"
            type="textarea"
            :rows="4"
            placeholder="请输入任务内容或选择预设模板"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="scheduleForm.status">
            <el-radio label="enabled">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSchedule" :loading="saving">
            {{ editingSchedule ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const filters = ref({
  status: '',
  platform: ''
})

const schedules = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const editingSchedule = ref(null)
const formRef = ref()
const saving = ref(false)

const scheduleForm = reactive({
  name: '',
  cronExpression: '',
  platform: [],
  taskContent: '',
  status: 'enabled'
})

const rules = {
  name: [
    { required: true, message: '请输入调度名称', trigger: 'blur' }
  ],
  cronExpression: [
    { required: true, message: '请输入Cron表达式', trigger: 'blur' }
  ],
  platform: [
    { 
      type: 'array', 
      required: true, 
      message: '请选择至少一个平台', 
      trigger: 'change' 
    }
  ],
  taskContent: [
    { required: true, message: '请输入任务内容', trigger: 'blur' }
  ]
}

const getStatusType = (status) => {
  const types = {
    enabled: 'success',
    disabled: 'danger',
    paused: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    enabled: '启用',
    disabled: '禁用',
    paused: '暂停'
  }
  return texts[status] || status
}

const createSchedule = () => {
  editingSchedule.value = null
  resetForm()
  dialogVisible.value = true
}

const editSchedule = (schedule) => {
  editingSchedule.value = schedule
  Object.assign(scheduleForm, {
    name: schedule.name,
    cronExpression: schedule.cronExpression,
    platform: schedule.platform,
    taskContent: schedule.taskContent,
    status: schedule.status
  })
  dialogVisible.value = true
}

const enableSchedule = (schedule) => {
  schedule.status = 'enabled'
  ElMessage.success(`调度 "${schedule.name}" 已启用`)
}

const disableSchedule = (schedule) => {
  schedule.status = 'disabled'
  ElMessage.success(`调度 "${schedule.name}" 已禁用`)
}

const deleteSchedule = async (schedule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除调度 "${schedule.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const index = schedules.value.findIndex(s => s.id === schedule.id)
    if (index > -1) {
      schedules.value.splice(index, 1)
      total.value--
      ElMessage.success('调度删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

const saveSchedule = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingSchedule.value) {
      // 更新现有调度
      Object.assign(editingSchedule.value, scheduleForm)
      ElMessage.success('调度更新成功')
    } else {
      // 创建新调度
      const newSchedule = {
        id: Date.now(),
        ...scheduleForm,
        nextRunTime: '2024-06-01 09:00:00',
        lastRunTime: '-',
        platform: [...scheduleForm.platform]
      }
      schedules.value.unshift(newSchedule)
      total.value++
      ElMessage.success('调度创建成功')
    }
    
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(scheduleForm, {
    name: '',
    cronExpression: '',
    platform: [],
    taskContent: '',
    status: 'enabled'
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const searchSchedules = () => {
  loadSchedules()
}

const resetFilters = () => {
  filters.value = {
    status: '',
    platform: ''
  }
  loadSchedules()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadSchedules()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadSchedules()
}

const loadSchedules = () => {
  // 模拟数据
  schedules.value = [
    {
      id: 1,
      name: '每日AI分析任务',
      cronExpression: '0 9 * * *',
      nextRunTime: '2024-06-01 09:00:00',
      platform: ['skywork', 'manus'],
      status: 'enabled',
      lastRunTime: '2024-05-31 09:00:00',
      taskContent: '每日生成AI技术发展趋势分析报告'
    },
    {
      id: 2,
      name: '每小时数据监控',
      cronExpression: '0 * * * *',
      nextRunTime: '2024-06-01 15:00:00',
      platform: ['skywork'],
      status: 'enabled',
      lastRunTime: '2024-06-01 14:00:00',
      taskContent: '监控系统运行状态和性能指标'
    },
    {
      id: 3,
      name: '周报生成任务',
      cronExpression: '0 18 * * 5',
      nextRunTime: '2024-06-07 18:00:00',
      platform: ['manus'],
      status: 'disabled',
      lastRunTime: '2024-05-24 18:00:00',
      taskContent: '自动生成周度工作总结报告'
    }
  ]
  total.value = schedules.value.length
}

onMounted(() => {
  loadSchedules()
})
</script>

<style scoped>
.schedule-list {
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

.form-tip {
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}

.dialog-footer {
  text-align: right;
}
</style> 