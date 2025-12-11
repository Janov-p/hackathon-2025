import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEY_USER = 'cm_user_matricule'
const STORAGE_KEY_CAMPAIGNS = 'cm_saved_campaigns'

export const useAuthStore = defineStore('auth', () => {
  // État utilisateur
  const matricule = ref(localStorage.getItem(STORAGE_KEY_USER) || null)
  const isLoginModalOpen = ref(false)
  
  // Compteur pour forcer la réactivité des campagnes
  const campaignsVersion = ref(0)

  // Computed
  const isLoggedIn = computed(() => !!matricule.value)
  
  // Computed réactif pour les campagnes de l'utilisateur
  const savedCampaigns = computed(() => {
    // Dépendance sur campaignsVersion pour forcer le recalcul
    campaignsVersion.value
    const allCampaigns = JSON.parse(localStorage.getItem(STORAGE_KEY_CAMPAIGNS) || '[]')
    if (!matricule.value) return []
    return allCampaigns.filter(c => c.userMatricule === matricule.value)
  })

  // Actions
  function login(userMatricule) {
    matricule.value = userMatricule
    localStorage.setItem(STORAGE_KEY_USER, userMatricule)
  }

  function logout() {
    matricule.value = null
    localStorage.removeItem(STORAGE_KEY_USER)
  }

  function openLoginModal() {
    isLoginModalOpen.value = true
  }

  function closeLoginModal() {
    isLoginModalOpen.value = false
  }

  // Gestion des campagnes sauvegardées
  function getAllCampaigns() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY_CAMPAIGNS) || '[]')
  }

  function saveCampaign(campaignData) {
    if (!matricule.value) {
      openLoginModal()
      return { success: false, reason: 'not_logged_in' }
    }

    const allCampaigns = getAllCampaigns()
    
    const campaign = {
      id: campaignData.id || `campaign_${Date.now()}`,
      userMatricule: matricule.value,
      createdAt: campaignData.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      data: campaignData.data
    }

    // Vérifier si la campagne existe déjà (mise à jour)
    const existingIndex = allCampaigns.findIndex(c => c.id === campaign.id)
    if (existingIndex >= 0) {
      allCampaigns[existingIndex] = campaign
    } else {
      allCampaigns.push(campaign)
    }

    localStorage.setItem(STORAGE_KEY_CAMPAIGNS, JSON.stringify(allCampaigns))
    // Incrémenter pour forcer la réactivité
    campaignsVersion.value++
    return { success: true, campaign }
  }

  function deleteCampaign(campaignId) {
    if (!matricule.value) return false

    const allCampaigns = getAllCampaigns()
    const campaign = allCampaigns.find(c => c.id === campaignId)
    
    // Vérifier que la campagne appartient à l'utilisateur
    if (!campaign || campaign.userMatricule !== matricule.value) {
      return false
    }

    const filtered = allCampaigns.filter(c => c.id !== campaignId)
    localStorage.setItem(STORAGE_KEY_CAMPAIGNS, JSON.stringify(filtered))
    // Incrémenter pour forcer la réactivité
    campaignsVersion.value++
    return true
  }

  function getCampaignById(campaignId) {
    const allCampaigns = getAllCampaigns()
    return allCampaigns.find(c => c.id === campaignId)
  }

  return {
    // State
    matricule,
    isLoginModalOpen,
    
    // Computed
    isLoggedIn,
    savedCampaigns,
    
    // Actions
    login,
    logout,
    openLoginModal,
    closeLoginModal,
    
    // Campagnes
    saveCampaign,
    deleteCampaign,
    getCampaignById
  }
})
