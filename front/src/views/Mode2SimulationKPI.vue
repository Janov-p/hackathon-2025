<script setup>
import { ref, computed } from 'vue'

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
  alert('Export PDF - Fonctionnalité à implémenter')
}
</script>

<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="p-6 rounded-xl border" style="background-color: #E5E7EB; border-color: #3F3F41;">
      <div class="flex items-start justify-between">
        <div>
          <h2 class="text-2xl font-bold mb-2" style="color: #3F3F41;">Simulation KPI Prévisionnels</h2>
          <p style="color: #3F3F41;">
            Saisissez votre plan média existant pour calculer les indicateurs de performance
          </p>
        </div>
        <div class="flex items-center gap-2" style="color: #E2001A;">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Formulaire -->
    <div class="rounded-xl shadow-sm border p-6" style="background-color: #FFFFFF; border-color: #3F3F41;">
      <div class="mb-6">
        <label class="block text-sm font-medium mb-2" style="color: #3F3F41;">
          Nom de la campagne
        </label>
        <input 
          v-model="campaignName"
          type="text"
          class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent"
          style="border-color: #E5E7EB; background-color: #FFFFFF; color: #3F3F41;"
          @focus="$event.target.style.boxShadow = 'inset 0 0 0 2px #E2001A'"
          @blur="$event.target.style.boxShadow = 'none'"
          placeholder="Ex: Campagne 2025"
        />
      </div>

      <!-- Liste des insertions -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold" style="color: #3F3F41;">Insertions média</h3>
          <button 
            @click="showAddForm = !showAddForm"
            class="px-4 py-2 text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
            style="background-color: #E2001A;"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Ajouter une insertion
          </button>
        </div>

        <!-- Formulaire d'ajout -->
        <div v-if="showAddForm" class="p-4 rounded-lg mb-4 border" style="background-color: #E5E7EB; border-color: #3F3F41;">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: #3F3F41;">Type de support</label>
              <select 
                v-model="newItem.type"
                @change="newItem.format = ''"
                class="w-full px-3 py-2 border rounded-lg"
                style="border-color: #E5E7EB; background-color: #FFFFFF; color: #3F3F41;"
              >
                <option value="print">Print</option>
                <option value="digital">Digital</option>
                <option value="social">Réseaux Sociaux</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1" style="color: #3F3F41;">Format</label>
              <select 
                v-model="newItem.format"
                class="w-full px-3 py-2 border rounded-lg"
                style="border-color: #E5E7EB; background-color: #FFFFFF; color: #3F3F41;"
              >
                <option value="">Sélectionner...</option>
                <option 
                  v-for="format in formats[newItem.type]" 
                  :key="format.id" 
                  :value="format.id"
                >
                  {{ format.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1" style="color: #3F3F41;">Quantité</label>
              <input 
                v-model.number="newItem.quantity"
                type="number"
                min="1"
                class="w-full px-3 py-2 border rounded-lg"
                style="border-color: #E5E7EB; background-color: #FFFFFF; color: #3F3F41;"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1" style="color: #3F3F41;">CPM</label>
              <input 
                v-model.number="newItem.customPrice"
                type="number"
                step="0.01"
                placeholder="CPM par défaut"
                class="w-full px-3 py-2 border rounded-lg"
                style="border-color: #E5E7EB; background-color: #FFFFFF; color: #3F3F41;"
              />
            </div>
          </div>

          <div class="flex gap-2 mt-4">
            <button 
              @click="addMediaItem"
              :disabled="!newItem.format"
              class="px-4 py-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
              style="background-color: #E2001A;"
            >
              Ajouter
            </button>
            <button 
              @click="showAddForm = false"
              class="px-4 py-2 rounded-lg"
              style="background-color: #E5E7EB; color: #3F3F41;"
            >
              Annuler
            </button>
          </div>
        </div>

        <!-- Liste des insertions ajoutées -->
        <div v-if="mediaItems.length === 0" class="text-center py-12 rounded-lg border-2 border-dashed" style="background-color: #E5E7EB; border-color: #3F3F41;">
          <svg class="w-16 h-16 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #3F3F41;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="font-medium" style="color: #3F3F41;">Aucune insertion ajoutée</p>
          <p class="text-sm mt-1" style="color: #3F3F41;">Cliquez sur "Ajouter une insertion" pour commencer</p>
        </div>

        <div v-else class="space-y-2">
          <div 
            v-for="item in mediaItems" 
            :key="item.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:opacity-90 transition-colors"
            style="background-color: #FFFFFF; border-color: #E5E7EB;"
          >
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="{
                    'print': item.type === 'print',
                    'digital': item.type === 'digital',
                    'social': item.type === 'social'
                  }"
                  :style="getTypeBadgeStyle(item.type)"
                >
                  {{ getTypeName(item.type) }}
                </span>
                <span class="font-medium" style="color: #3F3F41;">{{ item.formatName }}</span>
                <span style="color: #3F3F41;">× {{ item.quantity }}</span>
              </div>
              <div class="text-sm mt-1" style="color: #3F3F41;">
                CPM: {{ formatCurrency(item.customPrice || item.baseCPM) }} • 
                Impressions: {{ formatNumber(item.baseImpressions * item.quantity) }}
              </div>
            </div>
            <button 
              @click="removeItem(item.id)"
              class="p-2 rounded-lg transition-colors"
              style="color: #E2001A;"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Résultats KPI -->
    <div v-if="kpiResults" class="space-y-6">
      <!-- KPIs principaux - Impact & Exposition -->
      <div>
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2" style="color: #3F3F41;">
          KPI d'Impact & Exposition
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #E2001A 0%, #A80013 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Audience Cumulée Dédupliquée</div>
            <div class="text-3xl font-bold">{{ formatNumber(kpiResults.audienceCumuleeDedupliquee) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Contacts uniques estimés</div>
          </div>

          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #3F3F41 0%, #1F1F21 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Taux de Couverture (Reach)</div>
            <div class="text-3xl font-bold">{{ formatPercent(kpiResults.tauxCouverture) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">De la population cible</div>
          </div>

          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #E2001A 0%, #8B000E 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Fréquence Moyenne</div>
            <div class="text-3xl font-bold">{{ kpiResults.frequenceMoyenne.toFixed(1) }}×</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Expositions par personne</div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div class="p-6 rounded-xl border-2" style="background-color: #FFFFFF; border-color: #E2001A;">
            <div class="text-sm font-medium mb-1" style="color: #3F3F41;">GRP (Gross Rating Point)</div>
            <div class="text-2xl font-bold" style="color: #E2001A;">{{ kpiResults.grp.toFixed(1) }}</div>
            <div class="text-xs mt-1" style="color: #3F3F41;">Couverture × Fréquence</div>
          </div>

          <div class="p-6 rounded-xl border-2" style="background-color: #FFFFFF; border-color: #E2001A;">
            <div class="text-sm font-medium mb-1" style="color: #3F3F41;">Impressions Estimées</div>
            <div class="text-2xl font-bold" style="color: #E2001A;">{{ formatNumber(kpiResults.totalImpressions) }}</div>
            <div class="text-xs mt-1" style="color: #3F3F41;">Tous supports confondus</div>
          </div>

          <div class="p-6 rounded-xl border-2" style="background-color: #FFFFFF; border-color: #E2001A;">
            <div class="text-sm font-medium mb-1" style="color: #3F3F41;">Vues Vidéo Estimées</div>
            <div class="text-2xl font-bold" style="color: #E2001A;">{{ formatNumber(kpiResults.vuesVideoTotal) }}</div>
            <div class="text-xs mt-1" style="color: #3F3F41;">Pour pré-roll et vidéos sociales</div>
          </div>
        </div>
      </div>

      <!-- KPI d'Efficacité Financière -->
      <div>
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2" style="color: #3F3F41;">
          KPI d'Efficacité Financière
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #E2001A 0%, #A80013 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Budget Total</div>
            <div class="text-3xl font-bold">{{ formatCurrency(kpiResults.totalCost) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Investissement publicitaire</div>
          </div>

          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #3F3F41 0%, #1F1F21 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">CPM Moyen</div>
            <div class="text-3xl font-bold">{{ formatCurrency(kpiResults.cpmMoyen) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Coût pour mille impressions</div>
          </div>

          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #E2001A 0%, #8B000E 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Coût GRP</div>
            <div class="text-3xl font-bold">{{ formatCurrency(kpiResults.coutGRP) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Coût par point de GRP</div>
          </div>
        </div>
      </div>

      <!-- KPI d'Engagement & Action -->
      <div>
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2" style="color: #3F3F41;">
          KPI d'Engagement & Action
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #E2001A 0%, #A80013 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">Clics Estimés</div>
            <div class="text-3xl font-bold">{{ formatNumber(kpiResults.totalClics) }}</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Interactions prévisionnelles</div>
          </div>

          <div class="text-white p-6 rounded-xl shadow-lg" style="background: linear-gradient(135deg, #3F3F41 0%, #1F1F21 100%);">
            <div class="text-sm font-medium mb-1" style="color: rgba(255, 255, 255, 0.9);">CTR Moyen Prévisionnel</div>
            <div class="text-3xl font-bold">{{ kpiResults.ctrMoyen.toFixed(2) }}%</div>
            <div class="text-xs mt-2" style="color: rgba(255, 255, 255, 0.9);">Taux de clic attendu</div>
          </div>
        </div>
      </div>

      <!-- KPI de Stratégie - Répartition par Support -->
      <div class="rounded-xl shadow-sm border p-6" style="background-color: #FFFFFF; border-color: #3F3F41;">
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2" style="color: #3F3F41;">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #E2001A;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
          KPI de Stratégie - Répartition par Support
        </h3>
        
        <div class="space-y-6">
          <div v-for="(data, type) in kpiResults.bySupport" :key="type">
            <div v-if="data.items > 0" class="space-y-3">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span 
                    class="px-3 py-1 text-sm font-semibold rounded-full"
                    :style="getTypeBadgeStyle(type)"
                  >
                    {{ getTypeName(type) }}
                  </span>
                  <span class="text-sm" style="color: #3F3F41;">{{ data.items }} insertion(s)</span>
                </div>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <!-- Budget -->
                <div class="p-4 rounded-lg" style="background-color: #E5E7EB;">
                  <div class="text-xs font-medium mb-1" style="color: #3F3F41;">Budget</div>
                  <div class="text-lg font-bold" style="color: #3F3F41;">{{ formatCurrency(data.cost) }}</div>
                  <div class="text-xs mt-1" style="color: #3F3F41;">
                    {{ formatPercent(kpiResults.repartitionBudget[type]) }}
                  </div>
                </div>

                <!-- Impressions -->
                <div class="p-4 rounded-lg" style="background-color: #E5E7EB;">
                  <div class="text-xs font-medium mb-1" style="color: #3F3F41;">Impressions</div>
                  <div class="text-lg font-bold" style="color: #3F3F41;">{{ formatNumber(data.impressions) }}</div>
                  <div class="text-xs mt-1" style="color: #3F3F41;">
                    {{ formatPercent(kpiResults.repartitionAudience[type]) }}
                  </div>
                </div>

                <!-- CPM -->
                <div class="p-4 rounded-lg" style="background-color: #E5E7EB;">
                  <div class="text-xs font-medium mb-1" style="color: #3F3F41;">CPM</div>
                  <div class="text-lg font-bold" style="color: #3F3F41;">{{ formatCurrency(data.cpm) }}</div>
                  <div class="text-xs mt-1" style="color: #3F3F41;">Coût/1000</div>
                </div>

                <!-- Clics -->
                <div class="p-4 rounded-lg" style="background-color: #E5E7EB;">
                  <div class="text-xs font-medium mb-1" style="color: #3F3F41;">Clics estimés</div>
                  <div class="text-lg font-bold" style="color: #3F3F41;">{{ formatNumber(data.clics) }}</div>
                  <div class="text-xs mt-1" style="color: #3F3F41;">
                    {{ ((data.clics / kpiResults.totalClics) * 100).toFixed(1) }}%
                  </div>
                </div>

                <!-- Part du total -->
                <div class="p-4 rounded-lg" style="background-color: #E5E7EB;">
                  <div class="text-xs font-medium mb-1" style="color: #3F3F41;">Part du total</div>
                  <div class="text-lg font-bold" style="color: #3F3F41;">
                    {{ formatPercent((data.cost / kpiResults.totalCost) * 100) }} 
                  </div>
                  <div class="text-xs mt-1" style="color: #3F3F41;">Budget</div>
                </div>
              </div>

              <!-- Barres de progression -->
              <div class="space-y-2">
                <div>
                  <div class="flex justify-between text-xs mb-1" style="color: #3F3F41;">
                    <span>Répartition budget</span>
                    <span>{{ formatPercent(kpiResults.repartitionBudget[type]) }}</span>
                  </div>
                  <div class="w-full rounded-full h-2" style="background-color: #E5E7EB;">
                    <div 
                      class="h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${kpiResults.repartitionBudget[type]}%`, 'background-color': '#E2001A' }"
                    ></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-xs mb-1" style="color: #3F3F41;">
                    <span>Répartition audience</span>
                    <span>{{ formatPercent(kpiResults.repartitionAudience[type]) }}</span>
                  </div>
                  <div class="w-full rounded-full h-2" style="background-color: #E5E7EB;">
                    <div 
                      class="h-2 rounded-full transition-all duration-500"
                      :style="{ width: `${kpiResults.repartitionAudience[type]}%`, 'background-color': '#E2001A' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="type !== 'social' || kpiResults.bySupport.social.items > 0" class="my-4" style="border-bottom: 1px solid #3F3F41;"></div>
          </div>
        </div>
      </div>

      <!-- Plan Média Proposé (Budget détaillé) -->
      <div class="rounded-xl shadow-sm border p-6" style="background-color: #FFFFFF; border-color: #3F3F41;">
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2" style="color: #3F3F41;">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #E2001A;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Plan Média Proposé - Budget Détaillé
        </h3>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b-2" style="background-color: #E5E7EB; border-color: #3F3F41;">
              <tr>
                <th class="px-4 py-3 text-left font-semibold" style="color: #3F3F41;">Support</th>
                <th class="px-4 py-3 text-left font-semibold" style="color: #3F3F41;">Format</th>
                <th class="px-4 py-3 text-center font-semibold" style="color: #3F3F41;">Quantité</th>
                <th class="px-4 py-3 text-right font-semibold" style="color: #3F3F41;">CPM</th>
                <th class="px-4 py-3 text-right font-semibold" style="color: #3F3F41;">Impressions</th>
                <th class="px-4 py-3 text-right font-semibold" style="color: #3F3F41;">Coût</th>
              </tr>
            </thead>
            <tbody class="divide-y" style="border-color: #E5E7EB;">
              <tr v-for="item in mediaItems" :key="item.id" style="background-color: #FFFFFF;">
                <td class="px-4 py-3">
                  <span 
                    class="px-2 py-1 text-xs font-medium rounded-full"
                    :style="getTypeBadgeStyle(item.type)"
                  >
                    {{ getTypeName(item.type) }}
                  </span>
                </td>
                <td class="px-4 py-3 font-medium" style="color: #3F3F41;">{{ item.formatName }}</td>
                <td class="px-4 py-3 text-center" style="color: #3F3F41;">{{ item.quantity }}</td>
                <td class="px-4 py-3 text-right" style="color: #3F3F41;">
                  {{ formatCurrency(item.customPrice || item.baseCPM) }}
                </td>
                <td class="px-4 py-3 text-right" style="color: #3F3F41;">
                  {{ formatNumber(item.baseImpressions * item.quantity) }}
                </td>
                <td class="px-4 py-3 text-right font-semibold" style="color: #3F3F41;">
                  {{ formatCurrency(((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM)) }}
                </td>
              </tr>
            </tbody>
            <tfoot class="border-t-2" style="background-color: #E5E7EB; border-color: #3F3F41;">
              <tr>
                <td colspan="4" class="px-4 py-3 text-right font-bold" style="color: #3F3F41;">TOTAL</td>
                <td class="px-4 py-3 text-right font-bold" style="color: #E2001A;">
                  {{ formatNumber(kpiResults.totalImpressions) }}
                </td>
                <td class="px-4 py-3 text-right font-bold" style="color: #E2001A;">
                  {{ formatCurrency(kpiResults.totalCost) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Bouton export -->
      <div class="flex justify-end">
        <button 
          @click="exportResults"
          class="px-6 py-3 text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2 shadow-lg"
          style="background-color: #E2001A;"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          Exporter en PDF
        </button>
      </div>
    </div>
  </div>
</template>