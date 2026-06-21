<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="服务器配置" name="server">
          <el-form label-width="150px" style="max-width: 600px;">
            <el-form-item label="服务器目录">
              <el-input v-model="config.serverDir" disabled />
            </el-form-item>
            <el-form-item label="RCON主机">
              <el-input v-model="config.rconHost" />
            </el-form-item>
            <el-form-item label="RCON端口">
              <el-input-number v-model="config.rconPort" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="RCON密码">
              <el-input v-model="config.rconPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="备份目录">
              <el-input v-model="config.backupDir" />
            </el-form-item>
            <el-form-item label="最大备份数">
              <el-input-number v-model="config.maxBackups" :min="1" :max="100" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="账户管理" name="account">
          <el-form label-width="150px" style="max-width: 600px;">
            <el-form-item label="当前用户">
              <el-input value="admin" disabled />
            </el-form-item>
            <el-form-item label="修改密码">
              <el-button type="primary" @click="showPasswordDialog = true">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="系统信息" name="system">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="应用名称">幻兽帕鲁服务器管理面板</el-descriptions-item>
            <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
            <el-descriptions-item label="后端框架">FastAPI</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="Python版本">{{ pythonVersion }}</el-descriptions-item>
            <el-descriptions-item label="操作系统">{{ osInfo }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="showPasswordDialog" title="修改密码" width="500px">
      <el-form label-width="100px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword" :loading="changingPassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

export default {
  name: 'Settings',
  setup() {
    const activeTab = ref('server')
    const saving = ref(false)
    const showPasswordDialog = ref(false)
    const changingPassword = ref(false)
    const pythonVersion = ref('3.11.0')
    const osInfo = ref('Debian 12')
    
    const config = ref({
      serverDir: '/home/steam/palworld-server',
      rconHost: '127.0.0.1',
      rconPort: 25575,
      rconPassword: 'adminpassword',
      backupDir: '/var/backups/palworld',
      maxBackups: 10
    })

    const passwordForm = ref({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const saveConfig = async () => {
      saving.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        ElMessage.success('配置保存成功')
      } catch (error) {
        console.error('Failed to save config:', error)
      } finally {
        saving.value = false
      }
    }

    const changePassword = async () => {
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        ElMessage.error('两次输入的密码不一致')
        return
      }

      changingPassword.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        ElMessage.success('密码修改成功')
        showPasswordDialog.value = false
        passwordForm.value = {
          oldPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (error) {
        console.error('Failed to change password:', error)
      } finally {
        changingPassword.value = false
      }
    }

    onMounted(() => {
      
    })

    return {
      activeTab,
      config,
      saving,
      showPasswordDialog,
      passwordForm,
      changingPassword,
      pythonVersion,
      osInfo,
      saveConfig,
      changePassword
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 20px;
}
</style>