<template>
  <div class="task-create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建新任务</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="taskForm"
        :rules="rules"
        label-width="120px"
        style="max-width: 800px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题" />
        </el-form-item>

        <el-form-item label="目标平台" prop="platforms">
          <el-checkbox-group v-model="taskForm.platforms">
            <el-checkbox label="skywork">Skywork</el-checkbox>
            <el-checkbox label="manus">Manus</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="任务内容" prop="content">
          <el-input
            v-model="taskForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入详细的任务描述..."
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="taskForm.priority" placeholder="选择优先级">
            <el-option label="低" :value="1" />
            <el-option label="中" :value="2" />
            <el-option label="高" :value="3" />
            <el-option label="紧急" :value="4" />
          </el-select>
        </el-form-item>

        <el-form-item label="计划执行时间">
          <el-date-picker
            v-model="taskForm.scheduledAt"
            type="datetime"
            placeholder="选择执行时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitTask" :loading="submitting">
            创建任务
          </el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button @click="goBack">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const taskForm = reactive({
  title: '',
  platforms: [],
  content: '',
  priority: 2,
  scheduledAt: null
})

const rules = {
  title: [
    { required: true, message: '请输入任务标题', trigger: 'blur' }
  ],
  platforms: [
    { 
      type: 'array', 
      required: true, 
      message: '请选择至少一个平台', 
      trigger: 'change' 
    }
  ],
  content: [
    { required: true, message: '请输入任务内容', trigger: 'blur' },
    { min: 10, message: '任务内容至少10个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

const submitTask = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('任务创建成功!')
    router.push('/tasks/list')
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.task-create {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 