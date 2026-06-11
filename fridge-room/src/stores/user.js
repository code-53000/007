import { defineStore } from 'pinia'
import { login, register, getProfile, updateProfile, getRoommates } from '@/api/auth'
import { showToast } from 'vant'

const STORAGE_KEY = 'fridge_user_token'
const USER_KEY = 'fridge_user_info'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(STORAGE_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
    roommates: [],
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
    userId: (state) => state.user?.id,
    avatarColor: (state) => state.user?.avatar_color || '#1989fa',
  },

  actions: {
    async doLogin(form) {
      const res = await login(form)
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem(STORAGE_KEY, res.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(res.user))
      return res
    },

    async doRegister(form) {
      const res = await register(form)
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem(STORAGE_KEY, res.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(res.user))
      return res
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(USER_KEY)
    },

    async fetchProfile() {
      const user = await getProfile()
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      return user
    },

    async updateUser(data) {
      const user = await updateProfile(data)
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      showToast('更新成功')
      return user
    },

    async fetchRoommates() {
      this.roommates = await getRoommates()
      return this.roommates
    },

    restoreAuth() {
      const token = localStorage.getItem(STORAGE_KEY)
      const user = localStorage.getItem(USER_KEY)
      if (token) this.token = token
      if (user) this.user = JSON.parse(user)
    },
  },
})
