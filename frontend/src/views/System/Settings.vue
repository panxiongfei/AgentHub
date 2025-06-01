<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="card">
        <!-- 基础设置 -->
        <el-tab-pane label="基础设置" name="basic">
          <el-form
            ref="basicFormRef"
            :model="basicSettings"
            :rules="basicRules"
            label-width="150px"
            style="max-width: 600px"
          >
            <el-form-item label="系统名称" prop="systemName">
              <el-input v-model="basicSettings.systemName" />
            </el-form-item>

            <el-form-item label="系统版本">
              <el-input v-model="basicSettings.version" disabled />
            </el-form-item>

            <el-form-item label="默认语言">
              <el-select v-model="basicSettings.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>

            <el-form-item label="时区设置">
              <el-select v-model="basicSettings.timezone">
                <el-option label="Asia/Shanghai" value="Asia/Shanghai" />
                <el-option label="America/New_York" value="America/New_York" />
                <el-option label="Europe/London" value="Europe/London" />
              </el-select>
            </el-form-item>

            <el-form-item label="自动保存">
              <el-switch v-model="basicSettings.autoSave" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
              <el-button @click="resetBasicSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 平台配置 -->
        <el-tab-pane label="平台配置" name="platform">
          <div class="platform-config">
            <div v-for="platform in platformSettings" :key="platform.name" class="platform-item">
              <el-card>
                <template #header>
                  <div class="platform-header">
                    <span>{{ platform.displayName }}</span>
                    <el-switch v-model="platform.enabled" />
                  </div>
                </template>

                <el-form label-width="120px">
                  <el-form-item label="平台地址">
                    <el-input v-model="platform.url" />
                  </el-form-item>

                  <el-form-item label="调试端口">
                    <el-input-number v-model="platform.debugPort" :min="1000" :max="9999" />
                  </el-form-item>

                  <el-form-item label="连接超时">
                    <el-input-number v-model="platform.timeout" :min="5" :max="60" />
                    <span class="unit">秒</span>
                  </el-form-item>

                  <el-form-item label="重试次数">
                    <el-input-number v-model="platform.retryCount" :min="0" :max="5" />
                  </el-form-item>

                  <el-form-item label="状态">
                    <el-tag :type="platform.status === 'connected' ? 'success' : 'danger'">
                      {{ platform.status === 'connected' ? '已连接' : '未连接' }}
                    </el-tag>
                    <el-button type="primary" size="small" @click="testConnection(platform)" style="margin-left: 10px">
                      测试连接
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </div>

            <div class="save-section">
              <el-button type="primary" @click="savePlatformSettings">保存平台配置</el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 任务配置 -->
        <el-tab-pane label="任务配置" name="task">
          <el-form
            ref="taskFormRef"
            :model="taskSettings"
            label-width="150px"
            style="max-width: 600px"
          >
            <el-form-item label="最大并发任务数">
              <el-input-number v-model="taskSettings.maxConcurrentTasks" :min="1" :max="20" />
            </el-form-item>

            <el-form-item label="任务超时时间">
              <el-input-number v-model="taskSettings.taskTimeout" :min="30" :max="300" />
              <span class="unit">秒</span>
            </el-form-item>

            <el-form-item label="重试间隔">
              <el-input-number v-model="taskSettings.retryInterval" :min="1" :max="60" />
              <span class="unit">秒</span>
            </el-form-item>

            <el-form-item label="结果保存路径">
              <el-input v-model="taskSettings.resultPath" />
            </el-form-item>

            <el-form-item label="自动清理">
              <el-switch v-model="taskSettings.autoCleanup" />
            </el-form-item>

            <el-form-item label="清理间隔" v-if="taskSettings.autoCleanup">
              <el-input-number v-model="taskSettings.cleanupInterval" :min="1" :max="30" />
              <span class="unit">天</span>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveTaskSettings">保存设置</el-button>
              <el-button @click="resetTaskSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <el-form
            ref="securityFormRef"
            :model="securitySettings"
            label-width="150px"
            style="max-width: 600px"
          >
            <el-form-item label="启用访问控制">
              <el-switch v-model="securitySettings.enableAuth" />
            </el-form-item>

            <el-form-item label="API密钥" v-if="securitySettings.enableAuth">
              <el-input
                v-model="securitySettings.apiKey"
                type="password"
                show-password
                placeholder="请输入API密钥"
              />
            </el-form-item>

            <el-form-item label="加密数据">
              <el-switch v-model="securitySettings.encryptData" />
            </el-form-item>

            <el-form-item label="日志记录级别">
              <el-select v-model="securitySettings.logLevel">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>

            <el-form-item label="敏感信息脱敏">
              <el-switch v-model="securitySettings.maskSensitiveData" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
              <el-button @click="resetSecuritySettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

