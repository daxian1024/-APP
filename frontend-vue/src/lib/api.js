import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.message ||
      '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  },
)

export const authApi = {
  register(data) {
    return api.post('/auth/register', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  refresh() {
    return api.post('/auth/refresh')
  },
  me() {
    return api.get('/auth/me')
  },
  updateMe(data) {
    return api.patch('/auth/me', data)
  },
}

export const serviceApi = {
  list() {
    return api.get('/services')
  },
  popular() {
    return api.get('/services/popular')
  },
}

export const addressApi = {
  list() {
    return api.get('/addresses')
  },
  create(data) {
    return api.post('/addresses', data)
  },
  update(id, data) {
    return api.patch(`/addresses/${id}`, data)
  },
  remove(id) {
    return api.delete(`/addresses/${id}`)
  },
}

export const orderApi = {
  list() {
    return api.get('/orders')
  },
  create(data) {
    return api.post('/orders', data)
  },
  timeline(id) {
    return api.get(`/orders/${id}/timeline`)
  },
  pay(id, data) {
    return api.post(`/orders/${id}/pay`, data)
  },
}

export const feedbackApi = {
  createReview(data) {
    return api.post('/feedback/reviews', data)
  },
  listReviews() {
    return api.get('/feedback/reviews')
  },
  createComplaint(data) {
    return api.post('/feedback/complaints', data)
  },
  listComplaints() {
    return api.get('/feedback/complaints')
  },
}

export const adminApi = {
  listOrders() {
    return api.get('/admin/orders')
  },
  assignNurse(orderId, data) {
    return api.patch(`/admin/orders/${orderId}/assign`, data)
  },
  updateOrderStatus(orderId, data) {
    return api.patch(`/admin/orders/${orderId}/status`, data)
  },
  sendNotification(data) {
    return api.post('/admin/notifications/send', data)
  },
}

export const analyticsApi = {
  getOverview() {
    return api.get('/analytics/overview')
  },
  getSummary() {
    return api.get('/analytics/summary')
  },
  getOrdersTrend(days = 7) {
    return api.get('/analytics/orders-trend', { params: { days } })
  },
  getServiceDistribution() {
    return api.get('/analytics/service-distribution')
  },
  getOrderStatusDistribution() {
    return api.get('/analytics/order-status-distribution')
  },
  getNurseRanking() {
    return api.get('/analytics/nurse-ranking')
  },
  getComplaintTrend(days = 7) {
    return api.get('/analytics/complaint-trend', { params: { days } })
  },
}

export default api