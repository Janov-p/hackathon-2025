<script setup>
import { computed, ref, watch } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import KpiCard from './KpiCard.vue'

const store = useCampaignStore()
const { kpiResults, isComplete, isLoading, lastUpdate } = storeToRefs(store)

const isUpdating = ref(false)

// Watch for updates to trigger animation
watch(lastUpdate, () => {
  isUpdating.value = true
  setTimeout(() => {
    isUpdating.value = false
  }, 1000)
})

const hasData = computed(() => {
  return kpiResults.value.audienceCumulee > 0
})

// Donut chart data
const donutData = computed(() => {
  const budget = store.formData.budget
  const rep = store.formData.repartition
  return [
    { label: 'Print', value: rep.print, color: '#6366f1' },
    { label: 'Digital', value: rep.digital, color: '#10b981' },
    { label: 'RS', value: rep.reseaux, color: '#ec4899' },
    { label: 'Event', value: rep.event, color: '#f59e0b' }
  ]
})

// Calculate donut segments
const donutSegments = computed(() => {
  let cumulative = 0
  return donutData.value.map(item => {
    const start = cumulative
    cumulative += item.value
    return {
      ...item,
      start,
      end: cumulative
    }
  })
})

function getDonutPath(start, end) {
  const startAngle = (start / 100) * 360 - 90
  const endAngle = (end / 100) * 360 - 90
  const largeArc = end - start > 50 ? 1 : 0
  
  const startX = 50 + 40 * Math.cos((startAngle * Math.PI) / 180)
  const startY = 50 + 40 * Math.sin((startAngle * Math.PI) / 180)
  const endX = 50 + 40 * Math.cos((endAngle * Math.PI) / 180)
  const endY = 50 + 40 * Math.sin((endAngle * Math.PI) / 180)
  
  return `M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArc} 1 ${endX} ${endY} Z`
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Empty state -->
    <div v-if="!hasData" class="flex-1 flex items-center justify-center">
      <div class="text-center p-8">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">KPI en attente</h3>
        <p class="text-sm text-gray-500">Complétez le formulaire pour voir les indicateurs de performance</p>
      </div>
    </div>

    <!-- KPI Content -->
    <div v-else class="space-y-4 overflow-auto">
      <!-- Impact & Exposition -->
      <div>
        <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          Impact & Exposition
        </h4>
        <div class="grid grid-cols-2 gap-3">
          <KpiCard
            title="Audience Cumulée"
            :value="kpiResults.audienceCumulee"
            unit="contacts"
            color="indigo"
            icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            tooltip="Nombre total de personnes touchées par la campagne"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="Taux de Couverture"
            :value="kpiResults.tauxCouverture"
            unit="%"
            color="emerald"
            icon="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            tooltip="Pourcentage de la cible touchée au moins une fois"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="Fréquence Moyenne"
            :value="kpiResults.frequenceMoyenne"
            unit="x"
            color="amber"
            icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            tooltip="Nombre moyen d'expositions par personne"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="GRP"
            :value="kpiResults.grp"
            color="pink"
            icon="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
            tooltip="Gross Rating Point - Pression publicitaire"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="Impressions"
            :value="kpiResults.impressions"
            color="indigo"
            icon="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            tooltip="Nombre total d'affichages publicitaires"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="Vues Vidéo"
            :value="kpiResults.vuesVideo"
            color="emerald"
            icon="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            tooltip="Nombre estimé de vues vidéo"
            :is-updating="isUpdating"
          />
        </div>
      </div>

      <!-- Efficacité Financière -->
      <div>
        <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Efficacité Financière
        </h4>
        <div class="grid grid-cols-2 gap-3">
          <KpiCard
            title="Coût GRP"
            :value="kpiResults.coutGrp"
            unit="€"
            color="amber"
            tooltip="Coût pour obtenir 1 point de GRP"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="CPM Global"
            :value="kpiResults.cpmGlobal"
            unit="€"
            color="pink"
            tooltip="Coût pour 1000 impressions"
            :is-updating="isUpdating"
          />
        </div>
      </div>

      <!-- Engagement & Action -->
      <div>
        <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
          </svg>
          Engagement & Action
        </h4>
        <div class="grid grid-cols-2 gap-3">
          <KpiCard
            title="Clics Estimés"
            :value="kpiResults.clicsEstimes"
            color="indigo"
            tooltip="Nombre de clics attendus sur les publicités"
            :is-updating="isUpdating"
          />
          <KpiCard
            title="CTR Moyen"
            :value="kpiResults.ctrMoyen"
            unit="%"
            color="emerald"
            tooltip="Taux de clic moyen prévisionnel"
            :is-updating="isUpdating"
          />
        </div>
      </div>

      <!-- Répartition Stratégique - Donut Chart -->
      <div>
        <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
          Répartition Stratégique
        </h4>
        <div class="flex items-center gap-4">
          <!-- Donut Chart -->
          <div class="relative w-32 h-32 flex-shrink-0">
            <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
              <path
                v-for="(segment, index) in donutSegments"
                :key="index"
                :d="getDonutPath(segment.start, segment.end)"
                :fill="segment.color"
                class="transition-all duration-500"
              />
              <circle cx="50" cy="50" r="25" fill="white" />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-xs font-bold text-gray-600">Budget</span>
            </div>
          </div>
          <!-- Legend -->
          <div class="flex-1 space-y-2">
            <div
              v-for="item in donutData"
              :key="item.label"
              class="flex items-center justify-between text-sm"
            >
              <div class="flex items-center gap-2">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: item.color }"
                ></div>
                <span class="text-gray-600">{{ item.label }}</span>
              </div>
              <span class="font-semibold text-gray-800">{{ item.value }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isLoading" class="absolute inset-0 bg-white/80 flex items-center justify-center rounded-2xl">
        <div class="flex items-center gap-2 text-indigo-600">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="font-medium">Calcul en cours...</span>
        </div>
      </div>
    </transition>
  </div>
</template>
