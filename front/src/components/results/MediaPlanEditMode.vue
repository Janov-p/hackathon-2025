<script setup>
import { ref, computed } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import RepartitionEditor from './RepartitionEditor.vue'
import SupportsEditor from './SupportsEditor.vue'
import FormatsEditor from './FormatsEditor.vue'
import CalendrierEditor from './CalendrierEditor.vue'

const store = useCampaignStore()
const { isLoading, modifiedPlan, budgetFinal, remise } = storeToRefs(store)

const emit = defineEmits(['close', 'save'])

const activeTab = ref('repartition')

const tabs = [
  { id: 'repartition', label: 'Répartition', icon: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z' },
  { id: 'supports', label: 'Supports', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'formats', label: 'Formats', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' },
  { id: 'calendrier', label: 'Calendrier', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' }
]

// Computed pour le brut HT (total des formats)
const brutHT = computed(() => totalFormats.value)

// Computed pour le net HT après remise
const netHT = computed(() => {
  if (!remise.value.active) return brutHT.value
  return Math.round(brutHT.value * (1 - remise.value.valeur / 100))
})

function updateRemiseActive(active) {
  store.updateRemise('active', active)
  if (active && remise.value.type !== 'pourcentage') {
    store.updateRemise('type', 'pourcentage')
  }
}

function updateRemiseValeur(valeur) {
  store.updateRemise('valeur', Math.min(100, Math.max(0, Number(valeur))))
}

const totalFormats = computed(() => {
  return modifiedPlan.value?.formatsProposés?.reduce((sum, f) => sum + f.total, 0) || 0
})

function handleRecalculate() {
  store.recalculateKpis()
}

function handleSave() {
  store.exitEditMode(true)
  emit('save')
}

function handleCancel() {
  store.exitEditMode(false)
  emit('close')
}

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Bandeau coût total avec remise -->
    <div class="flex-shrink-0 bg-gradient-to-r from-cm-red to-cm-dark p-4 text-white">
      <div class="flex items-center justify-between gap-4">
        <!-- Brut HT -->
        <div class="flex-1">
          <div class="text-xs text-white/70 uppercase tracking-wider">Brut HT</div>
          <div class="text-xl font-bold">{{ formatCurrency(brutHT) }}</div>
        </div>
        
        <!-- Remise -->
        <div class="flex items-center gap-3 bg-white/10 rounded-lg px-3 py-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <div class="relative">
              <input
                type="checkbox"
                :checked="remise.active"
                @change="updateRemiseActive($event.target.checked)"
                class="sr-only peer"
              />
              <div class="w-8 h-5 bg-white/30 rounded-full peer-checked:bg-green-400 transition-colors"></div>
              <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-3"></div>
            </div>
            <span class="text-sm font-medium">Remise</span>
          </label>
          
          <div v-if="remise.active" class="flex items-center gap-1">
            <input
              type="number"
              :value="remise.valeur"
              @input="updateRemiseValeur($event.target.value)"
              min="0"
              max="100"
              class="w-16 px-2 py-1 text-sm text-cm-dark bg-white rounded border-0 focus:ring-2 focus:ring-white/50"
            />
            <span class="text-sm font-medium">%</span>
          </div>
        </div>
        
        <!-- Net HT -->
        <div class="flex-1 text-right">
          <div class="text-xs text-white/70 uppercase tracking-wider">Net HT</div>
          <div class="text-2xl font-bold">{{ formatCurrency(netHT) }}</div>
        </div>
      </div>
    </div>

    <!-- Header with tabs -->
    <div class="flex-shrink-0 border-b border-gray-200">
      <div class="flex overflow-x-auto scrollbar-hide">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors',
            activeTab === tab.id
              ? 'border-cm-red text-cm-red'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" />
          </svg>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content area -->
    <div class="flex-1 overflow-y-auto p-4">
      <transition
        mode="out-in"
        enter-active-class="transition-opacity duration-150"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <RepartitionEditor v-if="activeTab === 'repartition'" key="repartition" />
        <SupportsEditor v-else-if="activeTab === 'supports'" key="supports" />
        <FormatsEditor v-else-if="activeTab === 'formats'" key="formats" />
        <CalendrierEditor v-else-if="activeTab === 'calendrier'" key="calendrier" />
      </transition>
    </div>

    <!-- Summary bar -->
    <div class="flex-shrink-0 border-t border-gray-200 bg-gray-50 px-4 py-3">
      <div class="flex items-center justify-between text-sm">
        <div class="flex items-center gap-6">
          <div>
            <span class="text-gray-500">Budget final:</span>
            <span class="ml-2 font-bold text-cm-dark">{{ formatCurrency(budgetFinal) }}</span>
          </div>
          <div>
            <span class="text-gray-500">Total formats:</span>
            <span class="ml-2 font-bold text-cm-dark">{{ formatCurrency(totalFormats) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="flex-shrink-0 border-t border-gray-200 bg-white px-4 py-3 flex items-center justify-between gap-3">
      <button
        @click="handleCancel"
        class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
      >
        Annuler
      </button>
      
      <div class="flex items-center gap-3">
        <button
          @click="handleRecalculate"
          :disabled="isLoading"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-cm-dark border border-cm-dark rounded-lg hover:bg-cm-dark hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ isLoading ? 'Calcul...' : 'Recalculer les KPI' }}
        </button>
        
        <button
          @click="handleSave"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-cm-red rounded-lg hover:bg-cm-red/90 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Valider
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
