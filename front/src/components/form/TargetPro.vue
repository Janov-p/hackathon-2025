<script setup>
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import { TAILLES_ENTREPRISE, SECTEURS_CIBLES, FONCTIONS } from '../../data/constants'

const store = useCampaignStore()
const { formData } = storeToRefs(store)

function toggleItem(array, value) {
  const index = array.indexOf(value)
  if (index === -1) {
    array.push(value)
  } else {
    array.splice(index, 1)
  }
}

function selectAll(array, items) {
  const allValues = items.map(i => i.value)
  if (array.length === allValues.length) {
    array.splice(0, array.length)
  } else {
    array.splice(0, array.length, ...allValues)
  }
}

function isAllSelected(array, items) {
  return array.length === items.length
}
</script>

<template>
  <div class="space-y-3">
    <!-- Taille d'entreprise -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Taille d'entreprise *</label>
      <div class="grid grid-cols-3 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.taillesEntreprise, TAILLES_ENTREPRISE)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.taillesEntreprise, TAILLES_ENTREPRISE)
              ? 'bg-cm-red text-white border-cm-red'
              : 'bg-white text-cm-red border-cm-red/30 active:bg-cm-red/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="taille in TAILLES_ENTREPRISE"
          :key="taille.value"
          @click="toggleItem(formData.taillesEntreprise, taille.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.taillesEntreprise.includes(taille.value)
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ taille.label }}
        </button>
      </div>
    </div>

    <!-- Secteurs cibles -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Secteurs ciblés *</label>
      <div class="grid grid-cols-2 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.secteursCibles, SECTEURS_CIBLES)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.secteursCibles, SECTEURS_CIBLES)
              ? 'bg-cm-red text-white border-cm-red'
              : 'bg-white text-cm-red border-cm-red/30 active:bg-cm-red/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="secteur in SECTEURS_CIBLES"
          :key="secteur.value"
          @click="toggleItem(formData.secteursCibles, secteur.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.secteursCibles.includes(secteur.value)
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ secteur.label }}
        </button>
      </div>
    </div>

    <!-- Fonctions décisionnaires -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Fonctions</label>
      <div class="grid grid-cols-2 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.fonctions, FONCTIONS)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.fonctions, FONCTIONS)
              ? 'bg-cm-red text-white border-cm-red'
              : 'bg-white text-cm-red border-cm-red/30 active:bg-cm-red/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="fonction in FONCTIONS"
          :key="fonction.value"
          @click="toggleItem(formData.fonctions, fonction.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.fonctions.includes(fonction.value)
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ fonction.label }}
        </button>
      </div>
    </div>
  </div>
</template>
