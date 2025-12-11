import { ref, watch } from 'vue'
import { useCampaignStore } from '../stores/campaign'
import { storeToRefs } from 'pinia'

export function useMediaCalculator() {
  const store = useCampaignStore()
  const { formData, isComplete } = storeToRefs(store)
  
  let debounceTimer = null
  const isCalculating = ref(false)

  // Debounced calculation trigger
  function triggerCalculation() {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    
    debounceTimer = setTimeout(async () => {
      if (isComplete.value) {
        isCalculating.value = true
        await store.generateResults()
        isCalculating.value = false
      }
    }, 500)
  }

  // Watch for form changes
  watch(
    formData,
    () => {
      triggerCalculation()
    },
    { deep: true }
  )

  // Watch for completion status
  watch(
    isComplete,
    (newVal) => {
      if (newVal) {
        triggerCalculation()
      }
    }
  )

  return {
    isCalculating,
    triggerCalculation
  }
}

// Utility functions for KPI calculations (placeholder logic)
export function calculateAudience(zones, budget) {
  const baseAudience = 185000
  const zoneFactor = zones.includes('corse-entiere') ? 1 : zones.length * 0.4
  const budgetFactor = Math.min(budget / 50000, 2)
  return Math.round(baseAudience * zoneFactor * budgetFactor)
}

export function calculateGRP(audience, frequency, population = 330000) {
  return Math.round((audience / population) * frequency * 100 * 10) / 10
}

export function calculateCPM(budget, impressions) {
  if (impressions === 0) return 0
  return Math.round((budget / impressions) * 1000 * 100) / 100
}

export function calculateCTR(clicks, impressions) {
  if (impressions === 0) return 0
  return Math.round((clicks / impressions) * 100 * 100) / 100
}

export function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

export function formatNumber(value) {
  return new Intl.NumberFormat('fr-FR').format(value)
}

export function formatPercent(value) {
  return `${value}%`
}
