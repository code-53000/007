import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'
import router from '@/router'

const request = axios.create({
  baseURL: '',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}
      let msg = ''

      if (Array.isArray(data.detail)) {
        msg = data.detail.map(d => d.msg || d.message || String(d)).join('；')
      } else if (typeof data.detail === 'object' && data.detail) {
        msg = data.detail.message || data.detail.msg || JSON.stringify(data.detail)
      } else if (typeof data.detail === 'string') {
        msg = data.detail
      } else {
        msg = data.message || data.msg || error.message
      }

      if (!msg) msg = '请求失败'

      if (status === 401) {
        const url = error.config?.url || ''
        const isAuthRequest = url.includes('/auth/login') || url.includes('/auth/register')
        if (isAuthRequest) {
          showToast({ type: 'fail', message: msg })
        } else {
          const userStore = useUserStore()
          userStore.logout()
          showToast({ type: 'fail', message: '登录已过期，请重新登录' })
          router.replace({ name: 'Login' })
        }
      } else if (status === 422) {
        showToast({ type: 'fail', message: '参数错误：' + msg })
      } else if (status === 400 || status === 403 || status === 404 || status === 409) {
        showToast({ type: 'fail', message: msg })
      } else if (status >= 500) {
        showToast({ type: 'fail', message: '服务器错误：' + msg })
      } else {
        showToast({ type: 'fail', message: msg })
      }
    } else if (error.code === 'ECONNABORTED') {
      showToast({ type: 'fail', message: '请求超时，请稍后重试' })
    } else if (error.message && error.message.includes('Network Error')) {
      showToast({ type: 'fail', message: '网络连接失败，请检查网络' })
    } else {
      showToast({ type: 'fail', message: error.message || '网络异常，请稍后重试' })
    }
    return Promise.reject(error)
  }
)

export default request
