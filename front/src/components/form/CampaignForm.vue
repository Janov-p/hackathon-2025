<script setup>
import { ref, computed, watch } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { useAuthStore } from '../../stores/auth'
import { storeToRefs } from 'pinia'
import { useMediaCalculator } from '../../composables/useMediaCalculator'
import { SECTEURS, ZONES_GEO, MICRO_ZONES } from '../../data/constants'

import TargetSwitch from './TargetSwitch.vue'
import ObjectivesSelect from './ObjectivesSelect.vue'
import TargetPro from './TargetPro.vue'
import TargetParticuliers from './TargetParticuliers.vue'
import BudgetSection from './BudgetSection.vue'
import SupportsSection from './SupportsSection.vue'
import EntrepriseAutocomplete from './EntrepriseAutocomplete.vue'

const store = useCampaignStore()
const authStore = useAuthStore()
const { formData, targetMode, formProgress, isComplete } = storeToRefs(store)
const { matricule: userMatricule, isLoggedIn } = storeToRefs(authStore)
const { isCalculating } = useMediaCalculator()

// Fonction pour remplir le matricule de l'utilisateur connecté
function fillUserMatricule() {
  if (isLoggedIn.value && userMatricule.value) {
    formData.value.matriculeCommercial = userMatricule.value
  } else {
    authStore.openLoginModal()
  }
}

// Track if target mode has been confirmed (user clicked on a choice)
const targetModeConfirmed = ref(false)

// Current visible section for progressive display (starts at 0, section 1 appears after target confirmed)
const visibleSections = ref(0)

// Collapsed sections state for mobile (section index -> collapsed state)
const collapsedSections = ref({
  1: false,
  2: false,
  3: false,
  4: false,
  5: false
})

// Toggle section collapse (mobile only)
function toggleSection(sectionNum) {
  collapsedSections.value[sectionNum] = !collapsedSections.value[sectionNum]
}

// Computed to check if section 1 is filled enough to show section 2
const section1Complete = computed(() => {
  return formData.value.nom && formData.value.secteur && formData.value.zones.length > 0
})

const section2Complete = computed(() => {
  return formData.value.objectifs.length > 0
})

const section3Complete = computed(() => {
  if (targetMode.value === 'professionnels') {
    return formData.value.taillesEntreprise.length > 0 && formData.value.secteursCibles.length > 0
  }
  return formData.value.ages.length > 0 && formData.value.csp.length > 0
})

const section4Complete = computed(() => {
  return formData.value.budget > 0
})

// When target mode is confirmed, show section 1
function onTargetConfirmed() {
  targetModeConfirmed.value = true
  if (visibleSections.value < 1) visibleSections.value = 1
}

// Watch individual sections to reveal next ones
watch(section1Complete, (val) => {
  if (val && visibleSections.value < 2) visibleSections.value = 2
})

watch(section2Complete, (val) => {
  if (val && visibleSections.value < 3) visibleSections.value = 3
})

watch(section3Complete, (val) => {
  if (val && visibleSections.value < 4) visibleSections.value = 4
})

watch(section4Complete, (val) => {
  if (val && visibleSections.value < 5) visibleSections.value = 5
})

function toggleZone(value) {
  const index = formData.value.zones.indexOf(value)
  if (index === -1) {
    formData.value.zones.push(value)
  } else {
    formData.value.zones.splice(index, 1)
  }
}

function toggleMicroZone(value) {
  const index = formData.value.microZones.indexOf(value)
  if (index === -1) {
    formData.value.microZones.push(value)
  } else {
    formData.value.microZones.splice(index, 1)
  }
}

function handleReset() {
  store.resetForm()
  targetModeConfirmed.value = false
  visibleSections.value = 0
}
</script>

