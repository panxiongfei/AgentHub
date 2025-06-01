import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Monitor' }
      }
    ]
  },
  {
    path: '/platforms',
    component: Layout,
    redirect: '/platforms/list',
    meta: { title: '平台管理', icon: 'Platform' },
    children: [
      {
        path: '/platforms/list',
        name: 'PlatformList',
        component: () => import('@/views/Platforms/index.vue'),
        meta: { title: '平台列表', icon: 'List' }
      },
      {
        path: '/platforms/browser',
        name: 'BrowserManager',
        component: () => import('@/views/Platforms/BrowserManager.vue'),
        meta: { title: '浏览器管理', icon: 'Monitor' }
      }
    ]
  },
  {
    path: '/tasks',
    component: Layout,
    redirect: '/tasks/list',
    meta: { title: '任务管理', icon: 'Document' },
    children: [
      {
        path: '/tasks/list',
        name: 'TaskList',
        component: () => import('@/views/Tasks/index.vue'),
        meta: { title: '任务列表', icon: 'List' }
      },
      {
        path: '/tasks/create',
        name: 'TaskCreate',
        component: () => import('@/views/Tasks/Create.vue'),
        meta: { title: '创建任务', icon: 'Plus' }
      },
      {
        path: '/tasks/detail/:id',
        name: 'TaskDetail',
        component: () => import('@/views/Tasks/Detail.vue'),
        meta: { title: '任务详情', icon: 'View' },
        props: true
      }
    ]
  },
  {
    path: '/history',
    component: Layout,
    redirect: '/history/list',
    meta: { title: '历史任务', icon: 'Clock' },
    children: [
      {
        path: '/history/list',
        name: 'HistoryList',
        component: () => import('@/views/History/index.vue'),
        meta: { title: '历史列表', icon: 'List' }
      },
      {
        path: '/history/download',
        name: 'HistoryDownload',
        component: () => import('@/views/History/Download.vue'),
        meta: { title: '批量下载', icon: 'Download' }
      },
      {
        path: '/history/detail/:platform/:taskId',
        name: 'HistoryDetail',
        component: () => import('@/views/History/Detail.vue'),
        meta: { title: '历史详情', icon: 'View' },
        props: true
      }
    ]
  },
  {
    path: '/schedule',
    component: Layout,
    redirect: '/schedule/list',
    meta: { title: '调度管理', icon: 'Timer' },
    children: [
      {
        path: '/schedule/list',
        name: 'ScheduleList',
        component: () => import('@/views/Schedule/index.vue'),
        meta: { title: '调度列表', icon: 'List' }
      }
    ]
  },
  {
    path: '/system',
    component: Layout,
    redirect: '/system/settings',
    meta: { title: '系统设置', icon: 'Setting' },
    children: [
      {
        path: '/system/settings',
        name: 'SystemSettings',
        component: () => import('@/views/System/Settings.vue'),
        meta: { title: '系统设置', icon: 'Tools' }
      },
      {
        path: '/system/logs',
        name: 'SystemLogs',
        component: () => import('@/views/System/Logs.vue'),
        meta: { title: '系统日志', icon: 'Document' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 