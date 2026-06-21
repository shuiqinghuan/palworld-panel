import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import Players from './views/Players.vue'
import Backups from './views/Backups.vue'
import Settings from './views/Settings.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/players', name: 'Players', component: Players },
  { path: '/backups', name: 'Backups', component: Backups },
  { path: '/settings', name: 'Settings', component: Settings }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router