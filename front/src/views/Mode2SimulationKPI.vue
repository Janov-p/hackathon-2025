<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Données de référence
const formats = {
  print: [
    { id: 'page_entiere', name: 'Page entière', cpm: 45, baseImpressions: 139000 },
    { id: 'demi_page', name: 'Demi-page', cpm: 30, baseImpressions: 139000 },
    { id: 'encart', name: 'Encart', cpm: 25, baseImpressions: 139000 },
    { id: 'supplement_thematique', name: 'Supplément thématique', cpm: 60, baseImpressions: 200000 },
    { id: 'magazine' , name: 'Magazine', cpm: 50, baseImpressions: 180000 }
  ],
  digital: [
    { id: 'habillage', name: 'Habillage site', cpm: 15, baseImpressions: 2500000 },
    { id: 'pave', name: 'Pavé', cpm: 8, baseImpressions: 2500000 },
    { id: 'interstitiel', name: 'Interstitiel appli', cpm: 12, baseImpressions: 400000 },
    { id: 'smart_cover', name: 'Smart cover mobile', cpm: 10, baseImpressions: 400000 },
    { id: 'preroll', name: 'Pré-roll vidéo', cpm: 20, baseImpressions: 300000 }
  ],
  social: [
    { id: 'instagram', name: 'Instagram', cpm: 6, baseImpressions: 250000 },
    { id: 'facebook', name: 'Facebook', cpm: 5, baseImpressions: 250000 },
    { id: 'linkedIn', name: 'LinkedIn', cpm: 7, baseImpressions: 200000 },
    { id: 'twitter', name: 'Twitter', cpm: 6, baseImpressions: 200000 },
    { id: 'video_social', name: 'Vidéo réseaux sociaux', cpm: 8, baseImpressions: 150000 }
  ]
}

// État du formulaire
const campaignName = ref('Plan média client')
const mediaItems = ref([])
const showAddForm = ref(false)

// Formulaire d'ajout
const newItem = ref({
  type: 'print',
  format: '',
  quantity: 1,
  customPrice: null
})

// Paramètres de calcul
const POPULATION_CIBLE = 150000 // Population cible
const CTR_BY_FORMAT = {
  print: 0,
  habillage: 0.012,
  pave: 0.008,
  interstitiel: 0.015,
  smart_cover: 0.010,
  preroll: 0.005,
  instagram: 0.010,
  facebook: 0.008,
  linkedIn: 0.012,
  twitter: 0.009,
  video_social: 0.020
}

