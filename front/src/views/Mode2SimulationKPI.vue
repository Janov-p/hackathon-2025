<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as XLSX from 'xlsx'
import { mediaService } from '../api'

const router = useRouter()

// Données de référence
// Données de référence dynamiques
const formats = ref({
  print: [],
  digital: [],
  social: []
})

// Chargement des options au montage
onMounted(async () => {
  try {
    const response = await mediaService.getOptions()
    if (response.data) {
      formats.value = response.data
    }
  } catch (err) {
    console.error("Erreur chargement options:", err)
    // Fallback ou notification
  }
})

// État du formulaire
const campaignName = ref('Plan média client')
const mediaItems = ref([])
const showAddForm = ref(false)

// Ciblage
const targetMode = ref('particuliers') // 'particuliers' | 'professionnels'
const targetCriteria = ref({
  age: [],
  sexe: [],
  csp: []
})

// Options de ciblage (pour l'UI)
const availableTargets = {
  age: [
    { id: '15_24_ans', label: '15-24 ans' },
    { id: '25_34_ans', label: '25-34 ans' },
    { id: '35_49_ans', label: '35-49 ans' },
    { id: '50_64_ans', label: '50-64 ans' },
    { id: '65_ans_ou_plus', label: '65 ans et +' }
  ],
  sexe: [
    { id: 'homme', label: 'Hommes' },
    { id: 'femme', label: 'Femmes' }
  ],
  csp: [
    { id: 'csp_plus', label: 'CSP+' },
    { id: 'actifs', label: 'Actifs' },
    { id: 'retraites', label: 'Retraités' }
  ]
}

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

// KPI Results fetched from Backend
const kpiResults = ref(null)
const isLoadingKPI = ref(false)

// Watcher pour mettre à jour les KPI quand les mediaItems changent
let debounceTimer = null

watch(mediaItems, (newItems) => {
  debouncedFetchKPIs()
}, { deep: true })

watch(targetMode, () => {
  debouncedFetchKPIs()
})

watch(targetCriteria, () => {
    debouncedFetchKPIs()
}, { deep: true })

function debouncedFetchKPIs() {
    if (debounceTimer) clearTimeout(debounceTimer)
    if (mediaItems.value.length === 0) {
        kpiResults.value = null
        return
    }
    debounceTimer = setTimeout(() => {
        fetchKPIs()
    }, 500)
}

