<template>
  <div class="backups">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>备份管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="createBackup" :loading="creating">
              <el-icon><Plus /></el-icon>
              创建备份
            </el-button>
            <el-button @click="loadBackups" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="backups" style="width: 100%" v-loading="loading">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column label="大小" width="120">
          <template #default="scope">
            {{ formatSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="restoreBackup(scope.row)"
            >
              恢复
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteBackup(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="创建备份" width="500px">
      <el-form label-width="100px">
        <el-form-item label="备份描述">
          <el-input v-model="backupDescription" placeholder="请输入备份描述(可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateBackup" :loading="creating">确认创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

export default {
  name: 'Backups',
  setup() {
    const backups = ref([])
    const loading = ref(false)
    const creating = ref(false)
    const showCreateDialog = ref(false)
    const backupDescription = ref('')

    const loadBackups = async () => {
      loading.value = true
      try {
        backups.value = await api.getBackups()
      } catch (error) {
        console.error('Failed to load backups:', error)
      } finally {
        loading.value = false
      }
    }

    const createBackup = () => {
      backupDescription.value = ''
      showCreateDialog.value = true
    }

    const confirmCreateBackup = async () => {
      creating.value = true
      try {
        await api.createBackup(backupDescription.value)
        ElMessage.success('备份创建成功')
        showCreateDialog.value = false
        await loadBackups()
      } catch (error) {
        console.error('Failed to create backup:', error)
      } finally {
        creating.value = false
      }
    }

    const restoreBackup = (backup) => {
      ElMessageBox.confirm(
        '恢复备份将覆盖当前存档,并且会自动停止服务器。确定要继续吗?',
        '确认恢复',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await api.restoreBackup(backup.id)
          ElMessage.success('备份恢复成功')
          await loadBackups()
        } catch (error) {
          console.error('Failed to restore backup:', error)
        }
      }).catch(() => {
        ElMessage.info('已取消恢复')
      })
    }

    const deleteBackup = (backup) => {
      ElMessageBox.confirm(
        '确定要删除这个备份吗?',
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          await api.deleteBackup(backup.id)
          ElMessage.success('备份删除成功')
          await loadBackups()
        } catch (error) {
          console.error('Failed to delete backup:', error)
        }
      }).catch(() => {
        ElMessage.info('已取消删除')
      })
    }

    const formatSize = (bytes) => {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
      return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadBackups()
    })

    return {
      backups,
      loading,
      creating,
      showCreateDialog,
      backupDescription,
      loadBackups,
      createBackup,
      confirmCreateBackup,
      restoreBackup,
      deleteBackup,
      formatSize,
      formatTime
    }
  }
}
</script>

<style scoped>
.backups {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>