// Calculs KPI complets
const kpiResults = computed(() => {
  if (mediaItems.value.length === 0) {
    return null
  }

  let totalCost = 0
  let totalImpressions = 0
  let totalClics = 0
  let vuesVideoTotal = 0
  
  let bySupport = {
    print: { cost: 0, impressions: 0, items: 0, clics: 0, cpm: 0 },
    digital: { cost: 0, impressions: 0, items: 0, clics: 0, cpm: 0 },
    social: { cost: 0, impressions: 0, items: 0, clics: 0, cpm: 0 }
  }

  // Calcul des métriques de base par insertion
  mediaItems.value.forEach(item => {
    const formatData = findFormat(item.type, item.format)
    if (!formatData) return

    const impressions = formatData.baseImpressions * item.quantity
    const cpm = item.customPrice || formatData.cpm
    const cost = (impressions / 1000) * cpm

    // CTR par format
    const ctr = CTR_BY_FORMAT[item.format] || 0.008
    const clics = Math.round(impressions * ctr)

    totalCost += cost
    totalImpressions += impressions
    totalClics += clics

    bySupport[item.type].cost += cost
    bySupport[item.type].impressions += impressions
    bySupport[item.type].items += 1
    bySupport[item.type].clics += clics

    // Vues vidéo (preroll et vidéos sociales)
    if (item.format === 'preroll' || item.format === 'video_social') {
      vuesVideoTotal += Math.round(impressions * 0.75)
    }
  })

  // Calcul CPM par support
  Object.keys(bySupport).forEach(type => {
    if (bySupport[type].impressions > 0) {
      bySupport[type].cpm = (bySupport[type].cost / bySupport[type].impressions) * 1000
    }
  })

  // === KPI d'Impact & Exposition ===
  
  // Modèle de déduplication multi-supports (formule Hofmans simplifiée)
  const reachPrint = Math.min(1, bySupport.print.impressions / POPULATION_CIBLE)
  const reachDigital = Math.min(1, bySupport.digital.impressions / (POPULATION_CIBLE * 1.5))
  const reachSocial = Math.min(1, bySupport.social.impressions / (POPULATION_CIBLE * 1.8))
  
  // Déduplication avec facteurs de recoupement
  const overlapPrintDigital = reachPrint * reachDigital * 0.35
  const overlapPrintSocial = reachPrint * reachSocial * 0.25
  const overlapDigitalSocial = reachDigital * reachSocial * 0.45
  const overlapAll = reachPrint * reachDigital * reachSocial * 0.15
  
  const reachDeduplique = reachPrint + reachDigital + reachSocial 
    - overlapPrintDigital - overlapPrintSocial - overlapDigitalSocial 
    + overlapAll
  
  const audienceCumuleeDedupliquee = Math.round(Math.min(reachDeduplique, 0.95) * POPULATION_CIBLE)
  const tauxCouverture = (audienceCumuleeDedupliquee / POPULATION_CIBLE) * 100
  
  // Fréquence moyenne : Impressions totales / Audience dédupliquée
  const frequenceMoyenne = audienceCumuleeDedupliquee > 0 
    ? totalImpressions / audienceCumuleeDedupliquee 
    : 0
  
  // GRP = Couverture × Fréquence
  const grp = tauxCouverture * frequenceMoyenne

  // === KPI d'Efficacité Financière ===
  
  const cpmMoyen = totalImpressions > 0 ? (totalCost / totalImpressions) * 1000 : 0
  const coutGRP = grp > 0 ? totalCost / grp : 0

  // === KPI d'Engagement & Action ===
  
  const ctrMoyen = totalImpressions > 0 ? (totalClics / totalImpressions) * 100 : 0

  // === KPI de Stratégie (Répartition) ===
  
  const repartitionBudget = {
    print: totalCost > 0 ? (bySupport.print.cost / totalCost) * 100 : 0,
    digital: totalCost > 0 ? (bySupport.digital.cost / totalCost) * 100 : 0,
    social: totalCost > 0 ? (bySupport.social.cost / totalCost) * 100 : 0
  }

  const repartitionAudience = {
    print: totalImpressions > 0 ? (bySupport.print.impressions / totalImpressions) * 100 : 0,
    digital: totalImpressions > 0 ? (bySupport.digital.impressions / totalImpressions) * 100 : 0,
    social: totalImpressions > 0 ? (bySupport.social.impressions / totalImpressions) * 100 : 0
  }

  return {
    // Impact & Exposition
    audienceCumuleeDedupliquee,
    tauxCouverture,
    frequenceMoyenne,
    grp,
    totalImpressions,
    vuesVideoTotal,
    
    // Efficacité Financière
    totalCost,
    cpmMoyen,
    coutGRP,
    bySupport,
    
    // Engagement & Action
    totalClics,
    ctrMoyen,
    
    // Stratégie
    repartitionBudget,
    repartitionAudience
  }
})

function findFormat(type, formatId) {
  return formats[type]?.find(f => f.id === formatId)
}

function addMediaItem() {
  if (!newItem.value.format) return

  const formatData = findFormat(newItem.value.type, newItem.value.format)
  if (!formatData) return

  mediaItems.value.push({
    id: Date.now(),
    type: newItem.value.type,
    format: newItem.value.format,
    formatName: formatData.name,
    quantity: newItem.value.quantity,
    customPrice: newItem.value.customPrice,
    baseCPM: formatData.cpm,
    baseImpressions: formatData.baseImpressions
  })

  // Reset form
  newItem.value = {
    type: 'print',
    format: '',
    quantity: 1,
    customPrice: null
  }
  showAddForm.value = false
}

function removeItem(id) {
  mediaItems.value = mediaItems.value.filter(item => item.id !== id)
}

function getTypeName(type) {
  const names = {
    print: 'Print',
    digital: 'Digital',
    social: 'Réseaux Sociaux'
  }
  return names[type] || type
}

function getTypeBadgeStyle(type) {
  const styles = {
    print: { backgroundColor: '#E5E7EB', color: '#E2001A' },
    digital: { backgroundColor: '#E5E7EB', color: '#3F3F41' },
    social: { backgroundColor: '#E5E7EB', color: '#E2001A' }
  }
  return styles[type] || { backgroundColor: '#E5E7EB', color: '#3F3F41' }
}