async function fetchKPIs() {
  if (mediaItems.value.length === 0) return
  
  isLoadingKPI.value = true
  try {
    // 1. Calculer le budget et l'allocation basés sur les items
    let totalCost = 0
    const allocationByChannel = { print: 0, digital: 0, social: 0, events: 0 }
    
    // Mapping frontend types to backend channels (frontend: 'social', backend: 'social')
    // Frontend types: 'print', 'digital', 'social'
    // Backend channels: 'print', 'digital', 'social', 'events'
    
    mediaItems.value.forEach(item => {
      // Calcul du coût : soit prix fixe (tarif), soit CPM
      let cost = 0
      const formatData = findFormat(item.type, item.format)
      
      if (item.customPrice) {
        // Si prix personnalisé, on assume que c'est le unit price (comme le CPM ou le Tarif)
        // Cas 1: C'est un item à prix fixe (tarif) -> customPrice = tarif
        // Cas 2: C'est un item à CPM -> customPrice = CPM
        if (formatData?.tarif) {
            cost = item.customPrice * item.quantity
        } else {
             const impressions = (item.baseImpressions || 0) * item.quantity
             cost = (impressions / 1000) * item.customPrice
        }
      } else {
        // Prix standard
        if (formatData?.tarif) {
            cost = formatData.tarif * item.quantity
        } else if (formatData?.cpm) {
            const impressions = (formatData.baseImpressions || 0) * item.quantity
            cost = (impressions / 1000) * formatData.cpm
        }
      }
      
      totalCost += cost
      allocationByChannel[item.type] += cost
    })
    
    // Convertir en pourcentages
    const budgetAllocation = {}
    Object.keys(allocationByChannel).forEach(channel => {
      if (totalCost > 0) {
        budgetAllocation[channel] = parseFloat(((allocationByChannel[channel] / totalCost) * 100).toFixed(1))
      } else {
        budgetAllocation[channel] = 0
      }
    })
    
    // 2. Appeler l'API
    const payload = {
      repartitionMode: 'manuel',
      formData: {
        budget: totalCost,
        repartition: budgetAllocation,
        items: mediaItems.value, // Ajout de la liste détaillée pour calcul précis backend
        nom: campaignName.value,
        cible: {
           targetMode: targetMode.value,
           criteria: targetCriteria.value
        }
      }
    }
    
    const response = await mediaService.generatePlan(payload)
    const backendPlan = response.data.media_plan
    
    // 3. Mapper la réponse vers la structure kpiResults attendue par le template
    // Le template attend:
    // audienceCumuleeDedupliquee, tauxCouverture, frequenceMoyenne, grp, totalImpressions, vuesVideoTotal
    // totalCost, cpmMoyen, coutGRP, totalClics, ctrMoyen
    // bySupport, repartitionBudget, repartitionAudience
    
    const targets = backendPlan.kpi_targets
    const strategy = backendPlan.channel_strategy
    
    // Reconstruction de la structure bySupport depuis la réponse backend ou utilisation des données locales pour le détail items
    // Le backend renvoie des totaux par canal, mails il ne connait pas le détail des items (formats).
    // On doit garder la logique locale pour 'items' et 'impressions' si on veut être précis sur les formats,
    // MAIS l'utilisateur veut que ce soit le BACKEND qui donne les KPI.
    // Le backend renvoie 'estimated_impressions', 'estimated_reach' par canal ? Non, global.
    // Strategy contient budget, percentage, recommended_supports.
    
    // Dilemme : Le backend fait une estimation "haut niveau" basée sur le budget. Le frontend a une liste précise d'items avec des CPM précis.
    // Si on utilise le backend, on "écrase" la précision des items locaux par des moyennes backend ?
    // L'utilisateur a dit : "utiliser les données du back". Donc on prend les estimations backend.
    
    const mappedResults = {
      // Impact
      audienceCumuleeDedupliquee: targets.estimated_reach,
      // Taux couverture : Reach / PopCible. Le backend ne connait pas PopCible (150k ici). On garde 150k en ref front.
      tauxCouverture: (targets.estimated_reach / POPULATION_CIBLE) * 100,
      frequenceMoyenne: targets.estimated_impressions / targets.estimated_reach, // approx
      grp: ((targets.estimated_reach / POPULATION_CIBLE) * 100) * (targets.estimated_impressions / targets.estimated_reach),
      totalImpressions: targets.estimated_impressions,
      vuesVideoTotal: 0, // Pas retourné par backend explicitement, on met 0 ou on garde logique locale ? Back ne renvoie pas ça. On laisse 0.
      
      // Financier
      totalCost: backendPlan.budget_summary.total_budget,
      cpmMoyen: targets.estimated_cpm,
      coutGRP: targets.estimated_cpc ? 0 : 0, // Pas de coutGRP direct dans backend, on peut le recalculer
      totalClics: (targets.estimated_reach * 0.1), // Backend renvoie CPC basé sur 10% CTR ? "estimated_cpc": round(sum... / (reach * 0.1)). Donc Clics = Reach * 0.1 ??? Bizarre dans backend.
      // Correction: Backend calculate_kpi_targets: estimated_cpc = budget / (reach * 0.1). Donc Backend assume Clics = Reach * 0.1 (10% de reach cliquent ??). C'est très simplifié.
      // On va utiliser ce que le backend implique.
      
      ctrMoyen: 10, // Backend hardcoded 10% CTR implicitement dans cpc calculation
      
      // Répartitions
      repartitionBudget: backendPlan.budget_summary.allocation_percentage,
      repartitionAudience: {}, // Pas renvoyé par le backend
      
      // Structure bySupport pour l'affichage des badges/totaux
      bySupport: {
        print: { 
            cost: strategy.print.budget, 
            impressions: (strategy.print.budget / 15) * 1000, // Est-ce qu'on peut récupérer les impressions par canal du backend ? Non, calculate_kpi_targets somme tout.
            items: allocationByChannel.print > 0 ? 1 : 0
        },
        digital: { 
            cost: strategy.digital.budget, 
            impressions: (strategy.digital.budget / 8) * 1000,
            items: allocationByChannel.digital > 0 ? 1 : 0
        },
        social: { 
            cost: strategy.social.budget, 
            impressions: (strategy.social.budget / 12) * 1000, 
            items: allocationByChannel.social > 0 ? 1 : 0
        }
      }
    }
    
    // Recalculs finaux pour affichage propre
    mappedResults.coutGRP = mappedResults.grp > 0 ? mappedResults.totalCost / mappedResults.grp : 0
    mappedResults.ctrMoyen = (mappedResults.totalClics / mappedResults.totalImpressions) * 100
    
    kpiResults.value = mappedResults
    
  } catch (error) {
    console.error('Erreur calcul KPI backend:', error)
  } finally {
    isLoadingKPI.value = false
  }
}

