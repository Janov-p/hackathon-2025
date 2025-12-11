<script setup>
import { computed, ref, watch } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { mediaPlan, isComplete, isLoading, lastUpdate, formData, isEditingPlan } = storeToRefs(store)

const emit = defineEmits(['edit'])

const isUpdating = ref(false)
const expandedSections = ref({
  supports: true,
  formats: false,
  calendrier: false,
  chiffrage: true
})

// Watch for updates to trigger animation
watch(lastUpdate, () => {
  isUpdating.value = true
  setTimeout(() => {
    isUpdating.value = false
  }, 1000)
})

const hasData = computed(() => {
  return mediaPlan.value.supportsRecommandes.length > 0
})

function toggleSection(section) {
  expandedSections.value[section] = !expandedSections.value[section]
}

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

const typeColors = {
  'Print': 'indigo',
  'Digital': 'emerald',
  'Réseaux sociaux': 'pink',
  'Event': 'amber'
}

function handleEdit() {
  store.enterEditMode()
  emit('edit')
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Empty state -->
    <div v-if="!hasData" class="flex-1 flex items-center justify-center">
      <div class="text-center p-8">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Plan média en attente</h3>
        <p class="text-sm text-gray-500">Complétez le formulaire pour générer le plan média</p>
      </div>
    </div>

    <!-- Media Plan Content -->
    <div v-else class="space-y-4 overflow-auto">
      <!-- Edit button -->
      <button
        @click="handleEdit"
        class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-cm-red/10 text-cm-red font-medium rounded-xl border-2 border-dashed border-cm-red/30 hover:bg-cm-red hover:text-white hover:border-cm-red transition-all duration-200"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Modifier le plan média
      </button>

      <!-- Supports recommandés -->
      <div class="border border-gray-200 rounded-xl overflow-hidden">
        <button
          @click="toggleSection('supports')"
          class="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-semibold text-gray-700">Supports recommandés</span>
            <span class="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full">
              {{ mediaPlan.supportsRecommandes.length }}
            </span>
          </div>
          <svg
            :class="['w-5 h-5 text-gray-400 transition-transform', expandedSections.supports ? 'rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-96"
          leave-active-class="transition-all duration-150"
          leave-from-class="opacity-100 max-h-96"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="expandedSections.supports" class="p-4 space-y-3 overflow-hidden">
            <div
              v-for="(support, index) in mediaPlan.supportsRecommandes"
              :key="index"
              :class="[
                'p-3 rounded-lg border-l-4 transition-all',
                `border-${typeColors[support.type] || 'gray'}-500`,
                `bg-${typeColors[support.type] || 'gray'}-50`
              ]"
            >
              <div class="flex items-start justify-between">
                <div>
                  <span :class="[
                    'text-xs font-bold uppercase tracking-wider',
                    `text-${typeColors[support.type] || 'gray'}-600`
                  ]">
                    {{ support.type }}
                  </span>
                  <h4 class="font-semibold text-gray-800">{{ support.nom }}</h4>
                  <p class="text-sm text-gray-500 mt-1">{{ support.justification }}</p>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Formats proposés -->
      <div class="border border-gray-200 rounded-xl overflow-hidden">
        <button
          @click="toggleSection('formats')"
          class="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            <span class="font-semibold text-gray-700">Formats proposés</span>
          </div>
          <svg
            :class="['w-5 h-5 text-gray-400 transition-transform', expandedSections.formats ? 'rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-96"
          leave-active-class="transition-all duration-150"
          leave-from-class="opacity-100 max-h-96"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="expandedSections.formats" class="overflow-x-auto overflow-hidden">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-2 text-left font-semibold text-gray-600">Support</th>
                  <th class="px-4 py-2 text-left font-semibold text-gray-600">Format</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-600">Tarif</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-600">Qté</th>
                  <th class="px-4 py-2 text-right font-semibold text-gray-600">Total</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(format, index) in mediaPlan.formatsProposés" :key="index" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-gray-800">{{ format.support }}</td>
                  <td class="px-4 py-3">
                    <span class="font-medium text-gray-800">{{ format.format }}</span>
                    <span class="text-xs text-gray-500 block">{{ format.dimensions }}</span>
                  </td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ formatCurrency(format.tarifUnitaire) }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ format.quantite }}</td>
                  <td class="px-4 py-3 text-right font-semibold text-gray-800">{{ formatCurrency(format.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </transition>
      </div>

      <!-- Calendrier -->
      <div class="border border-gray-200 rounded-xl overflow-hidden">
        <button
          @click="toggleSection('calendrier')"
          class="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-semibold text-gray-700">Calendrier de diffusion</span>
          </div>
          <svg
            :class="['w-5 h-5 text-gray-400 transition-transform', expandedSections.calendrier ? 'rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-96"
          leave-active-class="transition-all duration-150"
          leave-from-class="opacity-100 max-h-96"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="expandedSections.calendrier" class="p-4 overflow-hidden">
            <div class="flex gap-2">
              <div
                v-for="semaine in mediaPlan.calendrier"
                :key="semaine.semaine"
                class="flex-1 bg-gray-50 rounded-lg p-3"
              >
                <div class="text-xs font-bold text-gray-500 mb-2">Semaine {{ semaine.semaine }}</div>
                <div class="space-y-1">
                  <div
                    v-for="action in semaine.actions"
                    :key="action.support"
                    class="text-xs"
                  >
                    <span class="font-medium text-gray-700">{{ action.support }}:</span>
                    <span class="text-gray-500 ml-1">{{ action.action }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Chiffrage -->
      <div class="border border-gray-200 rounded-xl overflow-hidden">
        <button
          @click="toggleSection('chiffrage')"
          class="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span class="font-semibold text-gray-700">Chiffrage</span>
          </div>
          <svg
            :class="['w-5 h-5 text-gray-400 transition-transform', expandedSections.chiffrage ? 'rotate-180' : '']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-96"
          leave-active-class="transition-all duration-150"
          leave-from-class="opacity-100 max-h-96"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="expandedSections.chiffrage" class="p-4 space-y-4 overflow-hidden">
            <!-- Total HT / TTC -->
            <div class="bg-gradient-to-r from-cm-red to-cm-dark rounded-xl p-4 text-white">
              <div class="flex justify-between items-end">
                <div>
                  <div class="text-xs opacity-70 uppercase tracking-wider">Total HT</div>
                  <div class="text-2xl font-bold">{{ formatCurrency(mediaPlan.chiffrage.totalHT) }}</div>
                </div>
                <div class="text-right">
                  <div class="text-xs opacity-70 uppercase tracking-wider">Total TTC (TVA 20%)</div>
                  <div class="text-2xl font-bold">{{ formatCurrency(mediaPlan.chiffrage.totalHT * 1.2) }}</div>
                </div>
              </div>
              <div class="mt-2 pt-2 border-t border-white/20 text-xs opacity-70 text-right">
                TVA : {{ formatCurrency(mediaPlan.chiffrage.totalHT * 0.2) }}
              </div>
            </div>

            <!-- Par support -->
            <div>
              <h5 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Par support</h5>
              <div class="space-y-2">
                <div
                  v-for="(value, key) in mediaPlan.chiffrage.parSupport"
                  :key="key"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <span class="text-sm text-gray-600 capitalize">{{ key }}</span>
                  <span class="font-semibold text-gray-800">{{ formatCurrency(value) }}</span>
                </div>
              </div>
            </div>

            <!-- Par semaine -->
            <div>
              <h5 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Par semaine</h5>
              <div class="flex gap-2">
                <div
                  v-for="semaine in mediaPlan.chiffrage.parSemaine"
                  :key="semaine.semaine"
                  class="flex-1 text-center p-2 bg-gray-50 rounded-lg"
                >
                  <div class="text-xs text-gray-500">S{{ semaine.semaine }}</div>
                  <div class="font-semibold text-gray-800 text-sm">{{ formatCurrency(semaine.montant) }}</div>
                </div>
              </div>
            </div>
          </div>
        </transition>
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
        <div class="flex items-center gap-2 text-emerald-600">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="font-medium">Génération en cours...</span>
        </div>
      </div>
    </transition>
  </div>
</template>
