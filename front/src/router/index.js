import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
      path: '/kpi-export',
      name: 'kpi-export',
      component: () => import('../views/KpiExportView.vue')
    }
  ]
})

export default router
