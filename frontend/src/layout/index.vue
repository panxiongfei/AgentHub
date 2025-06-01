<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo-container">
        <div class="logo">
          <el-icon v-if="!isCollapse" size="28" color="#409EFF">
            <Platform />
          </el-icon>
          <span v-if="!isCollapse" class="logo-text">AgentHub</span>
        </div>
      </div>
      
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        :unique-opened="true"
        class="sidebar-menu"
        router
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <el-sub-menu v-if="route.children && route.children.length > 1" :index="route.path">
            <template #title>
              <el-icon>
                <component :is="route.meta?.icon || 'Menu'" />
              </el-icon>
              <span>{{ route.meta?.title }}</span>
            </template>
            <el-menu-item
              v-for="child in route.children"
              :key="child.path"
              :index="child.path"
            >
              <el-icon>
                <component :is="child.meta?.icon || 'Document'" />
              </el-icon>
              <span>{{ child.meta?.title }}</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item
            v-else
            :index="route.children?.[0]?.path || route.path"
          >
            <el-icon>
              <component :is="route.meta?.icon || route.children?.[0]?.meta?.icon || 'Menu'" />
            </el-icon>
            <span>{{ route.meta?.title || route.children?.[0]?.meta?.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="sidebar-toggle"
          >
            <el-icon size="18">
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 系统状态 -->
          <div class="system-status">
            <el-tooltip :content="systemStore.isOnline ? '系统正常' : '系统异常'" placement="bottom">
              <div class="status-indicator">
                <div :class="['status-dot', systemStore.isOnline ? 'online' : 'offline']"></div>
                <span class="status-text">{{ systemStore.isOnline ? '在线' : '离线' }}</span>
              </div>
            </el-tooltip>
          </div>

          <!-- 用户菜单 -->
          <el-dropdown>
            <div class="user-info">
              <el-avatar size="small" src="/avatar.jpg">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">管理员</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import {
  Platform,
  Expand,
  Fold,
  User,
  SwitchButton,
  Monitor,
  Document,
  Clock,
  Timer,
  Setting,
  List,
  Plus,
  View,
  Download,
  Tools
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const systemStore = useSystemStore()

const isCollapse = ref(false)

const currentRoute = computed(() => route)

const menuRoutes = computed(() => {
  return router.getRoutes().filter(route => 
    route.meta?.title && !route.path.includes(':')
  )
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const handleLogout = () => {
  // 处理退出登录
  console.log('退出登录')
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.sidebar {
  background: #001428;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #304156;
  padding: 0 15px;
}

.logo {
  display: flex;
  align-items: center;
  color: #409EFF;
  font-weight: bold;
  gap: 8px;
}

.logo-text {
  font-size: 16px;
  white-space: nowrap;
}

.sidebar-menu {
  border: none;
  background: #001428;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #263445;
  color: #409EFF;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #409EFF;
  color: #fff;
}

.sidebar-menu :deep(.el-sub-menu .el-sub-menu__title) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-sub-menu .el-sub-menu__title:hover) {
  background-color: #263445;
  color: #409EFF;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.sidebar-toggle {
  padding: 8px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.system-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background-color: #67c23a;
}

.status-dot.offline {
  background-color: #f56c6c;
}

.status-text {
  font-size: 12px;
  color: #909399;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style> 