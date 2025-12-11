<script setup>
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const emit = defineEmits(['confirmed'])

const store = useCampaignStore()
const { targetMode } = storeToRefs(store)

const modes = [
  { id: 'professionnels', label: 'Professionnels', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
  { id: 'particuliers', label: 'Particuliers', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' }
]

function setMode(mode) {
  store.setTargetMode(mode)
  emit('confirmed')
}
</script>

<template>
  <div class="bg-cm-gray rounded-lg p-4 border border-gray-200">
    <p class="text-center text-sm font-semibold text-cm-dark mb-3">Quel est votre type de cible ?</p>
    <div class="flex items-center justify-center gap-3">
      <button
        v-for="mode in modes"
        :key="mode.id"
        @click="setMode(mode.id)"
        :class="[
          'flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 border-2',
          targetMode === mode.id
            ? 'bg-cm-red text-white border-cm-red shadow-md'
            : 'bg-white text-gray-600 border-gray-200 hover:border-cm-red/50 hover:text-cm-red hover:bg-cm-red/5'
        ]"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="mode.icon" />
        </svg>
        {{ mode.label }}
      </button>
    </div>
  </div>
</template>
