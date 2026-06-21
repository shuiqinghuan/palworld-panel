<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="server-status-card">
          <template #header>
            <div class="card-header">
              <span>服务器状态</span>
              <div class="control-buttons">
                <el-button
                  type="success"
                  @click="startServer"
                  :loading="starting"
                  :disabled="serverStatus?.status === 'running'"
                >
                  <el-icon><VideoPlay /></el-icon>
                  启动
                </el-button>
                <el-button
                  type="danger"
                  @click="stopServer"
                  :loading="stopping"
                  :disabled="serverStatus?.status !== 'running'"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止
                </el-button>
                <el-button
                  type="warning"
                  @click="saveServer"
                  :loading="saving"
                  :disabled="serverStatus?.status !== 'running'"
                >
                  <el-icon><DocumentChecked /></el-icon>
                  保存
                </el-button>
              </div>
            </div>
          </template>
          <div v-if="serverStatus" class="status-content">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="服务器名称">{{ serverStatus.name }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="serverStatus.status === 'running' ? 'success' : 'danger'">
                  {{ serverStatus.status === 'running' ? '运行中' : '已停止' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="在线玩家">{{ serverStatus.players_count }} / {{ serverStatus.max_players }}</el-descriptions-item>
              <el-descriptions-item label="CPU使用率">{{ serverStatus.cpu_usage.toFixed(2) }}%</el-descriptions-item>
              <el-descriptions-item label="内存使用">{{ serverStatus.memory_usage.toFixed(2) }} MB / {{ serverStatus.memory_total.toFixed(2) }} MB</el-descriptions-item>
              <el-descriptions-item label="运行时间">{{ formatUptime(serverStatus.uptime) }}</el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="服务器未运行" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>系统资源</span>
          </template>
          <div v-if="systemStats" class="system-stats">
            <div class="stat-item">
              <div class="stat-label">CPU使用率</div>
              <el-progress :percentage="systemStats.cpu_percent" :color="getProgressColor(systemStats.cpu_percent)" />
            </div>
            <div class="stat-item">
              <div class="stat-label">内存使用率</div>
              <el-progress :percentage="systemStats.memory_percent" :color="getProgressColor(systemStats.memory_percent)" />
            </div>
            <div class="stat-item">
              <div class="stat-label">磁盘使用率</div>
              <el-progress :percentage="systemStats.disk_percent" :color="getProgressColor(systemStats.disk_percent)" />
            </div>
            <div class="stat-item">
              <div class="stat-label">网络流量</div>
              <div class="network-stats">
                <span>发送: {{ systemStats.network_sent.toFixed(2) }} MB</span>
                <span>接收: {{ systemStats.network_recv.toFixed(2) }} MB</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="showBroadcastDialog = true" :disabled="serverStatus?.status !== 'running'">
              <el-icon><ChatDotRound /></el-icon>
              广播消息
            </el-button>
            <el-button type="warning" @click="showShutdownDialog = true" :disabled="serverStatus?.status !== 'running'">
              <el-icon><SwitchButton /></el-icon>
              定时关服
            </el-button>
            <el-button type="info" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showBroadcastDialog" title="广播消息" width="500px">
      <el-input
        v-model="broadcastMessage"
        type="textarea"
        :rows="3"
        placeholder="请输入要广播的消息"
      />
      <template #footer>
        <el-button @click="showBroadcastDialog = false">取消</el-button>
        <el-button type="primary" @click="sendBroadcast" :loading="broadcasting">发送</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showShutdownDialog" title="定时关服" width="500px">
      <el-form label-width="100px">
        <el-form-item label="倒计时(秒)">
          <el-input-number v-model="shutdownSeconds" :min="10" :max="3600" />
        </el-form-item>
        <el-form-item label="提示消息">
          <el-input v-model="shutdownMessage" placeholder="服务器即将关闭" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShutdownDialog = false">取消</el-button>
        <el-button type="danger" @click="executeShutdown" :loading="shuttingDown">确认关服</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

export default {
  name: 'Dashboard',
  setup() {
    const serverStatus = ref(null)
    const systemStats = ref(null)
    const starting = ref(false)
    const stopping = ref(false)
    const saving = ref(false)
    const showBroadcastDialog = ref(false)
    const showShutdownDialog = ref(false)
    const broadcastMessage = ref('')
    const broadcasting = ref(false)
    const shutdownSeconds = ref(60)
    const shutdownMessage = ref('服务器即将关闭')
    const shuttingDown = ref(false)
    
    let refreshInterval = null

    const loadServerStatus = async () => {
      try {
        serverStatus.value = await api.getServerStatus()
      } catch (error) {
        serverStatus.value = null
      }
    }

    const loadSystemStats = async () => {
      try {
        systemStats.value = await api.getSystemStats()
      } catch (error) {
        console.error('Failed to load system stats:', error)
      }
    }

    const refreshData = async () => {
      await Promise.all([loadServerStatus(), loadSystemStats()])
      ElMessage.success('数据已刷新')
    }

    const startServer = async () => {
      starting.value = true
      try {
        await api.startServer()
        ElMessage.success('服务器启动命令已执行')
        setTimeout(loadServerStatus, 3000)
      } catch (error) {
        console.error('Failed to start server:', error)
      } finally {
        starting.value = false
      }
    }

    const stopServer = async () => {
      stopping.value = true
      try {
        await api.stopServer()
        ElMessage.success('服务器已停止')
        serverStatus.value = null
      } catch (error) {
        console.error('Failed to stop server:', error)
      } finally {
        stopping.value = false
      }
    }

    const saveServer = async () => {
      saving.value = true
      try {
        await api.saveServer()
        ElMessage.success('服务器已保存')
      } catch (error) {
        console.error('Failed to save server:', error)
      } finally {
        saving.value = false
      }
    }

    const sendBroadcast = async () => {
      if (!broadcastMessage.value.trim()) {
        ElMessage.warning('请输入要广播的消息')
        return
      }
      
      broadcasting.value = true
      try {
        await api.broadcast(broadcastMessage.value)
        ElMessage.success('消息已广播')
        showBroadcastDialog.value = false
        broadcastMessage.value = ''
      } catch (error) {
        console.error('Failed to broadcast:', error)
      } finally {
        broadcasting.value = false
      }
    }

    const executeShutdown = async () => {
      shuttingDown.value = true
      try {
        await api.shutdownServer(shutdownSeconds.value, shutdownMessage.value)
        ElMessage.success(`服务器将在 ${shutdownSeconds.value} 秒后关闭`)
        showShutdownDialog.value = false
      } catch (error) {
        console.error('Failed to shutdown server:', error)
      } finally {
        shuttingDown.value = false
      }
    }

    const formatUptime = (timestamp) => {
      if (!timestamp) return 'N/A'
      const uptime = Date.now() / 1000 - timestamp
      const hours = Math.floor(uptime / 3600)
      const minutes = Math.floor((uptime % 3600) / 60)
      return `${hours}小时 ${minutes}分钟`
    }

    const getProgressColor = (percentage) => {
      if (percentage < 50) return '#67c23a'
      if (percentage < 80) return '#e6a23c'
      return '#f56c6c'
    }

    onMounted(() => {
      loadServerStatus()
      loadSystemStats()
      refreshInterval = setInterval(() => {
        loadServerStatus()
        loadSystemStats()
      }, 5000)
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      serverStatus,
      systemStats,
      starting,
      stopping,
      saving,
      showBroadcastDialog,
      showShutdownDialog,
      broadcastMessage,
      broadcasting,
      shutdownSeconds,
      shutdownMessage,
      shuttingDown,
      refreshData,
      startServer,
      stopServer,
      saveServer,
      sendBroadcast,
      executeShutdown,
      formatUptime,
      getProgressColor
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.status-content {
  margin-top: 20px;
}

.system-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-label {
  font-weight: bold;
  color: #606266;
}

.network-stats {
  display: flex;
  gap: 20px;
  color: #606266;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.quick-actions .el-button {
  width: 100%;
}
</style>