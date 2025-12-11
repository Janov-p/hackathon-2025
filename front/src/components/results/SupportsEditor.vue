<script setup>
import { computed } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { modifiedPlan } = storeToRefs(store)

const supportCategories = [
  {
    key: 'print',
    label: 'Print',
    color: '#6366f1',
    icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
    options: [
      { id: 'quotidien', label: 'Quotidien Corse-Matin' },
      { id: 'magazine', label: 'Magazine Diverto' },
      { id: 'supplement', label: 'Suppléments thématiques' }
    ]
  },
  {
    key: 'digital',
    label: 'Digital',
    color: '#10b981',
    icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    options: [
      { id: 'site-web', label: 'Site CorseMatin.com' },
      { id: 'newsletter', label: 'Newsletter' },
      { id: 'app-mobile', label: 'Application mobile' }
    ]
  },
  {
    key: 'reseauxSociaux',
    label: 'Réseaux sociaux',
    color: '#ec4899',
    icon: 'M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z',
    options: [
      { id: 'facebook', label: 'Facebook' },
      { id: 'instagram', label: 'Instagram' },
      { id: 'linkedin', label: 'LinkedIn' },
      { id: 'tiktok', label: 'TikTok' }
    ]
  },
  {
    key: 'events',
    label: 'Events',
    color: '#f59e0b',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    options: [
      { id: 'club-impresa', label: 'Club Impresa' },
      { id: 'salon', label: 'Salons professionnels' },
      { id: 'conference', label: 'Conférences' }
    ]
  }
]

function isSelected(category, optionId) {
  if (!modifiedPlan.value) return false
  return modifiedPlan.value.supports[category]?.includes(optionId) || false
}

function toggleSupport(category, optionId) {
  if (!modifiedPlan.value) return
  
  const supports = modifiedPlan.value.supports[category] || []
  const index = supports.indexOf(optionId)
  
  if (index === -1) {
    modifiedPlan.value.supports[category] = [...supports, optionId]
  } else {
    modifiedPlan.value.supports[category] = supports.filter(id => id !== optionId)
  }
}

function getSelectedCount(category) {
  if (!modifiedPlan.value) return 0
  return modifiedPlan.value.supports[category]?.length || 0
}
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
      <svg class="w-4 h-4 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Supports sélectionnés
    </h3>

    <div class="space-y-4">
      <div v-for="cat in supportCategories" :key="cat.key" class="border border-gray-200 rounded-lg overflow-hidden">
        <!-- Category header -->
        <div 
          class="flex items-center justify-between px-4 py-3"
          :style="{ backgroundColor: cat.color + '10' }"
        >
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5" :style="{ color: cat.color }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="cat.icon" />
            </svg>
            <span class="font-medium text-gray-700">{{ cat.label }}</span>
          </div>
          <span 
            class="px-2 py-0.5 text-xs font-bold rounded-full"
            :style="{ backgroundColor: cat.color + '20', color: cat.color }"
          >
            {{ getSelectedCount(cat.key) }} / {{ cat.options.length }}
          </span>
        </div>

        <!-- Options -->
        <div class="p-3 space-y-2 bg-white">
          <label 
            v-for="option in cat.options" 
            :key="option.id"
            class="flex items-center gap-3 p-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <div class="relative">
              <input
                type="checkbox"
                :checked="isSelected(cat.key, option.id)"
                @change="toggleSupport(cat.key, option.id)"
                class="sr-only peer"
              />
              <div 
                class="w-5 h-5 border-2 rounded transition-colors peer-checked:border-transparent"
                :class="isSelected(cat.key, option.id) ? '' : 'border-gray-300'"
                :style="isSelected(cat.key, option.id) ? { backgroundColor: cat.color } : {}"
              >
                <svg 
                  v-if="isSelected(cat.key, option.id)"
                  class="w-full h-full text-white p-0.5" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <span class="text-sm text-gray-700">{{ option.label }}</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>
