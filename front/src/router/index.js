import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Mode2SimulationKPI from '../views/Mode2SimulationKPI.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/items',
      name: 'items',
      component: () => import('../views/ItemsView.vue')
    },
    {
      path: '/export',
      name: 'export',
      component: () => import('../views/PdfExportView.vue')
    },
    {
      path: '/mode2-simulation-kpi',
      name: 'mode2-simulation-kpi',
      component: Mode2SimulationKPI
    }
  ]
})

export default router
