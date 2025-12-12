<script setup>
import { computed } from 'vue'
import { useCampaignStore } from '../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { isComplete, kpiResults, mediaPlan, formData, remise } = storeToRefs(store)

const isEnabled = computed(() => {
  return isComplete.value && kpiResults.value.audienceCumulee > 0
})

function goToExport() {
  if (!isEnabled.value) return
  
  // Sauvegarder les données dans localStorage pour le nouvel onglet
  const exportData = {
    kpiResults: kpiResults.value,
    mediaPlan: mediaPlan.value,
    formData: formData.value,
    remise: remise.value
  }
  localStorage.setItem('exportData', JSON.stringify(exportData))
  
  window.open('/hackathon/export', '_blank')
}
</script>

<template>
  <button
    @click="goToExport"
    :disabled="!isEnabled"
    :class="[
      'group flex items-center gap-2 px-6 py-3 rounded-full font-semibold shadow-lg transition-all duration-300',
      isEnabled
        ? 'bg-cm-red text-white hover:shadow-xl hover:scale-105 cursor-pointer'
        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
    ]"
  >
    <svg
      class="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </svg>
    <span>Exporter</span>
  </button>
</template>
