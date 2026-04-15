import { defineStore } from 'pinia'
import api from '../lib/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || '',
    refreshToken: localStorage.getItem('refresh_token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    avatar: localStorage.getItem('avatar') || '',
    bio: localStorage.getItem('bio') || '',
  }),
  getters: {
    isLoggedIn: (s) => !!s.accessToken,
    displayName: (s) => s.user?.username || '未登录用户',
  },
  actions: {
    setAccessToken(token) {
      this.accessToken = token || ''
      localStorage.setItem('access_token', this.accessToken)
    },
    setTokens(access, refresh) {
      this.accessToken = access || ''
      this.refreshToken = refresh || ''
      localStorage.setItem('access_token', this.accessToken)
      localStorage.setItem('refresh_token', this.refreshToken)
    },
    async login(account, password) {
      const res = await api.post('/auth/login', { account, password })
      const data = res.data?.data || {}
      this.setTokens(data.access_token, data.refresh_token)
      this.user = data.user || null
      localStorage.setItem('user', JSON.stringify(this.user))
      return data
    },
    async register(username, phone, password) {
      await api.post('/auth/register', { username, phone, password, role: 'elderly' })
      return this.login(username, password)
    },
    async fetchMe() {
      if (!this.accessToken) return null
      const res = await api.get('/auth/me')
      this.user = res.data?.data || null
      localStorage.setItem('user', JSON.stringify(this.user))
      return this.user
    },
    async updateProfile(payload) {
      const res = await api.patch('/auth/me', { username: payload.username })
      this.user = res.data?.data || this.user
      localStorage.setItem('user', JSON.stringify(this.user))
      this.avatar = payload.avatar || this.avatar
      this.bio = payload.bio || this.bio
      localStorage.setItem('avatar', this.avatar)
      localStorage.setItem('bio', this.bio)
    },
    logout() {
      this.accessToken = ''
      this.refreshToken = ''
      this.user = null
      this.avatar = ''
      this.bio = ''
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      localStorage.removeItem('avatar')
      localStorage.removeItem('bio')
    },
  },
})
