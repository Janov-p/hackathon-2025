<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Données chargées depuis localStorage
const kpiResults = ref(null)
const mediaItems = ref([])
const campaignName = ref('')

// État pour l'envoi d'email
const emailTo = ref('')
const emailSending = ref(false)
const emailSent = ref(false)
const emailError = ref('')
const showEmailModal = ref(false)

const hasData = computed(() => {
  return kpiResults.value && kpiResults.value.totalCost > 0
})

// Charger les données depuis localStorage au montage
onMounted(() => {
  const savedData = localStorage.getItem('kpiExportData')
  if (savedData) {
    try {
      const data = JSON.parse(savedData)
      kpiResults.value = data.kpiResults || null
      mediaItems.value = data.mediaItems || []
      campaignName.value = data.campaignName || 'Plan média'
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
  return new Intl.NumberFormat('fr-FR').format(Math.round(value))
}

function formatPercent(num) {
  return `${num.toFixed(1)}%`
}

function getTypeName(type) {
  const names = {
    print: 'Print',
    digital: 'Digital',
    social: 'Réseaux Sociaux'
  }
  return names[type] || type
}

function goBack() {
  router.push('/')
}

function printPdf() {
  window.print()
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
        templateId: 3, // Template différent pour le mode KPI
        params: {
          nom: campaignName.value,
          audienceCumulee: formatNumber(kpiResults.value.audienceCumuleeDedupliquee),
          tauxCouverture: formatPercent(kpiResults.value.tauxCouverture),
          grp: kpiResults.value.grp.toFixed(1),
          impressions: formatNumber(kpiResults.value.totalImpressions),
          totalHT: formatCurrency(kpiResults.value.totalCost),
          cpmMoyen: formatCurrency(kpiResults.value.cpmMoyen)
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
    <!-- Header avec actions (caché à l'impression) -->
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
          <!-- Bouton Envoyer par email -->
          <button
            @click="showEmailModal = true"
            class="flex items-center justify-center gap-2 px-4 md:px-5 py-3 md:py-2.5 min-h-[48px] bg-white border-2 border-cm-red text-cm-red rounded-lg font-semibold hover:bg-cm-red hover:text-white active:scale-[0.98] transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span>Envoyer par email</span>
          </button>

          <!-- Bouton Imprimer -->
          <button
            @click="printPdf"
            class="flex items-center justify-center gap-2 px-4 md:px-5 py-3 md:py-2.5 min-h-[48px] bg-cm-red text-white rounded-lg font-semibold hover:bg-cm-dark active:scale-[0.98] transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <span>Imprimer / PDF</span>
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

    <!-- Contenu PDF -->
    <div class="max-w-5xl mx-auto p-3 md:p-6 pb-48 md:pb-6 print:p-0 print:max-w-none">
      <div v-if="hasData" class="bg-white rounded-xl md:rounded-2xl shadow-xl overflow-hidden print:rounded-none print:shadow-none">
        <!-- En-tête -->
        <div class="bg-cm-red p-4 md:p-8 text-white print:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h1 class="text-2xl md:text-3xl font-bold">Rapport KPI</h1>
              <p class="text-white/80 mt-1 text-sm md:text-base">{{ campaignName }}</p>
            </div>
            <div class="sm:text-right">
              <div class="text-xs md:text-sm text-white/70">Généré le</div>
              <div class="font-semibold text-sm md:text-base">{{ new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) }}</div>
            </div>
          </div>
        </div>

        <!-- KPI Impact & Exposition -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Impact & Exposition
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-4">
            <div class="bg-red-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Audience Cumulée</div>
              <div class="text-lg md:text-2xl font-bold text-cm-red">{{ formatNumber(kpiResults.audienceCumuleeDedupliquee) }}</div>
              <div class="text-xs md:text-sm text-gray-500">contacts uniques</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-dark">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Taux de Couverture</div>
              <div class="text-lg md:text-2xl font-bold text-cm-dark">{{ formatPercent(kpiResults.tauxCouverture) }}</div>
              <div class="text-xs md:text-sm text-gray-500">reach</div>
            </div>
            <div class="bg-red-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Fréquence Moyenne</div>
              <div class="text-lg md:text-2xl font-bold text-cm-red">{{ kpiResults.frequenceMoyenne.toFixed(1) }}×</div>
              <div class="text-xs md:text-sm text-gray-500">expositions/personne</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-dark">
              <div class="text-xs text-gray-500 uppercase tracking-wider">GRP</div>
              <div class="text-lg md:text-2xl font-bold text-cm-dark">{{ kpiResults.grp.toFixed(1) }}</div>
              <div class="text-xs md:text-sm text-gray-500">points</div>
            </div>
            <div class="bg-red-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Impressions</div>
              <div class="text-lg md:text-2xl font-bold text-cm-red">{{ formatNumber(kpiResults.totalImpressions) }}</div>
              <div class="text-xs md:text-sm text-gray-500">total</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-dark">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Vues Vidéo</div>
              <div class="text-lg md:text-2xl font-bold text-cm-dark">{{ formatNumber(kpiResults.vuesVideoTotal) }}</div>
              <div class="text-xs md:text-sm text-gray-500">estimées</div>
            </div>
          </div>
        </div>

        <!-- KPI Efficacité Financière -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Efficacité Financière
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4">
            <div class="bg-cm-red rounded-lg md:rounded-xl p-3 md:p-4 text-white">
              <div class="text-xs text-white/70 uppercase tracking-wider">Budget Total</div>
              <div class="text-xl md:text-2xl font-bold">{{ formatCurrency(kpiResults.totalCost) }}</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-dark">
              <div class="text-xs text-gray-500 uppercase tracking-wider">CPM Moyen</div>
              <div class="text-lg md:text-2xl font-bold text-cm-dark">{{ formatCurrency(kpiResults.cpmMoyen) }}</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-red">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Coût GRP</div>
              <div class="text-lg md:text-2xl font-bold text-cm-red">{{ formatCurrency(kpiResults.coutGRP) }}</div>
            </div>
            <div class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl border-l-4 border-cm-dark">
              <div class="text-xs text-gray-500 uppercase tracking-wider">Clics Estimés</div>
              <div class="text-lg md:text-2xl font-bold text-cm-dark">{{ formatNumber(kpiResults.totalClics) }}</div>
            </div>
          </div>
        </div>

        <!-- Répartition par Support -->
        <div class="p-4 md:p-8 border-b border-gray-200 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </svg>
            Répartition par Support
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-2 md:gap-4">
            <template v-for="(data, type) in kpiResults.bySupport" :key="type">
              <div v-if="data.items > 0" class="bg-gray-50 p-3 md:p-4 rounded-lg md:rounded-xl">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-bold text-cm-dark">{{ getTypeName(type) }}</span>
                  <span class="text-lg font-bold text-cm-red">{{ formatCurrency(data.cost) }}</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs mb-2">
                  <div>
                    <span class="text-gray-500">Impressions</span>
                    <p class="font-semibold text-cm-dark">{{ formatNumber(data.impressions) }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500">Part budget</span>
                    <p class="font-semibold text-cm-red">{{ formatPercent(kpiResults.repartitionBudget[type]) }}</p>
                  </div>
                </div>
                <div class="w-full rounded-full h-2 bg-gray-200">
                  <div class="h-2 rounded-full bg-cm-red" :style="{ width: `${kpiResults.repartitionBudget[type]}%` }"></div>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- Détail du Plan Média -->
        <div class="p-4 md:p-8 print:p-6">
          <h2 class="text-base md:text-lg font-bold text-cm-dark mb-3 md:mb-4 flex items-center gap-2">
            <svg class="w-4 md:w-5 h-4 md:h-5 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Détail du Plan Média
          </h2>
          
          <!-- Mobile: Cards -->
          <div class="md:hidden space-y-2">
            <div
              v-for="item in mediaItems"
              :key="item.id"
              class="bg-gray-50 rounded-lg p-3"
            >
              <div class="flex justify-between items-start mb-2">
                <div>
                  <span class="text-xs font-bold text-cm-red uppercase">{{ getTypeName(item.type) }}</span>
                  <span class="font-medium text-gray-800 block text-sm">{{ item.formatName }}</span>
                </div>
                <span class="font-bold text-cm-red">{{ formatCurrency(((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM)) }}</span>
              </div>
              <div class="flex justify-between text-xs text-gray-500">
                <span>{{ formatNumber(item.baseImpressions * item.quantity) }} impressions</span>
                <span>× {{ item.quantity }}</span>
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
                  <th class="px-4 py-3 text-center font-semibold text-gray-600">Quantité</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">CPM</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">Impressions</th>
                  <th class="px-4 py-3 text-right font-semibold text-gray-600">Coût</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="item in mediaItems" :key="item.id">
                  <td class="px-4 py-3 text-cm-red font-medium">{{ getTypeName(item.type) }}</td>
                  <td class="px-4 py-3 font-medium text-gray-800">{{ item.formatName }}</td>
                  <td class="px-4 py-3 text-center text-gray-600">{{ item.quantity }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ formatCurrency(item.customPrice || item.baseCPM) }}</td>
                  <td class="px-4 py-3 text-right text-gray-600">{{ formatNumber(item.baseImpressions * item.quantity) }}</td>
                  <td class="px-4 py-3 text-right font-semibold text-gray-800">{{ formatCurrency(((item.baseImpressions * item.quantity) / 1000) * (item.customPrice || item.baseCPM)) }}</td>
                </tr>
              </tbody>
              <tfoot class="bg-cm-red text-white">
                <tr>
                  <td colspan="4" class="px-4 py-3 text-right font-bold">TOTAL</td>
                  <td class="px-4 py-3 text-right font-bold">{{ formatNumber(kpiResults.totalImpressions) }}</td>
                  <td class="px-4 py-3 text-right font-bold text-lg">{{ formatCurrency(kpiResults.totalCost) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-100 px-4 md:px-8 py-3 md:py-4 text-center text-xs md:text-sm text-gray-500 print:bg-gray-50">
          Document généré par Calculette Plan Média - Corse-Matin
        </div>
      </div>

      <!-- État vide -->
      <div v-else class="bg-white rounded-xl md:rounded-2xl shadow-xl p-8 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Aucune donnée à afficher</h3>
        <p class="text-sm text-gray-500 mb-4">Retournez à l'application pour générer un rapport KPI</p>
        <button @click="goBack" class="px-4 py-2 bg-cm-red text-white rounded-lg font-semibold hover:bg-cm-dark transition-all">
          Retour
        </button>
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
              <p class="text-gray-500 mt-1">Le rapport KPI sera envoyé au destinataire</p>
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
