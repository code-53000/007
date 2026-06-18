import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false, title: '注册' },
  },
  {
    path: '/',
    name: 'Fridge',
    component: () => import('@/views/FridgeView.vue'),
    meta: { requiresAuth: true, title: '冰箱格子', tabbar: true },
  },
  {
    path: '/box/:id',
    name: 'BoxDetail',
    component: () => import('@/views/BoxDetail.vue'),
    meta: { requiresAuth: true, title: '格子详情' },
  },
  {
    path: '/food/add',
    name: 'AddFood',
    component: () => import('@/views/AddFood.vue'),
    meta: { requiresAuth: true, title: '登记食物' },
  },
  {
    path: '/food/edit/:id',
    name: 'EditFood',
    component: () => import('@/views/AddFood.vue'),
    meta: { requiresAuth: true, title: '编辑食物' },
  },
  {
    path: '/expiry',
    name: 'Expiry',
    component: () => import('@/views/ExpiryView.vue'),
    meta: { requiresAuth: true, title: '过期提醒', tabbar: true },
  },
  {
    path: '/shared',
    name: 'Shared',
    component: () => import('@/views/SharedView.vue'),
    meta: { requiresAuth: true, title: '共享空间', tabbar: true },
  },
  {
    path: '/cleanup',
    name: 'Cleanup',
    component: () => import('@/views/CleanupView.vue'),
    meta: { requiresAuth: true, title: '清理记录' },
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/LogsView.vue'),
    meta: { requiresAuth: true, title: '操作记录' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true, title: '我的', tabbar: true },
  },
  {
    path: '/box/add',
    name: 'AddBox',
    component: () => import('@/views/AddBox.vue'),
    meta: { requiresAuth: true, title: '新建格子' },
  },
  {
    path: '/seasoning/add',
    name: 'AddSeasoning',
    component: () => import('@/views/AddSeasoning.vue'),
    meta: { requiresAuth: true, title: '添加调料' },
  },
  {
    path: '/seasoning/edit/:id',
    name: 'EditSeasoning',
    component: () => import('@/views/AddSeasoning.vue'),
    meta: { requiresAuth: true, title: '编辑调料' },
  },
  {
    path: '/space-notice/add',
    name: 'AddSpaceNotice',
    component: () => import('@/views/AddSpaceNotice.vue'),
    meta: { requiresAuth: true, title: '发布空间预告' },
  },
  {
    path: '/space-notice/edit/:id',
    name: 'EditSpaceNotice',
    component: () => import('@/views/AddSpaceNotice.vue'),
    meta: { requiresAuth: true, title: '编辑空间预告' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  document.title = to.meta.title ? `${to.meta.title} - 冰箱管家` : '冰箱管家'

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
