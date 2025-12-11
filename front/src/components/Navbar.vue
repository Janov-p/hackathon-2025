<script setup>
import { ref } from 'vue'
import UserMenu from './UserMenu.vue'

const currentMode = ref('elaboration')
const mobileMenuOpen = ref(false)

const modes = [
  { id: 'elaboration', label: 'Élaboration plan média', shortLabel: 'Plan média' },
  { id: 'kpi', label: 'Calcul KPI', shortLabel: 'KPI' }
]

function setMode(mode) {
  currentMode.value = mode
  mobileMenuOpen.value = false
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

defineExpose({ currentMode })
</script>

<template>
  <nav class="bg-white shadow-lg relative z-40">
    <div class="container mx-auto px-3 md:px-6">
      <div class="flex items-center justify-between h-12 md:h-16">
        <!-- Logo -->
        <div class="flex items-center gap-2 md:gap-4">
          <img 
            src="https://www.corsematin.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Flogo-cm.03feaf59.png&w=640&q=75" 
            alt="Corse-Matin" 
            class="h-7 md:h-10 w-auto"
          />
          <!-- Titre desktop uniquement -->
          <h1 class="text-xl font-bold text-cm-dark hidden md:block">
            Calculette Plan Média
          </h1>
        </div>

        <!-- Mobile: Mode Toggle pleine largeur -->
        <div class="flex md:hidden flex-1 mx-3">
          <div class="flex flex-1 bg-cm-gray rounded-md p-0.5">
            <button 
              v-for="mode in modes"
              :key="mode.id"
              @click="setMode(mode.id)"
              :class="[
                'flex-1 h-[32px] px-2 rounded text-xs font-medium transition-all duration-200 flex items-center justify-center',
                currentMode === mode.id 
                  ? 'bg-cm-red text-white shadow-sm' 
                  : 'text-cm-dark'
              ]"
            >
              {{ mode.shortLabel }}
            </button>
          </div>
        </div>
        
        <!-- Desktop: Mode Toggle + User Menu -->
        <div class="hidden md:flex items-center gap-4">
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

        <!-- Mobile: User Menu only -->
        <div class="flex md:hidden">
          <UserMenu />
        </div>
      </div>
    </div>
  </nav>
</template>