function getTypeBadgeClass(type) {
  const classes = {
    print: 'bg-red-50 text-cm-red',
    digital: 'bg-gray-100 text-cm-dark',
    social: 'bg-red-50 text-cm-red'
  }
  return classes[type] || 'bg-gray-100 text-cm-dark'
}

function formatNumber(num) {
  return new Intl.NumberFormat('fr-FR').format(Math.round(num))
}

function formatCurrency(num) {
  return new Intl.NumberFormat('fr-FR', { 
    style: 'currency', 
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num)
}

function formatPercent(num) {
  return `${num.toFixed(1)}%`
}

function exportResults() {
  if (!kpiResults.value) return

  // Sauvegarder les données dans localStorage pour la page d'export
  const exportData = {
    kpiResults: kpiResults.value,
    mediaItems: mediaItems.value,
    campaignName: campaignName.value
  }
  localStorage.setItem('kpiExportData', JSON.stringify(exportData))

  // Naviguer vers la page d'export
  router.push('/kpi-export')
}

function handleFileImport(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      // Pour un vrai import Excel, il faudrait utiliser une librairie comme xlsx
      // Ici on simule avec un parsing CSV basique
      const content = e.target.result
      const lines = content.split('\n').filter(line => line.trim())
      
      // Skip header row
      const dataLines = lines.slice(1)
      
      dataLines.forEach(line => {
        const cols = line.split(/[,;]/).map(c => c.trim())
        if (cols.length >= 3) {
          const [typeName, formatName, quantity, customCpm] = cols
          
          // Trouver le type
          let type = 'print'
          if (typeName.toLowerCase().includes('digital')) type = 'digital'
          else if (typeName.toLowerCase().includes('social') || typeName.toLowerCase().includes('réseau')) type = 'social'
          
          // Trouver le format correspondant
          const formatData = formats[type]?.find(f => 
            f.name.toLowerCase().includes(formatName.toLowerCase()) ||
            formatName.toLowerCase().includes(f.name.toLowerCase())
          )
          
          if (formatData) {
            mediaItems.value.push({
              id: Date.now() + Math.random(),
              type,
              format: formatData.id,
              formatName: formatData.name,
              quantity: parseInt(quantity) || 1,
              customPrice: customCpm ? parseFloat(customCpm) : null,
              baseCPM: formatData.cpm,
              baseImpressions: formatData.baseImpressions
            })
          }
        }
      })
      
      if (mediaItems.value.length > 0) {
        showAddForm.value = false
      }
    } catch (error) {
      console.error('Erreur lors de l\'import:', error)
      alert('Erreur lors de l\'import du fichier. Vérifiez le format.')
    }
  }
  
  reader.readAsText(file)
  // Reset input pour permettre de réimporter le même fichier
  event.target.value = ''
}
</script>

