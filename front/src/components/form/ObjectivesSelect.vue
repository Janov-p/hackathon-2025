<script setup>
import { computed } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import { OBJECTIFS } from '../../data/constants'

const store = useCampaignStore()
const { formData } = storeToRefs(store)

function toggleObjectif(value) {
  const index = formData.value.objectifs.indexOf(value)
  if (index === -1) {
    formData.value.objectifs.push(value)
  } else {
    formData.value.objectifs.splice(index, 1)
  }
}

function isSelected(value) {
  return formData.value.objectifs.includes(value)
}

function selectAll() {
  const allValues = OBJECTIFS.map(o => o.value)
  if (formData.value.objectifs.length === allValues.length) {
    formData.value.objectifs = []
  } else {
    formData.value.objectifs = [...allValues]
  }
}

const isAllSelected = computed(() => formData.value.objectifs.length === OBJECTIFS.length)
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block text-xs font-semibold text-gray-700">
        Objectifs de la campagne *
      </label>
      <button
        @click="selectAll"
        :class="[
          'px-2 py-0.5 rounded text-xs font-medium transition-all duration-200 border',
          isAllSelected
            ? 'bg-cm-red text-white border-cm-red'
            : 'bg-white text-cm-red border-cm-red/30 hover:bg-cm-red/5'
        ]"
      >
        Tout
      </button>
    </div>
    <div class="grid grid-cols-2 gap-1.5">
      <button
        v-for="objectif in OBJECTIFS"
        :key="objectif.value"
        @click="toggleObjectif(objectif.value)"
        :class="[
          'flex items-center gap-2 p-2.5 md:p-2 min-h-[44px] rounded-lg border transition-all duration-200 text-left active:scale-[0.98]',
          isSelected(objectif.value)
            ? 'border-cm-red bg-cm-red/5'
            : 'border-gray-200 active:border-cm-red/50 active:bg-gray-100'
        ]"
      >
        <div :class="[
          'w-5 h-5 md:w-4 md:h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors',
          isSelected(objectif.value)
            ? 'border-cm-red bg-cm-red'
            : 'border-gray-300'
        ]">
          <svg v-if="isSelected(objectif.value)" class="w-3 h-3 md:w-2.5 md:h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </div>
        <span :class="[
          'text-xs font-medium',
          isSelected(objectif.value) ? 'text-cm-red' : 'text-gray-700'
        ]">
          {{ objectif.label }}
        </span>
      </button>
    </div>
  </div>
</template>
