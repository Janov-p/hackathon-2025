<script setup>
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import { TRANCHES_AGE, SEXES, CSP, CENTRES_INTERET } from '../../data/constants'

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
    <!-- Tranches d'âge -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Tranches d'âge *</label>
      <div class="grid grid-cols-3 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.ages, TRANCHES_AGE)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.ages, TRANCHES_AGE)
              ? 'bg-cm-red text-white border-cm-red'
              : 'bg-white text-cm-red border-cm-red/30 active:bg-cm-red/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="age in TRANCHES_AGE"
          :key="age.value"
          @click="toggleItem(formData.ages, age.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.ages.includes(age.value)
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ age.label }}
        </button>
      </div>
    </div>

    <!-- Sexe -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Sexe</label>
      <div class="grid grid-cols-3 gap-1">
        <button
          v-for="sexe in SEXES"
          :key="sexe.value"
          @click="formData.sexe = sexe.value"
          :class="[
            'px-3 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.sexe === sexe.value
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ sexe.label }}
        </button>
      </div>
    </div>

    <!-- CSP -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">CSP *</label>
      <div class="grid grid-cols-2 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.csp, CSP)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.csp, CSP)
              ? 'bg-cm-red text-white border-cm-red'
              : 'bg-white text-cm-red border-cm-red/30 active:bg-cm-red/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="csp in CSP"
          :key="csp.value"
          @click="toggleItem(formData.csp, csp.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.csp.includes(csp.value)
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-red/20'
          ]"
        >
          {{ csp.label }}
        </button>
      </div>
    </div>

    <!-- Centres d'intérêt -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Centres d'intérêt</label>
      <div class="grid grid-cols-2 md:flex md:flex-wrap gap-1">
        <button
          @click="selectAll(formData.centresInteret, CENTRES_INTERET)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 border active:scale-95',
            isAllSelected(formData.centresInteret, CENTRES_INTERET)
              ? 'bg-cm-dark text-white border-cm-dark'
              : 'bg-white text-cm-dark border-cm-dark/30 active:bg-cm-dark/10'
          ]"
        >
          Tout
        </button>
        <button
          v-for="interet in CENTRES_INTERET"
          :key="interet.value"
          @click="toggleItem(formData.centresInteret, interet.value)"
          :class="[
            'px-2.5 py-2 md:py-1 min-h-[40px] md:min-h-0 rounded-full text-xs font-medium transition-all duration-200 active:scale-95',
            formData.centresInteret.includes(interet.value)
              ? 'bg-cm-dark text-white'
              : 'bg-gray-100 text-gray-700 active:bg-cm-dark/20'
          ]"
        >
          {{ interet.label }}
        </button>
      </div>
    </div>
  </div>
</template>
