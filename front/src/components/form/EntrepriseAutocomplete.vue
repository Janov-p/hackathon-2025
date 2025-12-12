<script setup>
import { ref, watch, computed } from 'vue'
import { useEntrepriseSearch } from '../../composables/useEntrepriseSearch'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { formData } = storeToRefs(store)

const { 
  results, 
  isLoading, 
  error, 
  searchEntreprises, 
  clearSearch,
  formatSiret,
  formatSiren
} = useEntrepriseSearch()

// État local
const searchQuery = ref('')
const showDropdown = ref(false)
const showDetails = ref(false)
let debounceTimer = null

// Entreprise sélectionnée (affichage)
const hasSelectedEntreprise = computed(() => {
  return formData.value.entreprise?.siret && formData.value.entreprise?.nomComplet
})

// Recherche avec debounce
watch(searchQuery, (newQuery) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  
  if (!newQuery || newQuery.length < 2) {
    results.value = []
    showDropdown.value = false
    return
  }
  
  debounceTimer = setTimeout(async () => {
    await searchEntreprises(newQuery)
    showDropdown.value = results.value.length > 0
  }, 300)
})

// Sélectionner une entreprise
function selectEntreprise(entreprise) {
  // Mettre à jour le store avec les données de l'entreprise
  formData.value.entreprise = {
    siren: entreprise.siren || '',
    siret: entreprise.siret || '',
    nomComplet: entreprise.nomComplet || '',
    nomRaisonSociale: entreprise.nomRaisonSociale || '',
    sigle: entreprise.sigle || '',
    adresse: entreprise.adresse?.complete || '',
    codePostal: entreprise.adresse?.codePostal || '',
    commune: entreprise.adresse?.commune || '',
    departement: entreprise.adresse?.departement || '',
    activitePrincipale: entreprise.activitePrincipale || '',
    categorieEntreprise: entreprise.categorieEntreprise || '',
    natureJuridique: entreprise.natureJuridique || '',
    dateCreation: entreprise.dateCreation || '',
    dirigeants: entreprise.dirigeants || []
  }
  
  // Mettre à jour le nom du client avec la dénomination sociale de l'entreprise
  formData.value.nomClient = entreprise.nomRaisonSociale || entreprise.nomComplet || ''
  
  // Fermer le dropdown et réinitialiser la recherche
  searchQuery.value = ''
  showDropdown.value = false
  clearSearch()
}

// Effacer l'entreprise sélectionnée
function clearEntreprise() {
  formData.value.entreprise = {
    siren: '',
    siret: '',
    nomComplet: '',
    nomRaisonSociale: '',
    sigle: '',
    adresse: '',
    codePostal: '',
    commune: '',
    departement: '',
    activitePrincipale: '',
    categorieEntreprise: '',
    natureJuridique: '',
    dateCreation: '',
    dirigeants: []
  }
  showDetails.value = false
}

// Fermer le dropdown quand on clique ailleurs
function handleClickOutside() {
  showDropdown.value = false
}

// Formater la catégorie d'entreprise
function formatCategorie(cat) {
  const categories = {
    'TPE': 'Très Petite Entreprise',
    'PME': 'Petite et Moyenne Entreprise',
    'ETI': 'Entreprise de Taille Intermédiaire',
    'GE': 'Grande Entreprise'
  }
  return categories[cat] || cat || 'Non renseigné'
}
</script>

