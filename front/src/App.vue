<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'
import PanelLayout from './components/PanelLayout.vue'
import CampaignForm from './components/form/CampaignForm.vue'
import KpiPanel from './components/results/KpiPanel.vue'
import MediaPlanPanel from './components/results/MediaPlanPanel.vue'
import MediaPlanEditMode from './components/results/MediaPlanEditMode.vue'
import ExportButton from './components/ExportButton.vue'
import Mode2SimulationKPI from './views/Mode2SimulationKPI.vue'
import LoginModal from './components/LoginModal.vue'
import CampaignActions from './components/CampaignActions.vue'
import { useCampaignStore } from './stores/campaign'
import { storeToRefs } from 'pinia'

const route = useRoute()
const navbar = ref(null)
const store = useCampaignStore()
const { lastUpdate, isComplete, isEditingPlan } = storeToRefs(store)

// Check if we're on a standalone page (export pages)
const isStandalonePage = computed(() => 
  route.path === '/export' || route.path === '/kpi-export'
)

// Get current mode from navbar
const currentMode = computed(() => navbar.value?.currentMode || 'elaboration')

// Track panel update animations
const kpiUpdating = ref(false)
const planUpdating = ref(false)

// Inverser les panneaux (Plan Média en haut par défaut)
const panelsInverted = ref(false)

const topRightTitle = computed(() => panelsInverted.value ? 'Indicateurs KPI' : 'Plan Média')
const bottomRightTitle = computed(() => panelsInverted.value ? 'Plan Média' : 'Indicateurs KPI')

function togglePanels() {
  panelsInverted.value = !panelsInverted.value
}

watch(lastUpdate, () => {
  kpiUpdating.value = true
  planUpdating.value = true
  setTimeout(() => {
    kpiUpdating.value = false
    planUpdating.value = false
  }, 1500)
})
</script>

<template>
  <!-- Standalone pages - full screen without navbar -->
  <router-view v-if="isStandalonePage" />

  <!-- Main app layout -->
  <div v-else class="h-screen flex flex-col bg-cm-gray overflow-hidden">
    <Navbar ref="navbar" class="flex-shrink-0" />
    <LoginModal />
    
    <!-- Mode KPI: Simulation KPI -->
    <div v-if="currentMode === 'kpi'" class="flex-1 min-h-0 overflow-auto">
      <Mode2SimulationKPI />
    </div>
    
    <!-- Mode Elaboration: Layout principal -->
    <div v-else class="flex-1 min-h-0 relative">
      <PanelLayout
        left-title="Configuration de la campagne"
        :top-right-title="topRightTitle"
        :bottom-right-title="bottomRightTitle"
        :edit-mode="isEditingPlan"
        :class="{ 'kpi-updating': kpiUpdating, 'plan-updating': planUpdating }"
      >
        <template #left-header-actions>
          <CampaignActions />
        </template>

        <template #left>
          <CampaignForm />
        </template>

        <template #edit-mode>
          <MediaPlanEditMode />
        </template>

        <template #top-right>
          <MediaPlanPanel v-if="!panelsInverted" />
          <KpiPanel v-else />
        </template>

        <template #bottom-right>
          <KpiPanel v-if="!panelsInverted" />
          <MediaPlanPanel v-else />
        </template>
      </PanelLayout>

      <!-- Export Button - Between the two right panels (hidden in edit mode and on mobile) -->
      <!-- Export Button Desktop - Floating center -->
      <transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="!isEditingPlan" class="hidden md:block absolute right-[25%] top-1/2 translate-x-1/2 -translate-y-1/2 z-20">
          <ExportButton />
        </div>
      </transition>

      <!-- Export Button Mobile - Sticky bottom bar -->
      <transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 translate-y-full"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-full"
      >
        <div v-if="!isEditingPlan" class="md:hidden fixed bottom-0 left-0 right-0 z-50 px-2 pb-2 pt-2 bg-cm-gray">
          <ExportButton class="w-full justify-center !rounded-xl" />
        </div>
      </transition>

      <!-- Toggle Panels Button - Coin droit (hidden in edit mode and on mobile) -->
      <transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <button
          v-if="!isEditingPlan"
          @click="togglePanels"
          class="hidden md:block absolute top-4 right-4 z-30 p-2 bg-white rounded-lg shadow-lg hover:bg-cm-gray transition-colors group"
          title="Inverser les panneaux"
        >
          <svg class="w-5 h-5 text-cm-dark transition-transform duration-300" :class="{ 'rotate-180': panelsInverted }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
          <span class="absolute right-full mr-2 top-1/2 -translate-y-1/2 px-2 py-1 bg-cm-dark text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            Inverser les panneaux
          </span>
        </button>
      </transition>
    </div>
  </div>
</template>

<style>
/* Panel update animations */
.kpi-updating .panel-top-right {
  animation: panelPulse 1.5s ease-in-out;
}

.plan-updating .panel-bottom-right {
  animation: panelPulseRed 1.5s ease-in-out;
}

@keyframes panelPulse {
  0%, 100% {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(35, 35, 36, 0.3), 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
}

@keyframes panelPulseRed {
  0%, 100% {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(226, 0, 26, 0.3), 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }
}
</style>