<template>
  <div class="space-y-4">
    <!-- Target Switch - Always visible, triggers section reveal -->
    <TargetSwitch @confirmed="onTargetConfirmed" />

    <!-- Section 1: Informations générales -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
    <section v-if="visibleSections >= 1" class="space-y-3 md:space-y-3 bg-white md:bg-transparent rounded-lg md:rounded-none border border-gray-200 md:border-0 p-3 md:p-0">
      <!-- Header cliquable sur mobile -->
      <button 
        @click="toggleSection(1)"
        class="w-full text-left md:pointer-events-none min-h-[44px] flex items-center"
      >
        <h3 class="w-full text-base font-bold text-gray-800 flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-cm-red/10 text-cm-red flex items-center justify-center text-xs font-bold">1</span>
          <span class="flex-1">Informations générales</span>
          <!-- Chevron mobile only -->
          <svg 
            class="w-5 h-5 text-gray-400 md:hidden transition-transform duration-200"
            :class="{ 'rotate-180': !collapsedSections[1] }"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <!-- Indicateur complété -->
          <span v-if="section1Complete" class="md:hidden w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </span>
        </h3>
      </button>

      <!-- Contenu collapsible sur mobile -->
      <div 
        :class="[
          'space-y-3 overflow-hidden transition-all duration-300 md:!max-h-none md:!opacity-100',
          collapsedSections[1] ? 'max-h-0 opacity-0' : 'max-h-[2000px] opacity-100'
        ]"
      >
      <!-- Recherche entreprise (API gouv) -->
      <EntrepriseAutocomplete />

      <!-- Dénomination sociale / Nom du client -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Dénomination sociale / Nom du client *
        </label>
        <input
          type="text"
          v-model="formData.nomClient"
          class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm"
          placeholder="Ex: SARL Dupont & Fils"
        />
      </div>

      <!-- Matricule commercial -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Matricule commercial *
        </label>
        <div class="flex gap-2">
          <input
            type="text"
            v-model="formData.matriculeCommercial"
            class="flex-1 px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm"
            placeholder="Ex: CM-2024-001"
          />
          <button
            type="button"
            @click="fillUserMatricule"
            class="px-3 py-2.5 md:py-2 min-h-[44px] bg-cm-red/10 text-cm-red text-xs font-medium rounded-lg hover:bg-cm-red/20 active:bg-cm-red/30 transition-colors whitespace-nowrap"
          >
            Mon matricule
          </button>
        </div>
      </div>

      <!-- Nom de la campagne -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Nom de la campagne *
        </label>
        <input
          type="text"
          v-model="formData.nom"
          class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm"
          placeholder="Ex: Campagne été 2024"
        />
      </div>

      <!-- Secteur d'activité -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Secteur d'activité *
        </label>
        <select
          v-model="formData.secteur"
          class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all bg-white text-sm"
        >
          <option value="">Sélectionnez un secteur</option>
          <option v-for="secteur in SECTEURS" :key="secteur.value" :value="secteur.value">
            {{ secteur.label }}
          </option>
        </select>
      </div>

      <!-- Période de diffusion -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Période de diffusion *
        </label>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <input
              type="date"
              v-model="formData.periodeDebut"
              class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm"
            />
          </div>
          <div>
            <input
              type="date"
              v-model="formData.periodeFin"
              class="w-full px-3 py-2.5 md:py-2 min-h-[44px] border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm"
            />
          </div>
        </div>
      </div>

      <!-- Zone géographique -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-2">
          Zone géographique *
        </label>
        <div class="grid grid-cols-2 md:flex md:flex-wrap gap-1.5">
          <button
            v-for="zone in ZONES_GEO"
            :key="zone.value"
            @click="toggleZone(zone.value)"
            :class="[
              'px-3 py-2 md:py-1.5 min-h-[44px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
              formData.zones.includes(zone.value)
                ? 'bg-cm-red text-white'
                : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
            ]"
          >
            {{ zone.label }}
          </button>
        </div>
      </div>

      <!-- Ciblage micro-territorial -->
      <div>
        <label class="block text-xs font-semibold text-gray-700 mb-1">
          Ciblage micro-territorial (optionnel)
        </label>
        <div class="grid grid-cols-3 md:flex md:flex-wrap gap-1">
          <button
            v-for="zone in MICRO_ZONES"
            :key="zone.value"
            @click="toggleMicroZone(zone.value)"
            :class="[
              'px-2 py-1.5 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
              formData.microZones.includes(zone.value)
                ? 'bg-cm-dark text-white'
                : 'bg-gray-100 text-gray-600 active:bg-cm-dark/20'
            ]"
          >
            {{ zone.label }}
          </button>
        </div>
      </div>
      </div><!-- Fin contenu collapsible section 1 -->
    </section>
    </transition>

    <!-- Section 2: Objectifs -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <section v-if="visibleSections >= 2" class="space-y-3 bg-white md:bg-transparent rounded-lg md:rounded-none border border-gray-200 md:border-0 p-3 md:p-0">
        <!-- Header cliquable sur mobile -->
        <button 
          @click="toggleSection(2)"
          class="w-full text-left md:pointer-events-none min-h-[44px] flex items-center"
        >
          <h3 class="w-full text-base font-bold text-gray-800 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cm-red/10 text-cm-red flex items-center justify-center text-xs font-bold">2</span>
            <span class="flex-1">Objectifs</span>
            <svg 
              class="w-5 h-5 text-gray-400 md:hidden transition-transform duration-200"
              :class="{ 'rotate-180': !collapsedSections[2] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span v-if="section2Complete" class="md:hidden w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </span>
          </h3>
        </button>
        <div 
          :class="[
            'overflow-hidden transition-all duration-300 md:!max-h-none md:!opacity-100',
            collapsedSections[2] ? 'max-h-0 opacity-0' : 'max-h-[1000px] opacity-100'
          ]"
        >
          <ObjectivesSelect />
        </div>
      </section>
    </transition>

    <!-- Section 3: Cible -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <section v-if="visibleSections >= 3" class="space-y-3 bg-white md:bg-transparent rounded-lg md:rounded-none border border-gray-200 md:border-0 p-3 md:p-0">
        <!-- Header cliquable sur mobile -->
        <button 
          @click="toggleSection(3)"
          class="w-full text-left md:pointer-events-none min-h-[44px] flex items-center"
        >
          <h3 class="w-full text-base font-bold text-gray-800 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cm-red/10 text-cm-red flex items-center justify-center text-xs font-bold">3</span>
            <span class="flex-1">Cible {{ targetMode === 'professionnels' ? 'B2B' : 'B2C' }}</span>
            <svg 
              class="w-5 h-5 text-gray-400 md:hidden transition-transform duration-200"
              :class="{ 'rotate-180': !collapsedSections[3] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span v-if="section3Complete" class="md:hidden w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </span>
          </h3>
        </button>
        <div 
          :class="[
            'overflow-hidden transition-all duration-300 md:!max-h-none md:!opacity-100',
            collapsedSections[3] ? 'max-h-0 opacity-0' : 'max-h-[1500px] opacity-100'
          ]"
        >
          <TargetPro v-if="targetMode === 'professionnels'" />
          <TargetParticuliers v-else />
        </div>
      </section>
    </transition>

    <!-- Section 4: Budget -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <section v-if="visibleSections >= 4" class="space-y-3 bg-white md:bg-transparent rounded-lg md:rounded-none border border-gray-200 md:border-0 p-3 md:p-0">
        <!-- Header cliquable sur mobile -->
        <button 
          @click="toggleSection(4)"
          class="w-full text-left md:pointer-events-none min-h-[44px] flex items-center"
        >
          <h3 class="w-full text-base font-bold text-gray-800 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cm-red/10 text-cm-red flex items-center justify-center text-xs font-bold">4</span>
            <span class="flex-1">Budget</span>
            <svg 
              class="w-5 h-5 text-gray-400 md:hidden transition-transform duration-200"
              :class="{ 'rotate-180': !collapsedSections[4] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span v-if="section4Complete" class="md:hidden w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </span>
          </h3>
        </button>
        <div 
          :class="[
            'overflow-hidden transition-all duration-300 md:!max-h-none md:!opacity-100',
            collapsedSections[4] ? 'max-h-0 opacity-0' : 'max-h-[800px] opacity-100'
          ]"
        >
          <BudgetSection />
        </div>
      </section>
    </transition>

    <!-- Section 5: Supports -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <section v-if="visibleSections >= 5" class="space-y-3 bg-white md:bg-transparent rounded-lg md:rounded-none border border-gray-200 md:border-0 p-3 md:p-0">
        <!-- Header cliquable sur mobile -->
        <button 
          @click="toggleSection(5)"
          class="w-full text-left md:pointer-events-none min-h-[44px] flex items-center"
        >
          <h3 class="w-full text-base font-bold text-gray-800 flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-cm-red/10 text-cm-red flex items-center justify-center text-xs font-bold">5</span>
            <span class="flex-1">Supports</span>
            <svg 
              class="w-5 h-5 text-gray-400 md:hidden transition-transform duration-200"
              :class="{ 'rotate-180': !collapsedSections[5] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </h3>
        </button>
        <div 
          :class="[
            'overflow-hidden transition-all duration-300 md:!max-h-none md:!opacity-100',
            collapsedSections[5] ? 'max-h-0 opacity-0' : 'max-h-[1000px] opacity-100'
          ]"
        >
          <SupportsSection />
        </div>
      </section>
    </transition>

    <!-- Reset button - only show when form has been started -->
    <div v-if="visibleSections >= 1" class="pt-3 border-t border-gray-200">
      <button
        @click="handleReset"
        class="text-xs text-gray-500 hover:text-red-600 transition-colors flex items-center gap-1"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Réinitialiser
      </button>
    </div>

    <!-- Calculating indicator -->
    <transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isCalculating" class="fixed bottom-4 left-1/2 -translate-x-1/2 md:left-auto md:translate-x-0 md:right-4 bg-cm-red text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 z-50">
        <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-sm">Calcul en cours...</span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.5s ease-out;
}
</style>
