<script setup>
import { ref } from 'vue'

const currentMode = ref('elaboration')

const modes = [
  { id: 'elaboration', label: 'Élaboration plan média' },
  { id: 'kpi', label: 'Calcul KPI' }
]

function setMode(mode) {
  currentMode.value = mode
}

defineExpose({ currentMode })
</script>

<template>
  <nav class="bg-gradient-to-r from-indigo-600 to-indigo-700 shadow-lg">
    <div class="container mx-auto px-6">
      <div class="flex items-center justify-between h-16">
        <h1 class="text-xl font-bold text-white">
          Calculette Plan Média
        </h1>
        <div class="flex bg-indigo-800/40 rounded-lg p-1">
          <button 
            v-for="mode in modes"
            :key="mode.id"
            @click="setMode(mode.id)"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
              currentMode === mode.id 
                ? 'bg-white text-indigo-700 shadow-sm' 
                : 'text-indigo-100 hover:text-white hover:bg-indigo-600/50'
            ]"
          >
            {{ mode.label }}
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>
