import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else {
        ElMessage.error(error.response.data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

export default {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  async getServerStatus() {
    const response = await api.get('/server/status')
    return response.data
  },

  async startServer() {
    const response = await api.post('/server/start')
    return response.data
  },

  async stopServer() {
    const response = await api.post('/server/stop')
    return response.data
  },

  async getPlayers() {
    const response = await api.get('/server/players')
    return response.data
  },

  async kickPlayer(steamId, reason = '') {
    const response = await api.post(`/server/kick/${steamId}?reason=${reason}`)
    return response.data
  },

  async banPlayer(steamId, reason = '') {
    const response = await api.post(`/server/ban/${steamId}?reason=${reason}`)
    return response.data
  },

  async broadcast(message) {
    const response = await api.post(`/server/broadcast?message=${encodeURIComponent(message)}`)
    return response.data
  },

  async saveServer() {
    const response = await api.post('/server/save')
    return response.data
  },

  async shutdownServer(seconds = 10, message = 'Server is shutting down') {
    const response = await api.post(`/server/shutdown?seconds=${seconds}&message=${encodeURIComponent(message)}`)
    return response.data
  },

  async getBackups() {
    const response = await api.get('/server/backups')
    return response.data
  },

  async createBackup(description = '') {
    const response = await api.post(`/server/backup?description=${encodeURIComponent(description)}`)
    return response.data
  },

  async restoreBackup(backupId) {
    const response = await api.post(`/server/backup/${backupId}/restore`)
    return response.data
  },

  async deleteBackup(backupId) {
    const response = await api.delete(`/server/backup/${backupId}`)
    return response.data
  },

  async getSystemStats() {
    const response = await api.get('/system/stats')
    return response.data
  }
}