<template>
  <div class="space-y-3">
    <!-- Champ de recherche -->
    <div class="relative">
      <label class="block text-xs font-semibold text-gray-700 mb-1">
        Rechercher une entreprise (SIRET, SIREN ou nom)
      </label>
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm pr-10"
          placeholder="Ex: 552081317 ou Carrefour..."
          @focus="showDropdown = results.length > 0"
          @blur="setTimeout(() => showDropdown = false, 200)"
        />
        <!-- Icône de recherche ou loader -->
        <div class="absolute right-3 top-1/2 -translate-y-1/2">
          <svg v-if="isLoading" class="w-5 h-5 text-cm-red animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      
      <!-- Dropdown des résultats -->
      <div 
        v-if="showDropdown && results.length > 0"
        class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-y-auto"
      >
        <button
          v-for="entreprise in results"
          :key="entreprise.siret"
          @mousedown.prevent="selectEntreprise(entreprise)"
          class="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-0 transition-colors"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">
                {{ entreprise.nomComplet }}
                <span v-if="entreprise.sigle" class="text-gray-500">({{ entreprise.sigle }})</span>
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                {{ entreprise.adresse?.complete }}
              </p>
            </div>
            <div class="text-right shrink-0">
              <span class="text-xs font-mono text-cm-red">{{ formatSiret(entreprise.siret) }}</span>
              <p v-if="entreprise.categorieEntreprise" class="text-xs text-gray-400 mt-0.5">
                {{ entreprise.categorieEntreprise }}
              </p>
            </div>
          </div>
        </button>
      </div>
      
      <!-- Message d'erreur -->
      <p v-if="error" class="text-xs text-red-500 mt-1">{{ error }}</p>
      
      <!-- Message si pas de résultats -->
      <p v-if="searchQuery.length >= 2 && !isLoading && results.length === 0 && !error" class="text-xs text-gray-500 mt-1">
        Aucune entreprise trouvée
      </p>
    </div>
    
    <!-- Entreprise sélectionnée -->
    <div v-if="hasSelectedEntreprise" class="bg-green-50 border border-green-200 rounded-lg p-3">
      <div class="flex items-start justify-between gap-2">
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-green-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <p class="font-semibold text-gray-900">{{ formData.entreprise.nomComplet }}</p>
          </div>
          <div class="mt-2 space-y-1 text-sm text-gray-600">
            <p><span class="font-medium">SIRET:</span> {{ formatSiret(formData.entreprise.siret) }}</p>
            <p><span class="font-medium">Adresse:</span> {{ formData.entreprise.adresse }}</p>
          </div>
          
          <!-- Bouton voir plus de détails -->
          <button 
            @click="showDetails = !showDetails"
            class="mt-2 text-xs text-cm-red hover:underline flex items-center gap-1"
          >
            {{ showDetails ? 'Masquer' : 'Voir plus' }} de détails
            <svg 
              class="w-3 h-3 transition-transform" 
              :class="{ 'rotate-180': showDetails }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <!-- Détails supplémentaires -->
          <div v-if="showDetails" class="mt-3 pt-3 border-t border-green-200 space-y-1 text-sm text-gray-600">
            <p><span class="font-medium">SIREN:</span> {{ formatSiren(formData.entreprise.siren) }}</p>
            <p v-if="formData.entreprise.sigle"><span class="font-medium">Sigle:</span> {{ formData.entreprise.sigle }}</p>
            <p v-if="formData.entreprise.codePostal">
              <span class="font-medium">Localisation:</span> 
              {{ formData.entreprise.codePostal }} {{ formData.entreprise.commune }}
              <span v-if="formData.entreprise.departement">({{ formData.entreprise.departement }})</span>
            </p>
            <p v-if="formData.entreprise.activitePrincipale">
              <span class="font-medium">Code APE:</span> {{ formData.entreprise.activitePrincipale }}
            </p>
            <p v-if="formData.entreprise.categorieEntreprise">
              <span class="font-medium">Catégorie:</span> {{ formatCategorie(formData.entreprise.categorieEntreprise) }}
            </p>
            <p v-if="formData.entreprise.dateCreation">
              <span class="font-medium">Date de création:</span> {{ formData.entreprise.dateCreation }}
            </p>
            <div v-if="formData.entreprise.dirigeants?.length > 0" class="mt-2">
              <p class="font-medium">Dirigeants:</p>
              <ul class="ml-4 mt-1 space-y-0.5">
                <li v-for="(dirigeant, idx) in formData.entreprise.dirigeants.slice(0, 3)" :key="idx" class="text-xs">
                  {{ dirigeant.prenoms }} {{ dirigeant.nom }} 
                  <span v-if="dirigeant.qualite" class="text-gray-400">- {{ dirigeant.qualite }}</span>
                </li>
                <li v-if="formData.entreprise.dirigeants.length > 3" class="text-xs text-gray-400">
                  ... et {{ formData.entreprise.dirigeants.length - 3 }} autre(s)
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Bouton supprimer -->
        <button 
          @click="clearEntreprise"
          class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
          title="Supprimer l'entreprise"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Aide -->
    <p class="text-xs text-gray-500">
      Recherchez par nom d'entreprise, numéro SIREN (9 chiffres) ou SIRET (14 chiffres). 
      Les informations seront automatiquement remplies.
    </p>
  </div>
</template>
