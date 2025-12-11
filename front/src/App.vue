<script setup>
import { ref } from 'vue'
import Navbar from './components/Navbar.vue'
import PanelLayout from './components/PanelLayout.vue'

const navbar = ref(null)
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-100">
    <Navbar ref="navbar" />
    <PanelLayout
    left-title="Panneau principal"
    top-right-title="Informations"
    bottom-right-title="Actions"
  >
    <template #left>
      <div class="space-y-4">
        <p class="text-gray-700">Contenu du panneau gauche.</p>
      </div>
    </template>

    <template #top-right>
      <div class="space-y-4">
        <p class="text-gray-700">Contenu du panneau haut droite.</p>
      </div>
    </template>

    <template #bottom-right>
      <div class="space-y-4">
        <p class="text-gray-700">Contenu du panneau bas droite.</p>
      </div>
    </template>
    </PanelLayout>
  </div>
</template>