// 基础设置
const basicFormRef = ref()
const basicSettings = reactive({
  systemName: 'AgentHub',
  version: 'v2.1.0',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  autoSave: true
})

const basicRules = {
  systemName: [
    { required: true, message: '请输入系统名称', trigger: 'blur' }
  ]
}

// 平台配置
const platformSettings = ref([
  {
    name: 'skywork',
    displayName: 'Skywork',
    enabled: true,
    url: 'https://skywork.ai',
    debugPort: 9222,
    timeout: 30,
    retryCount: 3,
    status: 'connected'
  },
  {
    name: 'manus',
    displayName: 'Manus',
    enabled: true,
    url: 'https://manus.ai',
    debugPort: 9223,
    timeout: 30,
    retryCount: 3,
    status: 'disconnected'
  }
])

// 任务配置
const taskFormRef = ref()
const taskSettings = reactive({
  maxConcurrentTasks: 5,
  taskTimeout: 120,
  retryInterval: 10,
  resultPath: 'data/results',
  autoCleanup: true,
  cleanupInterval: 7
})

// 安全设置
const securityFormRef = ref()
const securitySettings = reactive({
  enableAuth: false,
  apiKey: '',
  encryptData: true,
  logLevel: 'info',
  maskSensitiveData: true
})

const saveBasicSettings = () => {
  if (!basicFormRef.value) return
  
  basicFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success('基础设置保存成功')
    }
  })
}

const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    systemName: 'AgentHub',
    version: 'v2.1.0',
    language: 'zh-CN',
    timezone: 'Asia/Shanghai',
    autoSave: true
  })
}

const testConnection = async (platform) => {
  try {
    ElMessage.info(`正在测试 ${platform.displayName} 连接...`)
    
    // 模拟连接测试
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    platform.status = Math.random() > 0.3 ? 'connected' : 'disconnected'
    
    if (platform.status === 'connected') {
      ElMessage.success(`${platform.displayName} 连接测试成功`)
    } else {
      ElMessage.error(`${platform.displayName} 连接测试失败`)
    }
  } catch (error) {
    ElMessage.error(`连接测试异常: ${error.message}`)
  }
}

const savePlatformSettings = () => {
  ElMessage.success('平台配置保存成功')
}

const saveTaskSettings = () => {
  ElMessage.success('任务配置保存成功')
}

const resetTaskSettings = () => {
  Object.assign(taskSettings, {
    maxConcurrentTasks: 5,
    taskTimeout: 120,
    retryInterval: 10,
    resultPath: 'data/results',
    autoCleanup: true,
    cleanupInterval: 7
  })
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功')
}

const resetSecuritySettings = () => {
  Object.assign(securitySettings, {
    enableAuth: false,
    apiKey: '',
    encryptData: true,
    logLevel: 'info',
    maskSensitiveData: true
  })
}

onMounted(() => {
  // 页面加载时的初始化逻辑
})
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-config {
  margin-top: 20px;
}

.platform-item {
  margin-bottom: 20px;
}

.platform-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.save-section {
  margin-top: 30px;
  text-align: center;
}

.unit {
  margin-left: 8px;
  color: #666;
  font-size: 14px;
}
</style> 