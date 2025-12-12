<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as XLSX from 'xlsx'

const router = useRouter()

// Données chargées depuis localStorage
const kpiResults = ref({})
const mediaPlan = ref({ supportsRecommandes: [], formatsProposés: [], chiffrage: { totalHT: 0, parSupport: {} } })
const formData = ref({})
const remise = ref({ active: false, type: 'pourcentage', valeur: 0, visible: true })

// Computed: calcul du brut HT, net HT et TTC
const brutHT = computed(() => mediaPlan.value.chiffrage?.totalHT || 0)
const netHT = computed(() => {
  if (!remise.value.active) return brutHT.value
  if (remise.value.type === 'pourcentage') {
    return Math.round(brutHT.value * (1 - remise.value.valeur / 100))
  }
  return Math.max(0, brutHT.value - remise.value.valeur)
})
const montantRemise = computed(() => brutHT.value - netHT.value)
const tva = computed(() => netHT.value * 0.2)
const totalTTC = computed(() => netHT.value * 1.2)

// État pour l'envoi d'email
const emailTo = ref('')
const emailSending = ref(false)
const emailSent = ref(false)
const emailError = ref('')
const showEmailModal = ref(false)

const hasData = computed(() => {
  return kpiResults.value.audienceCumulee > 0
})

// Charger les données depuis localStorage au montage
onMounted(() => {
  const savedData = localStorage.getItem('exportData')
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      kpiResults.value = data.kpiResults || {}
      mediaPlan.value = data.mediaPlan || { supportsRecommandes: [], formatsProposés: [], chiffrage: { totalHT: 0, parSupport: {} } }
      formData.value = data.formData || {}
      remise.value = data.remise || { active: false, type: 'pourcentage', valeur: 0, visible: true }
    } catch (e) {
      console.error('Erreur lors du chargement des données:', e)
    }
  }
})

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

function formatNumber(value) {
  return new Intl.NumberFormat('fr-FR').format(value)
}

function goBack() {
  router.push('/')
}

function printPdf() {
  window.print()
}