<template>
  <div class="h-full flex flex-col md:flex-row gap-3 md:gap-6 p-3 md:p-6 bg-cm-gray">
    <!-- Panneau gauche : Configuration -->
    <div class="w-full md:w-1/2 flex flex-col min-h-0">
      <div class="bg-white rounded-xl md:rounded-2xl shadow-lg flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-red text-white flex-shrink-0 rounded-t-xl md:rounded-t-2xl">
          <h2 class="text-base md:text-lg font-semibold">Configuration du Plan Média</h2>
        </div>

        <!-- Contenu scrollable -->
        <div class="flex-1 overflow-auto p-3 md:p-4 space-y-3">
          <!-- Nom campagne -->
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Campagne</label>
            <input 
              v-model="campaignName"
              type="text"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-cm-red focus:border-transparent bg-gray-50 text-cm-dark"
              placeholder="Nom de la campagne"
            />
          </div>

          <!-- Boutons d'action -->
          <div class="flex gap-2">
            <button 
              @click="showAddForm = !showAddForm"
              class="flex-1 px-3 py-2 text-xs text-white rounded-lg hover:opacity-90 transition-colors flex items-center justify-center gap-1.5 bg-cm-red"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Ajouter manuellement
            </button>
            <label class="flex-1 px-3 py-2 text-xs text-cm-dark rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center gap-1.5 bg-gray-50 border border-gray-200 cursor-pointer">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Importer Excel
              <input type="file" accept=".xlsx,.xls,.csv" @change="handleFileImport" class="hidden" />
            </label>
          </div>

          <!-- Formulaire d'ajout -->
          <div v-if="showAddForm" class="p-3 rounded-xl bg-gray-50 border border-gray-200 space-y-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Support</label>
                <select 
                  v-model="newItem.type"
                  @change="newItem.format = ''"
                  class="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg bg-white text-cm-dark"
                >
                  <option value="print">Print</option>
                  <option value="digital">Digital</option>
                  <option value="social">Réseaux Sociaux</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Format</label>
                <select 
                  v-model="newItem.format"
                  class="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg bg-white text-cm-dark"
                >
                  <option value="">Sélectionner...</option>
                  <option v-for="format in formats[newItem.type]" :key="format.id" :value="format.id">
                    {{ format.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Quantité</label>
                <input 
                  v-model.number="newItem.quantity"
                  type="number"
                  min="1"
                  class="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg bg-white text-cm-dark"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">CPM</label>
                <input 
                  v-model.number="newItem.customPrice"
                  type="number"
                  step="0.01"
                  placeholder="Défaut"
                  class="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg bg-white text-cm-dark"
                />
              </div>
            </div>
            <div class="flex gap-2">
              <button 
                @click="addMediaItem"
                :disabled="!newItem.format"
                class="flex-1 px-3 py-1.5 text-xs text-white rounded-lg disabled:opacity-50 bg-cm-red"
              >
                Ajouter
              </button>
              <button 
                @click="showAddForm = false"
                class="px-3 py-1.5 text-xs rounded-lg bg-gray-200 text-cm-dark"
              >
                Annuler
              </button>
            </div>
          </div>

          <!-- Liste des insertions -->
          <div v-if="mediaItems.length === 0" class="text-center py-6 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50">
            <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-xs text-gray-400">Aucune insertion</p>
          </div>

          <div v-else class="space-y-1.5">
            <div 
              v-for="item in mediaItems" 
              :key="item.id"
              class="flex items-center justify-between p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors text-xs"
            >
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5">
                  <span :class="['px-1.5 py-0.5 text-[10px] font-semibold rounded-full', getTypeBadgeClass(item.type)]">
                    {{ getTypeName(item.type) }}
                  </span>
                  <span class="font-medium text-cm-dark truncate">{{ item.formatName }}</span>
                  <span class="text-gray-400">×{{ item.quantity }}</span>
                </div>
                <div class="text-[10px] text-gray-400 mt-0.5">
                  {{ formatCurrency(((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM)) }}
                </div>
              </div>
              <button 
                @click="removeItem(item.id)"
                class="p-1 rounded text-gray-300 hover:text-cm-red hover:bg-red-50"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Footer avec total -->
        <div v-if="kpiResults" class="px-3 md:px-4 py-2 md:py-3 border-t border-gray-100 bg-gray-50 flex-shrink-0">
          <div class="flex justify-between items-center text-sm">
            <span class="text-gray-500">Budget total</span>
            <span class="font-bold text-cm-red">{{ formatCurrency(kpiResults.totalCost) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Panneau droit : Résultats KPI -->
    <div class="w-full md:w-1/2 flex flex-col min-h-0">
      <div class="bg-white rounded-xl md:rounded-2xl shadow-lg flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-dark text-white flex-shrink-0 rounded-t-xl md:rounded-t-2xl">
          <h2 class="text-base md:text-lg font-semibold">Indicateurs KPI</h2>
        </div>

        <!-- Contenu -->
        <div v-if="!kpiResults" class="flex-1 flex items-center justify-center">
          <div class="text-center p-8">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-700 mb-2">KPI en attente</h3>
            <p class="text-sm text-gray-500">Ajoutez des insertions pour voir les indicateurs</p>
          </div>
        </div>

        <div v-else class="flex-1 overflow-auto p-3 md:p-4 space-y-5">
          <!-- KPI Impact & Exposition -->
          <div>
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Impact & Exposition
            </h4>
            <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div class="p-4 rounded-xl bg-red-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Audience</p>
                <p class="text-2xl font-bold text-cm-red">{{ formatNumber(kpiResults.audienceCumuleeDedupliquee) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-gray-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Couverture</p>
                <p class="text-2xl font-bold text-cm-dark">{{ formatPercent(kpiResults.tauxCouverture) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-red-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Fréquence</p>
                <p class="text-2xl font-bold text-cm-red">{{ kpiResults.frequenceMoyenne.toFixed(1) }}×</p>
              </div>
              <div class="p-4 rounded-xl bg-gray-50">
                <p class="text-xs text-gray-500 uppercase mb-1">GRP</p>
                <p class="text-2xl font-bold text-cm-dark">{{ kpiResults.grp.toFixed(1) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-red-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Impressions</p>
                <p class="text-2xl font-bold text-cm-red">{{ formatNumber(kpiResults.totalImpressions) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-gray-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Vues Vidéo</p>
                <p class="text-2xl font-bold text-cm-dark">{{ formatNumber(kpiResults.vuesVideoTotal) }}</p>
              </div>
            </div>
          </div>

          <!-- KPI Financier -->
          <div>
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Efficacité Financière
            </h4>
            <div class="grid grid-cols-2 gap-3">
              <div class="p-4 rounded-xl bg-red-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Budget</p>
                <p class="text-2xl font-bold text-cm-red">{{ formatCurrency(kpiResults.totalCost) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-gray-50">
                <p class="text-xs text-gray-500 uppercase mb-1">CPM Moyen</p>
                <p class="text-2xl font-bold text-cm-dark">{{ formatCurrency(kpiResults.cpmMoyen) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-red-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Coût GRP</p>
                <p class="text-2xl font-bold text-cm-red">{{ formatCurrency(kpiResults.coutGRP) }}</p>
              </div>
              <div class="p-4 rounded-xl bg-gray-50">
                <p class="text-xs text-gray-500 uppercase mb-1">Clics</p>
                <p class="text-2xl font-bold text-cm-dark">{{ formatNumber(kpiResults.totalClics) }}</p>
              </div>
            </div>
          </div>

          <!-- Répartition par Support -->
          <div>
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              </svg>
              Répartition par Support
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <template v-for="(data, type) in kpiResults.bySupport" :key="type">
                <div v-if="data.items > 0" class="p-4 rounded-xl bg-gray-50">
                  <div class="flex items-center justify-between mb-3">
                    <span :class="['px-2.5 py-1 text-xs font-semibold rounded-full', getTypeBadgeClass(type)]">
                      {{ getTypeName(type) }}
                    </span>
                    <span class="text-lg font-bold text-cm-dark">{{ formatCurrency(data.cost) }}</span>
                  </div>
                  <div class="grid grid-cols-2 gap-2 text-xs mb-3">
                    <div>
                      <span class="text-gray-400">Impressions</span>
                      <p class="font-semibold text-cm-dark text-base">{{ formatNumber(data.impressions) }}</p>
                    </div>
                    <div>
                      <span class="text-gray-400">Part</span>
                      <p class="font-semibold text-cm-red text-base">{{ formatPercent(kpiResults.repartitionBudget[type]) }}</p>
                    </div>
                  </div>
                  <div class="w-full rounded-full h-2 bg-gray-200">
                    <div class="h-2 rounded-full bg-cm-red transition-all" :style="{ width: `${kpiResults.repartitionBudget[type]}%` }"></div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- Tableau récapitulatif -->
          <div class="flex-1">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Détail du Plan
            </h4>
            <div class="overflow-x-auto rounded-xl border border-gray-100">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Support</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
                    <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Qté</th>
                    <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Coût</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in mediaItems" :key="item.id" class="hover:bg-gray-50">
                    <td class="px-4 py-3">
                      <span :class="['px-2 py-1 text-xs font-semibold rounded-full', getTypeBadgeClass(item.type)]">
                        {{ getTypeName(item.type) }}
                      </span>
                    </td>
                    <td class="px-4 py-3 font-medium text-cm-dark">{{ item.formatName }}</td>
                    <td class="px-4 py-3 text-center text-gray-500">{{ item.quantity }}</td>
                    <td class="px-4 py-3 text-right font-semibold text-cm-dark">
                      {{ formatCurrency(((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM)) }}
                    </td>
                  </tr>
                </tbody>
                <tfoot class="bg-gray-50 border-t-2 border-gray-200">
                  <tr>
                    <td colspan="3" class="px-4 py-3 text-right font-bold text-cm-dark">TOTAL</td>
                    <td class="px-4 py-3 text-right font-bold text-cm-red text-lg">{{ formatCurrency(kpiResults.totalCost) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

        <!-- Footer avec bouton export -->
        <div v-if="kpiResults" class="px-3 md:px-4 py-2 md:py-3 border-t border-gray-100 flex-shrink-0 flex justify-end">
          <button 
            @click="exportResults"
            class="px-4 py-2 text-sm text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2 bg-cm-red"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            Exporter PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>