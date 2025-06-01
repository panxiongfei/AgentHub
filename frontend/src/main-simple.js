import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import AppSimple from './App-simple.vue'
import router from './router'

console.log('🚀 正在启动简化版 AgentHub 前端应用...')

try {
  const app = createApp(AppSimple)

  // 注册所有图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(router)
  app.use(ElementPlus, {
    locale: zhCn,
  })

  console.log('✅ 简化版应用配置完成，正在挂载...')
  app.mount('#app')
  console.log('🎉 简化版 AgentHub 前端应用启动成功!')
} catch (error) {
  console.error('❌ 简化版应用启动失败:', error)
} 