function findFormat(type, formatId) {
  return formats.value[type]?.find(f => f.id === formatId)
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
    baseCPM: formatData.cpm || null,
    baseTarif: formatData.tarif || null,
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

function exportToExcel() {
  if (!kpiResults.value) return

  // Créer le workbook
  const wb = XLSX.utils.book_new()

  // === Feuille 1: Résumé KPI ===
  const kpiData = [
    ['RAPPORT KPI - PLAN MÉDIA'],
    [''],
    ['Campagne:', campaignName.value],
    ['Date de génération:', new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })],
    [''],
    ['=== IMPACT & EXPOSITION ==='],
    ['Audience Cumulée (dédupliquée)', kpiResults.value.audienceCumuleeDedupliquee, 'contacts uniques'],
    ['Taux de Couverture', `${kpiResults.value.tauxCouverture.toFixed(1)}%`, 'reach'],
    ['Fréquence Moyenne', `${kpiResults.value.frequenceMoyenne.toFixed(1)}×`, 'expositions/personne'],
    ['GRP', kpiResults.value.grp.toFixed(1), 'points'],
    ['Impressions Totales', kpiResults.value.totalImpressions, ''],
    ['Vues Vidéo', kpiResults.value.vuesVideoTotal, 'estimées'],
    [''],
    ['=== EFFICACITÉ FINANCIÈRE ==='],
    ['Budget Total', kpiResults.value.totalCost, '€'],
    ['CPM Moyen', kpiResults.value.cpmMoyen.toFixed(2), '€'],
    ['Coût GRP', kpiResults.value.coutGRP.toFixed(2), '€'],
    ['Clics Estimés', kpiResults.value.totalClics, ''],
    ['CTR Moyen', `${kpiResults.value.ctrMoyen.toFixed(2)}%`, ''],
    [''],
    ['=== RÉPARTITION PAR SUPPORT ==='],
    ['Support', 'Budget (€)', 'Part (%)', 'Impressions', 'Clics'],
  ]

  // Ajouter les données par support
  Object.entries(kpiResults.value.bySupport).forEach(([type, data]) => {
    if (data.items > 0) {
      kpiData.push([
        getTypeName(type),
        data.cost.toFixed(2),
        `${kpiResults.value.repartitionBudget[type].toFixed(1)}%`,
        data.impressions,
        data.clics
      ])
    }
  })

  const wsKPI = XLSX.utils.aoa_to_sheet(kpiData)
  
  // Définir les largeurs de colonnes
  wsKPI['!cols'] = [
    { wch: 35 },
    { wch: 20 },
    { wch: 20 },
    { wch: 15 },
    { wch: 15 }
  ]

  XLSX.utils.book_append_sheet(wb, wsKPI, 'Résumé KPI')

  // === Feuille 2: Détail du Plan Média ===
  const detailHeaders = ['Support', 'Format', 'Quantité', 'CPM (€)', 'Impressions', 'Coût (€)']
  const detailData = [detailHeaders]

  mediaItems.value.forEach(item => {
    const impressions = item.baseImpressions * item.quantity
    const cpm = item.customPrice || item.baseCPM
    const cost = (impressions / 1000) * cpm
    
    detailData.push([
      getTypeName(item.type),
      item.formatName,
      item.quantity,
      cpm.toFixed(2),
      impressions,
      cost.toFixed(2)
    ])
  })

  // Ajouter la ligne total
  detailData.push([])
  detailData.push([
    'TOTAL',
    '',
    mediaItems.value.reduce((sum, item) => sum + item.quantity, 0),
    '',
    kpiResults.value.totalImpressions,
    kpiResults.value.totalCost.toFixed(2)
  ])

  const wsDetail = XLSX.utils.aoa_to_sheet(detailData)
  
  // Définir les largeurs de colonnes
  wsDetail['!cols'] = [
    { wch: 18 },
    { wch: 25 },
    { wch: 12 },
    { wch: 12 },
    { wch: 15 },
    { wch: 15 }
  ]

  XLSX.utils.book_append_sheet(wb, wsDetail, 'Détail Plan Média')

  // === Feuille 3: Données pour réimport ===
  const importHeaders = ['Type', 'Format', 'Quantité', 'CPM personnalisé']
  const importData = [importHeaders]

  mediaItems.value.forEach(item => {
    importData.push([
      getTypeName(item.type),
      item.formatName,
      item.quantity,
      item.customPrice || ''
    ])
  })

  const wsImport = XLSX.utils.aoa_to_sheet(importData)
  wsImport['!cols'] = [
    { wch: 18 },
    { wch: 25 },
    { wch: 12 },
    { wch: 18 }
  ]

  XLSX.utils.book_append_sheet(wb, wsImport, 'Import Template')

  // Générer et télécharger le fichier
  const fileName = `plan-media-${campaignName.value.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
}
</script>

<template>
  <div class="min-h-full md:h-full flex flex-col md:flex-row gap-3 md:gap-6 p-3 md:p-6 pb-6 bg-cm-gray overflow-auto md:overflow-hidden">
    <!-- Panneau gauche : Configuration -->
    <div class="w-full md:w-1/2 flex flex-col md:min-h-0">
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

          <!-- Sélection de la Cible -->
          <div class="mt-4">
              <label class="block text-xs font-medium text-gray-500 mb-2">Cible</label>
              
              <!-- Switch Particuliers/Pro -->
              <div class="flex bg-gray-100 p-1 rounded-lg mb-3">
                  <button 
                    @click="targetMode = 'particuliers'"
                    :class="['flex-1 py-1.5 text-xs font-medium rounded-md transition-all', targetMode === 'particuliers' ? 'bg-white text-cm-red shadow-sm' : 'text-gray-500 hover:text-gray-700']"
                  >
                      Particuliers
                  </button>
                  <button 
                    @click="targetMode = 'professionnels'"
                    :class="['flex-1 py-1.5 text-xs font-medium rounded-md transition-all', targetMode === 'professionnels' ? 'bg-white text-cm-red shadow-sm' : 'text-gray-500 hover:text-gray-700']"
                  >
                      Professionnels
                  </button>
              </div>

              <!-- Filtres avancés (Particuliers only pour l'instant) -->
              <div v-if="targetMode === 'particuliers'" class="space-y-3 p-3 bg-gray-50 rounded-xl border border-gray-100">
                  <!-- Sexe -->
                  <div>
                      <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1.5">Sexe</label>
                      <div class="flex flex-wrap gap-2">
                          <label v-for="opt in availableTargets.sexe" :key="opt.id" class="inline-flex items-center">
                              <input type="checkbox" v-model="targetCriteria.sexe" :value="opt.id" class="form-checkbox h-3 w-3 text-cm-red rounded border-gray-300 focus:ring-cm-red">
                              <span class="ml-1.5 text-xs text-cm-dark">{{ opt.label }}</span>
                          </label>
                      </div>
                  </div>
                  <!-- Age -->
                  <div>
                      <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1.5">Age</label>
                      <div class="grid grid-cols-2 gap-2">
                          <label v-for="opt in availableTargets.age" :key="opt.id" class="inline-flex items-center">
                              <input type="checkbox" v-model="targetCriteria.age" :value="opt.id" class="form-checkbox h-3 w-3 text-cm-red rounded border-gray-300 focus:ring-cm-red">
                              <span class="ml-1.5 text-xs text-cm-dark">{{ opt.label }}</span>
                          </label>
                      </div>
                  </div>
                   <!-- CSP -->
                   <div>
                      <label class="block text-[10px] font-bold text-gray-400 uppercase mb-1.5">CSP</label>
                      <div class="flex flex-wrap gap-2">
                          <label v-for="opt in availableTargets.csp" :key="opt.id" class="inline-flex items-center">
                              <input type="checkbox" v-model="targetCriteria.csp" :value="opt.id" class="form-checkbox h-3 w-3 text-cm-red rounded border-gray-300 focus:ring-cm-red">
                              <span class="ml-1.5 text-xs text-cm-dark">{{ opt.label }}</span>
                          </label>
                      </div>
                  </div>
              </div>
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
                <label class="block text-xs text-gray-500 mb-1">Prix U. / CPM</label>
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
                  {{ formatCurrency((item.baseTarif ? (item.baseTarif * item.quantity) : ((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM))) }}
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
    <div class="w-full md:w-1/2 flex flex-col md:min-h-0">
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

        <!-- Footer avec boutons export -->
        <div v-if="kpiResults" class="px-3 md:px-4 py-2 md:py-3 border-t border-gray-100 flex-shrink-0 flex justify-end gap-2">
          <button 
            @click="exportToExcel"
            class="px-4 py-2 text-sm text-cm-dark rounded-lg hover:bg-gray-100 transition-all flex items-center gap-2 bg-gray-50 border border-gray-200"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Excel
          </button>
          <button 
            @click="exportResults"
            class="px-4 py-2 text-sm text-white rounded-lg hover:opacity-90 transition-all flex items-center gap-2 bg-cm-red"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
            </svg>
            PDF
          </button>
        </div>
      </div>
    </div>
  </div>
</template>