function exportToExcel() {
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

  // === Feuille 3: KPI ===
  const kpiData = [
    ['INDICATEURS DE PERFORMANCE (KPI)'],
    [''],
    ['Indicateur', 'Valeur'],
    ['Audience Cumulée', kpiResults.value.audienceCumulee],
    ['Taux de Couverture', `${kpiResults.value.tauxCouverture}%`],
    ['Fréquence Moyenne', `${kpiResults.value.frequenceMoyenne}x`],
    ['GRP', kpiResults.value.grp],
    ['Impressions', kpiResults.value.impressions],
    ['Clics Estimés', kpiResults.value.clicsEstimes]
  ]
  const wsKpi = XLSX.utils.aoa_to_sheet(kpiData)
  wsKpi['!cols'] = [{ wch: 25 }, { wch: 20 }]
  XLSX.utils.book_append_sheet(wb, wsKpi, 'KPI')

  // === Feuille 4: Chiffrage ===
  const chiffrageData = [
    ['CHIFFRAGE'],
    [''],
    ['Brut HT', brutHT.value, '€']
  ]
  if (remise.value.active && remise.value.visible) {
    chiffrageData.push(['Remise', -montantRemise.value, '€'])
  }
  chiffrageData.push(
    ['Net HT', netHT.value, '€'],
    ['TVA (20%)', tva.value, '€'],
    ['Total TTC', totalTTC.value, '€'],
    [''],
    ['=== RÉPARTITION PAR SUPPORT ==='],
    ['Support', 'Montant (€)']
  )
  Object.entries(mediaPlan.value.chiffrage.parSupport).forEach(([key, value]) => {
    chiffrageData.push([key, value])
  })
  const wsChiffrage = XLSX.utils.aoa_to_sheet(chiffrageData)
  wsChiffrage['!cols'] = [{ wch: 25 }, { wch: 15 }, { wch: 5 }]
  XLSX.utils.book_append_sheet(wb, wsChiffrage, 'Chiffrage')

  // Télécharger le fichier
  const fileName = `plan-media-${campaignName.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
}

async function sendEmail() {
  if (!emailTo.value) {
    emailError.value = 'Veuillez entrer une adresse email'
    return
  }

  emailSending.value = true
  emailError.value = ''

  try {
    const response = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'api-key': import.meta.env.VITE_BREVO_API_KEY,
        'content-type': 'application/json'
      },
      body: JSON.stringify({
        to: [{ email: emailTo.value }],
        templateId: 2,
        params: {
          nom: formData.value.nom || 'Campagne',
          secteur: formData.value.secteur || '-',
          audienceCumulee: formatNumber(kpiResults.value.audienceCumulee),
          tauxCouverture: kpiResults.value.tauxCouverture,
          grp: kpiResults.value.grp,
          impressions: formatNumber(kpiResults.value.impressions),
          totalHT: formatCurrency(netHT.value),
          totalTTC: formatCurrency(totalTTC.value)
        }
      })
    })

    if (response.ok) {
      emailSent.value = true
      setTimeout(() => {
        showEmailModal.value = false
        emailSent.value = false
        emailTo.value = ''
      }, 2000)
    } else {
      const data = await response.json()
      emailError.value = data.message || 'Erreur lors de l\'envoi'
    }
  } catch (err) {
    emailError.value = 'Erreur de connexion au serveur'
  } finally {
    emailSending.value = false
  }
}

</script>

<template>
  <div class="min-h-screen bg-cm-gray">
    <!-- Header avec actions (caché à l'impression) - Sticky bottom on mobile -->
    <div class="print:hidden fixed bottom-0 left-0 right-0 md:sticky md:top-0 md:bottom-auto z-50 bg-white shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] md:shadow-md">
      <div class="max-w-5xl mx-auto px-3 md:px-6 py-3 md:py-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2 md:gap-0">
        <button
          @click="goBack"
          class="hidden md:flex items-center gap-2 text-cm-dark hover:text-cm-red transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span class="font-medium">Retour</span>
        </button>

        <div class="flex flex-col md:flex-row items-stretch md:items-center gap-2 md:gap-3">
          <!-- Bouton Excel -->
          <button
            @click="exportToExcel"
            class="flex items-center justify-center gap-2 px-4 md:px-5 py-3 md:py-2.5 min-h-[48px] bg-emerald-50 border-2 border-emerald-500 text-emerald-700 rounded-lg font-semibold hover:bg-emerald-600 hover:text-white hover:border-emerald-600 active:scale-[0.98] transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Excel</span>
          </button>

          <!-- Bouton PDF -->
          <button
            @click="printPdf"
            class="flex items-center justify-center gap-2 px-4 md:px-5 py-3 md:py-2.5 min-h-[48px] bg-red-50 border-2 border-cm-red text-cm-red rounded-lg font-semibold hover:bg-cm-red hover:text-white hover:border-cm-red active:scale-[0.98] transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span>PDF</span>
          </button>

          <!-- Bouton Envoyer par email -->
          <button
            @click="showEmailModal = true"
            class="flex items-center justify-center gap-2 px-4 md:px-5 py-3 md:py-2.5 min-h-[48px] bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-100 active:scale-[0.98] transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span>Email</span>
          </button>
        </div>
        
        <!-- Mobile back button -->
        <button
          @click="goBack"
          class="md:hidden flex items-center justify-center gap-2 px-4 py-2 min-h-[44px] text-cm-dark active:text-cm-red transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span class="font-medium">Retour à l'application</span>
        </button>
      </div>
    </div>

    <!-- Contenu PDF - Add bottom padding on mobile for sticky bar -->
    <div class="max-w-5xl mx-auto p-3 md:p-6 pb-48 md:pb-6 print:p-0 print:max-w-none">
      <div class="bg-white rounded-xl md:rounded-2xl shadow-xl overflow-hidden print:rounded-none print:shadow-none">
        <!-- En-tête -->
        <div class="bg-cm-red p-4 md:p-8 text-white print:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h1 class="text-2xl md:text-3xl font-bold">Plan Média</h1>
              <p class="text-white/80 mt-1 text-sm md:text-base">{{ formData.nom || 'Campagne' }}</p>
            </div>
            <div class="sm:text-right">
              <div class="text-xs md:text-sm text-white/70">Généré le</div>
              <div class="font-semibold text-sm md:text-base">{{ new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) }}</div>
            </div>
          </div>
        </div>

        <!-- Informations campagne -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Informations Campagne
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            <div>
              <div class="text-xs text-gray-500 uppercase tracking-wider">Nom</div>
              <div class="font-semibold text-gray-800 text-sm md:text-base">{{ formData.nom || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500 uppercase tracking-wider">Secteur</div>
              <div class="font-semibold text-gray-800 text-sm md:text-base">{{ formData.secteur || '-' }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500 uppercase tracking-wider">Période</div>
              <div class="font-semibold text-gray-800 text-sm md:text-base">
                {{ formData.periodeDebut || '-' }} → {{ formData.periodeFin || '-' }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500 uppercase tracking-wider">Zones</div>
              <div class="font-semibold text-gray-800 text-sm md:text-base">{{ formData.zones?.join(', ') || '-' }}</div>
            </div>
          </div>
        </div>

        <!-- KPI -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Indicateurs de Performance (KPI)
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-4">
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Audience Cumulée</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ formatNumber(kpiResults.audienceCumulee) }}</div>
              <div class="text-xs md:text-sm text-gray-500">contacts</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Taux de Couverture</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ kpiResults.tauxCouverture }}%</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Fréquence Moyenne</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ kpiResults.frequenceMoyenne }}x</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">GRP</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ kpiResults.grp }}</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Impressions</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ formatNumber(kpiResults.impressions) }}</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Clics Estimés</div>
              <div class="text-lg md:text-2xl font-bold text-gray-800">{{ formatNumber(kpiResults.clicsEstimes) }}</div>
            </div>
          </div>
        </div>

        <!-- Supports recommandés -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Supports Recommandés
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-4">
            <div
              v-for="(support, index) in mediaPlan.supportsRecommandes"
              :key="index"
              class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red"
            >
              <div class="text-xs font-bold text-cm-red uppercase tracking-wider">{{ support.type }}</div>
              <div class="font-semibold text-gray-800 mt-1 text-sm md:text-base">{{ support.nom }}</div>
              <div class="text-xs md:text-sm text-gray-500 mt-1">{{ support.justification }}</div>
            </div>
          </div>
        </div>

        <!-- Formats proposés -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            Formats Proposés
          </h2>
          <!-- Mobile: Cards -->
          <div class="md:hidden space-y-2">
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
          <!-- Desktop: Table -->
          <div class="hidden md:block overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-gray-600">Support</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-600">Format</th>
                  <th class="px-4 py-3 text-left font-semibold text-gray-600">Dimensions</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">Tarif</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">Qté</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">Total</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="(format, index) in mediaPlan.formatsProposés" :key="index">
                  <td class="px-4 py-3 text-gray-800">{{ format.support }}</td>
                  <td class="px-4 py-3 font-medium text-gray-800">{{ format.format }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ format.dimensions }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ formatCurrency(format.tarifUnitaire) }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ format.quantite }}</td>
                  <td class="px-4 py-3 text-right font-semibold text-gray-800">{{ formatCurrency(format.total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Chiffrage -->
        <div class="p-4 md:p-8 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Chiffrage
          </h2>

          <!-- Total avec Brut HT, Net HT et TTC -->
          <div class="bg-cm-red rounded-lg md:rounded-xl p-4 md:p-6 text-white mb-4 md:mb-6">
            <!-- Ligne Brut HT -->
            <div class="flex justify-between items-center pb-2 md:pb-3 border-b border-white/20">
              <div class="text-xs md:text-sm text-white/70 uppercase tracking-wider">Brut HT</div>
              <div class="text-lg md:text-xl font-semibold">{{ formatCurrency(brutHT) }}</div>
            </div>
            
            <!-- Ligne Remise (si active et visible) -->
            <div v-if="remise.active && remise.visible" class="flex justify-between items-center py-2 md:py-3 border-b border-white/20">
              <div class="text-xs md:text-sm text-white/70 uppercase tracking-wider">
                Remise {{ remise.type === 'pourcentage' ? `(${remise.valeur}%)` : '' }}
              </div>
              <div class="text-lg md:text-xl font-semibold text-green-300">- {{ formatCurrency(montantRemise) }}</div>
            </div>
            
            <!-- Ligne Net HT -->
            <div class="flex justify-between items-center py-2 md:py-3 border-b border-white/20">
              <div class="text-xs md:text-sm text-white/70 uppercase tracking-wider">Net HT</div>
              <div class="text-xl md:text-2xl font-bold">{{ formatCurrency(netHT) }}</div>
            </div>
            
            <!-- Ligne TVA -->
            <div class="flex justify-between items-center py-2 md:py-3 border-b border-white/20">
              <div class="text-xs md:text-sm text-white/70 uppercase tracking-wider">TVA (20%)</div>
              <div class="text-lg md:text-xl font-semibold">{{ formatCurrency(tva) }}</div>
            </div>
            
            <!-- Ligne Total TTC -->
            <div class="flex justify-between items-center pt-2 md:pt-3">
              <div class="text-xs md:text-sm text-white/70 uppercase tracking-wider">Total TTC</div>
              <div class="text-2xl md:text-3xl font-bold">{{ formatCurrency(totalTTC) }}</div>
            </div>
          </div>

          <!-- Par support -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4">
            <div
              v-for="(value, key) in mediaPlan.chiffrage.parSupport"
              :key="key"
              class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl text-center"
            >
              <div class="text-xs text-gray-500 uppercase tracking-wider capitalize">{{ key }}</div>
              <div class="text-lg md:text-xl font-bold text-gray-800 mt-1">{{ formatCurrency(value) }}</div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-100 px-4 md:px-8 py-3 md:py-4 text-center text-xs md:text-sm text-gray-500 print:bg-gray-50">
          Document généré par Calculette Plan Média - Corse-Matin
        </div>
      </div>
    </div>

    <!-- Modal Email -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showEmailModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 print:hidden">
          <div class="absolute inset-0 bg-black/50" @click="showEmailModal = false"></div>
          <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <button
              @click="showEmailModal = false"
              class="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="text-center mb-6">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-cm-red/10 flex items-center justify-center">
                <svg class="w-8 h-8 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 class="text-xl font-bold text-cm-dark">Envoyer par email</h3>
              <p class="text-gray-500 mt-1">Le plan média sera envoyé en pièce jointe</p>
            </div>

            <!-- Succès -->
            <div v-if="emailSent" class="text-center py-8">
              <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p class="text-green-600 font-semibold">Email envoyé avec succès !</p>
            </div>

            <!-- Formulaire -->
            <div v-else>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Adresse email du destinataire</label>
                <input
                  v-model="emailTo"
                  type="email"
                  placeholder="exemple@email.com"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cm-red focus:border-cm-red outline-none transition-all"
                  @keyup.enter="sendEmail"
                />
              </div>

              <div v-if="emailError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {{ emailError }}
              </div>

              <button
                @click="sendEmail"
                :disabled="emailSending"
                class="w-full py-3 bg-cm-red text-white rounded-lg font-semibold hover:bg-cm-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <svg v-if="emailSending" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ emailSending ? 'Envoi en cours...' : 'Envoyer' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
@media print {
  .print\:hidden {
    display: none !important;
  }
  .print\:p-0 {
    padding: 0 !important;
  }
  .print\:p-6 {
    padding: 1.5rem !important;
  }
  .print\:max-w-none {
    max-width: none !important;
  }
  .print\:rounded-none {
    border-radius: 0 !important;
  }
  .print\:shadow-none {
    box-shadow: none !important;
  }
  .print\:bg-gray-50 {
    background-color: #f9fafb !important;
  }
}
</style>
