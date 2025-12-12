<script setup>
import { computed, ref, watch } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import * as XLSX from 'xlsx'

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

function exportToExcel() {
  if (!hasData.value) return

  const wb = XLSX.utils.book_new()
  const campaignName = formData.value.nom || 'Plan-Media'

  // === Feuille 1: Supports recommandés ===
  const supportsData = [
    ['PLAN MÉDIA - SUPPORTS RECOMMANDÉS'],
    [''],
    ['Campagne:', campaignName],
    ['Date:', new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })],
    [''],
    ['Type', 'Nom', 'Justification']
  ]
  mediaPlan.value.supportsRecommandes.forEach(support => {
    supportsData.push([support.type, support.nom, support.justification])
  })
  const wsSupports = XLSX.utils.aoa_to_sheet(supportsData)
  wsSupports['!cols'] = [{ wch: 18 }, { wch: 25 }, { wch: 50 }]
  XLSX.utils.book_append_sheet(wb, wsSupports, 'Supports')

  // === Feuille 2: Formats proposés ===
  const formatsData = [
    ['FORMATS PROPOSÉS'],
    [''],
    ['Support', 'Format', 'Dimensions', 'Tarif unitaire (€)', 'Quantité', 'Total (€)']
  ]
  let totalFormats = 0
  mediaPlan.value.formatsProposés.forEach(format => {
    formatsData.push([
      format.support,
      format.format,
      format.dimensions,
      format.tarifUnitaire,
      format.quantite,
      format.total
    ])
    totalFormats += format.total
  })
  formatsData.push([])
  formatsData.push(['', '', '', '', 'TOTAL', totalFormats])
  const wsFormats = XLSX.utils.aoa_to_sheet(formatsData)
  wsFormats['!cols'] = [{ wch: 15 }, { wch: 15 }, { wch: 15 }, { wch: 18 }, { wch: 10 }, { wch: 12 }]
  XLSX.utils.book_append_sheet(wb, wsFormats, 'Formats')

  // === Feuille 3: Calendrier ===
  const calendarData = [
    ['CALENDRIER DE DIFFUSION'],
    [''],
    ['Semaine', 'Support', 'Action']
  ]
  mediaPlan.value.calendrier.forEach(semaine => {
    semaine.actions.forEach((action, idx) => {
      calendarData.push([
        idx === 0 ? `Semaine ${semaine.semaine}` : '',
        action.support,
        action.action
      ])
    })
  })
  const wsCalendar = XLSX.utils.aoa_to_sheet(calendarData)
  wsCalendar['!cols'] = [{ wch: 12 }, { wch: 15 }, { wch: 25 }]
  XLSX.utils.book_append_sheet(wb, wsCalendar, 'Calendrier')

  // === Feuille 4: Chiffrage ===
  const chiffrageData = [
    ['CHIFFRAGE'],
    [''],
    ['Total HT', mediaPlan.value.chiffrage.totalHT, '€'],
    ['TVA (20%)', mediaPlan.value.chiffrage.totalHT * 0.2, '€'],
    ['Total TTC', mediaPlan.value.chiffrage.totalHT * 1.2, '€'],
    [''],
    ['=== RÉPARTITION PAR SUPPORT ==='],
    ['Support', 'Montant (€)']
  ]
  Object.entries(mediaPlan.value.chiffrage.parSupport).forEach(([key, value]) => {
    chiffrageData.push([key, value])
  })
  chiffrageData.push([])
  chiffrageData.push(['=== RÉPARTITION PAR SEMAINE ==='])
  chiffrageData.push(['Semaine', 'Montant (€)'])
  mediaPlan.value.chiffrage.parSemaine.forEach(semaine => {
    chiffrageData.push([`Semaine ${semaine.semaine}`, semaine.montant])
  })
  const wsChiffrage = XLSX.utils.aoa_to_sheet(chiffrageData)
  wsChiffrage['!cols'] = [{ wch: 25 }, { wch: 15 }, { wch: 5 }]
  XLSX.utils.book_append_sheet(wb, wsChiffrage, 'Chiffrage')

  // Télécharger le fichier
  const fileName = `plan-media-${campaignName.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
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
      <!-- Action buttons -->
      <div class="flex gap-2">
        <button
          @click="handleEdit"
          class="flex-1 flex items-center justify-center gap-2 px-3 md:px-4 py-2.5 md:py-3 min-h-[44px] bg-cm-red/10 text-cm-red font-medium rounded-lg md:rounded-xl border-2 border-dashed border-cm-red/30 hover:bg-cm-red hover:text-white hover:border-cm-red active:scale-[0.98] transition-all duration-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span class="text-sm md:text-base">Modifier</span>
        </button>
        <button
          @click="exportToExcel"
          class="flex items-center justify-center gap-2 px-3 md:px-4 py-2.5 md:py-3 min-h-[44px] bg-emerald-50 text-emerald-700 font-medium rounded-lg md:rounded-xl border-2 border-emerald-200 hover:bg-emerald-600 hover:text-white hover:border-emerald-600 active:scale-[0.98] transition-all duration-200"
          title="Exporter en Excel"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span class="hidden md:inline text-sm">Excel</span>
        </button>
      </div>

      <!-- Supports recommandés -->
      <div class="border border-gray-200 rounded-lg md:rounded-xl overflow-hidden">
        <button
          @click="toggleSection('supports')"
          class="w-full flex items-center justify-between p-3 md:p-4 min-h-[48px] bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors"
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
          <div v-if="expandedSections.supports" class="p-3 md:p-4 space-y-2 md:space-y-3 overflow-hidden">
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
      <div class="border border-gray-200 rounded-lg md:rounded-xl overflow-hidden">
        <button
          @click="toggleSection('formats')"
          class="w-full flex items-center justify-between p-3 md:p-4 min-h-[48px] bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors"
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
          <div v-if="expandedSections.formats" class="overflow-hidden">
            <!-- Mobile: Cards view -->
            <div class="md:hidden p-3 space-y-2">
              <div
                v-for="(format, index) in mediaPlan.formatsProposés"
                :key="index"
                class="bg-gray-50 rounded-lg p-3"
              >
                <div class="flex justify-between items-start mb-2">
                  <div>
                    <span class="font-medium text-gray-800 text-sm">{{ format.support }}</span>
                    <span class="text-xs text-gray-500 block">{{ format.format }}</span>
                  </div>
                  <span class="font-bold text-cm-red">{{ formatCurrency(format.total) }}</span>
                </div>
                <div class="flex justify-between text-xs text-gray-500">
                  <span>{{ format.dimensions }}</span>
                  <span>{{ format.quantite }} × {{ formatCurrency(format.tarifUnitaire) }}</span>
                </div>
              </div>
            </div>
            <!-- Desktop: Table view -->
            <div class="hidden md:block overflow-x-auto">
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
          </div>
        </transition>
      </div>

      <!-- Calendrier -->
      <div class="border border-gray-200 rounded-lg md:rounded-xl overflow-hidden">
        <button
          @click="toggleSection('calendrier')"
          class="w-full flex items-center justify-between p-3 md:p-4 min-h-[48px] bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-semibold text-gray-700 text-sm md:text-base">Calendrier de diffusion</span>
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
          <div v-if="expandedSections.calendrier" class="p-3 md:p-4 overflow-x-auto overflow-hidden">
            <div class="flex gap-2 min-w-max md:min-w-0">
              <div
                v-for="semaine in mediaPlan.calendrier"
                :key="semaine.semaine"
                class="flex-1 min-w-[120px] md:min-w-0 bg-gray-50 rounded-lg p-2 md:p-3"
              >
                <div class="text-xs font-bold text-gray-500 mb-2">S{{ semaine.semaine }}</div>
                <div class="space-y-1">
                  <div
                    v-for="action in semaine.actions"
                    :key="action.support"
                    class="text-xs"
                  >
                    <span class="font-medium text-gray-700">{{ action.support }}:</span>
                    <span class="text-gray-500 ml-1 block md:inline">{{ action.action }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Chiffrage -->
      <div class="border border-gray-200 rounded-lg md:rounded-xl overflow-hidden">
        <button
          @click="toggleSection('chiffrage')"
          class="w-full flex items-center justify-between p-3 md:p-4 min-h-[48px] bg-gray-50 hover:bg-gray-100 active:bg-gray-200 transition-colors"
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
          <div v-if="expandedSections.chiffrage" class="p-3 md:p-4 space-y-3 md:space-y-4 overflow-hidden">
            <!-- Total HT / TTC -->
            <div class="bg-gradient-to-r from-cm-red to-cm-dark rounded-lg md:rounded-xl p-3 md:p-4 text-white">
              <div class="flex flex-col sm:flex-row justify-between gap-2 sm:items-end">
                <div>
                  <div class="text-xs opacity-70 uppercase tracking-wider">Total HT</div>
                  <div class="text-xl md:text-2xl font-bold">{{ formatCurrency(mediaPlan.chiffrage.totalHT) }}</div>
                </div>
                <div class="sm:text-right">
                  <div class="text-xs opacity-70 uppercase tracking-wider">Total TTC (TVA 20%)</div>
                  <div class="text-xl md:text-2xl font-bold">{{ formatCurrency(mediaPlan.chiffrage.totalHT * 1.2) }}</div>
                </div>
              </div>
              <div class="mt-2 pt-2 border-t border-white/20 text-xs opacity-70 text-right">
                TVA : {{ formatCurrency(mediaPlan.chiffrage.totalHT * 0.2) }}
              </div>
            </div>

            <!-- Par support -->
            <div>
              <h5 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Par support</h5>
              <div class="grid grid-cols-2 md:grid-cols-1 gap-1.5 md:gap-2">
                <div
                  v-for="(value, key) in mediaPlan.chiffrage.parSupport"
                  :key="key"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                >
                  <span class="text-xs md:text-sm text-gray-600 capitalize">{{ key }}</span>
                  <span class="font-semibold text-gray-800 text-sm">{{ formatCurrency(value) }}</span>
                </div>
              </div>
            </div>

            <!-- Par semaine -->
            <div>
              <h5 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Par semaine</h5>
              <div class="flex gap-1.5 md:gap-2 overflow-x-auto pb-1">
                <div
                  v-for="semaine in mediaPlan.chiffrage.parSemaine"
                  :key="semaine.semaine"
                  class="flex-1 min-w-[60px] text-center p-2 bg-gray-50 rounded-lg"
                >
                  <div class="text-xs text-gray-500">S{{ semaine.semaine }}</div>
                  <div class="font-semibold text-gray-800 text-xs md:text-sm">{{ formatCurrency(semaine.montant) }}</div>
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
