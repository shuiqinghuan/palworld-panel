<template>
  <div class="players">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>在线玩家 ({{ players.length }})</span>
          <el-button type="primary" @click="loadPlayers" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="players" style="width: 100%" v-loading="loading">
        <el-table-column prop="steam_id" label="Steam ID" width="200" />
        <el-table-column prop="name" label="玩家名称" />
        <el-table-column prop="level" label="等级" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              size="small"
              type="warning"
              @click="kickPlayer(scope.row)"
            >
              踢出
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="banPlayer(scope.row)"
            >
              封禁
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showKickDialog" title="踢出玩家" width="500px">
      <el-form label-width="100px">
        <el-form-item label="玩家名称">
          <el-input v-model="currentPlayer.name" disabled />
        </el-form-item>
        <el-form-item label="Steam ID">
          <el-input v-model="currentPlayer.steam_id" disabled />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="kickReason" placeholder="请输入踢出原因(可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKickDialog = false">取消</el-button>
        <el-button type="warning" @click="confirmKick" :loading="kicking">确认踢出</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBanDialog" title="封禁玩家" width="500px">
      <el-form label-width="100px">
        <el-form-item label="玩家名称">
          <el-input v-model="currentPlayer.name" disabled />
        </el-form-item>
        <el-form-item label="Steam ID">
          <el-input v-model="currentPlayer.steam_id" disabled />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="banReason" placeholder="请输入封禁原因(可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBanDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmBan" :loading="banning">确认封禁</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

export default {
  name: 'Players',
  setup() {
    const players = ref([])
    const loading = ref(false)
    const showKickDialog = ref(false)
    const showBanDialog = ref(false)
    const currentPlayer = ref({})
    const kickReason = ref('')
    const banReason = ref('')
    const kicking = ref(false)
    const banning = ref(false)

    const loadPlayers = async () => {
      loading.value = true
      try {
        players.value = await api.getPlayers()
      } catch (error) {
        console.error('Failed to load players:', error)
      } finally {
        loading.value = false
      }
    }

    const kickPlayer = (player) => {
      currentPlayer.value = player
      kickReason.value = ''
      showKickDialog.value = true
    }

    const banPlayer = (player) => {
      currentPlayer.value = player
      banReason.value = ''
      showBanDialog.value = true
    }

    const confirmKick = async () => {
      kicking.value = true
      try {
        await api.kickPlayer(currentPlayer.value.steam_id, kickReason.value)
        ElMessage.success('玩家已踢出')
        showKickDialog.value = false
        await loadPlayers()
      } catch (error) {
        console.error('Failed to kick player:', error)
      } finally {
        kicking.value = false
      }
    }

    const confirmBan = async () => {
      banning.value = true
      try {
        await api.banPlayer(currentPlayer.value.steam_id, banReason.value)
        ElMessage.success('玩家已封禁')
        showBanDialog.value = false
        await loadPlayers()
      } catch (error) {
        console.error('Failed to ban player:', error)
      } finally {
        banning.value = false
      }
    }

    onMounted(() => {
      loadPlayers()
    })

    return {
      players,
      loading,
      showKickDialog,
      showBanDialog,
      currentPlayer,
      kickReason,
      banReason,
      kicking,
      banning,
      loadPlayers,
      kickPlayer,
      banPlayer,
      confirmKick,
      confirmBan
    }
  }
}
</script>

<style scoped>
.players {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>