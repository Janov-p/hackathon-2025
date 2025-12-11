<script setup>
import { ref } from 'vue'
import UserMenu from './UserMenu.vue'

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
  <nav class="bg-white shadow-lg">
    <div class="container mx-auto px-6">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-4">
          <img 
            src="https://www.corsematin.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Flogo-cm.03feaf59.png&w=640&q=75" 
            alt="Corse-Matin" 
            class="h-10 w-auto"
          />
          <h1 class="text-xl font-bold text-cm-dark">
            Calculette Plan Média
          </h1>
        </div>
        
        <div class="flex items-center gap-4">
          <!-- Mode Toggle -->
          <div class="flex bg-cm-gray rounded-lg p-1">
            <button 
              v-for="mode in modes"
              :key="mode.id"
              @click="setMode(mode.id)"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                currentMode === mode.id 
                  ? 'bg-cm-red text-white shadow-sm' 
                  : 'text-cm-dark hover:text-cm-red hover:bg-white'
              ]"
            >
              {{ mode.label }}
            </button>
          </div>
          
          <!-- User Menu -->
          <UserMenu />
        </div>
      </div>
    </div>
  </nav>
</template>
