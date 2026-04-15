import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

let refreshing = false
let queue = []

function resolveQueue(token) {
  queue.forEach((cb) => cb(token))
  queue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const original = error.config || {}
    const status = error?.response?.status

    if (status === 401 && !original._retry && auth.refreshToken) {
      original._retry = true

      if (refreshing) {
        return new Promise((resolve) => {
          queue.push((newToken) => {
            original.headers = original.headers || {}
            original.headers.Authorization = `Bearer ${newToken}`
            resolve(api(original))
          })
        })
      }

      refreshing = true
      try {
        const refreshResp = await axios.post(`${API_BASE}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${auth.refreshToken}` },
        })
        const newToken = refreshResp.data?.data?.access_token
        if (!newToken) throw new Error('refresh failed')

        auth.setAccessToken(newToken)
        resolveQueue(newToken)
        original.headers = original.headers || {}
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      } catch (_e) {
        auth.logout()
        return Promise.reject(error)
      } finally {
        refreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default api
