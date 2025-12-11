<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCampaignStore } from '../stores/campaign'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const campaignStore = useCampaignStore()
const { isLoggedIn, matricule, savedCampaigns } = storeToRefs(authStore)

const isCampaignsOpen = ref(false)
const saveSuccess = ref(false)

function closeCampaigns() {
  isCampaignsOpen.value = false
}

function handleSaveCampaign() {
  if (!isLoggedIn.value) {
    authStore.openLoginModal()
    return
  }
  
  const result = authStore.saveCampaign({
    data: {
      targetMode: campaignStore.targetMode,
      formData: { ...campaignStore.formData },
      kpiResults: { ...campaignStore.kpiResults },
      mediaPlan: { ...campaignStore.mediaPlan }
    }
  })
  
  if (result.success) {
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 2000)
  }
}

function loadCampaign(campaign) {
  campaignStore.targetMode = campaign.data.targetMode
  Object.assign(campaignStore.formData, campaign.data.formData)
  Object.assign(campaignStore.kpiResults, campaign.data.kpiResults)
  Object.assign(campaignStore.mediaPlan, campaign.data.mediaPlan)
  campaignStore.lastUpdate = new Date()
  closeCampaigns()
}

function deleteCampaign(campaignId, event) {
  event.stopPropagation()
  if (confirm('Supprimer cette campagne ?')) {
    authStore.deleteCampaign(campaignId)
  }
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div class="flex items-center gap-1">
    <!-- Save Button -->
    <button
      @click="handleSaveCampaign"
      class="p-1.5 rounded-lg transition-all duration-200 relative group"
      :class="saveSuccess ? 'bg-green-500 text-white' : 'hover:bg-white/20 text-white/80 hover:text-white'"
      :title="isLoggedIn ? 'Sauvegarder la campagne' : 'Connectez-vous pour sauvegarder'"
    >
      <svg v-if="!saveSuccess" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      
      <!-- Tooltip -->
      <span class="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-cm-dark text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        {{ saveSuccess ? 'Sauvegardé !' : (isLoggedIn ? 'Sauvegarder' : 'Connexion requise') }}
      </span>
    </button>

    <!-- Campaigns List Button -->
    <div class="relative">
      <button
        @click="isCampaignsOpen = !isCampaignsOpen"
        class="p-1.5 rounded-lg hover:bg-white/20 text-white/80 hover:text-white transition-all duration-200 flex items-center gap-1 group"
        title="Mes campagnes"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span v-if="savedCampaigns.length > 0" class="text-xs bg-white text-cm-red font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
          {{ savedCampaigns.length }}
        </span>
        
        <!-- Tooltip -->
        <span class="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-cm-dark text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          Mes campagnes
        </span>
      </button>

      <!-- Campaigns Dropdown -->
      <Transition name="dropdown">
        <div 
          v-if="isCampaignsOpen"
          class="absolute top-full right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
        >
          <div class="px-4 py-3 bg-cm-gray/50 border-b border-gray-100">
            <p class="font-semibold text-cm-dark text-sm">Mes campagnes</p>
            <p v-if="!isLoggedIn" class="text-xs text-cm-dark/60 mt-1">Connectez-vous pour voir vos campagnes</p>
          </div>

          <div class="max-h-64 overflow-y-auto">
            <div 
              v-if="!isLoggedIn"
              class="p-4"
            >
              <button
                @click="authStore.openLoginModal(); closeCampaigns()"
                class="w-full bg-cm-red text-white font-medium py-2 px-4 rounded-lg hover:bg-cm-red/90 transition-colors text-sm"
              >
                Se connecter
              </button>
            </div>
            
            <div 
              v-else-if="savedCampaigns.length === 0"
              class="p-4 text-sm text-cm-dark/50 text-center"
            >
              Aucune campagne sauvegardée
            </div>
            
            <div
              v-else
              v-for="campaign in savedCampaigns"
              :key="campaign.id"
              @click="loadCampaign(campaign)"
              class="flex items-center justify-between gap-2 px-4 py-3 hover:bg-cm-gray cursor-pointer group border-b border-gray-50 last:border-0"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-cm-dark truncate">
                  {{ campaign.data.formData.nom || 'Sans nom' }}
                </p>
                <p class="text-xs text-cm-dark/50">
                  {{ formatDate(campaign.updatedAt) }}
                </p>
              </div>
              <button
                @click="deleteCampaign(campaign.id, $event)"
                class="p-1.5 rounded hover:bg-red-100 text-cm-dark/40 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Backdrop -->
    <div 
      v-if="isCampaignsOpen"
      class="fixed inset-0 z-40"
      @click="closeCampaigns"
    />
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
