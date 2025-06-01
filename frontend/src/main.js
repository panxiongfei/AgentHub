import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import './style.css'
import './assets/platform-icons.css'

console.log('🚀 正在启动 AgentHub 前端应用...')

try {
  const app = createApp(App)

  // 注册所有图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(createPinia())
  app.use(router)
  app.use(ElementPlus, {
    locale: zhCn,
  })

  console.log('✅ 应用配置完成，正在挂载...')
  app.mount('#app')
  console.log('🎉 AgentHub 前端应用启动成功!')
} catch (error) {
  console.error('❌ 应用启动失败:', error)
} 