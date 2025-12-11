<script setup>
defineProps({
  leftTitle: {
    type: String,
    default: 'Panneau gauche'
  },
  topRightTitle: {
    type: String,
    default: 'Panneau haut'
  },
  bottomRightTitle: {
    type: String,
    default: 'Panneau bas'
  }
})
</script>

<template>
  <div class="flex-1 flex gap-4 p-4 bg-gray-100 overflow-hidden">
    <!-- Panneau gauche -->
    <div class="w-1/2 bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col">
      <div class="px-6 py-4 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white">
        <h2 class="text-lg font-semibold">{{ leftTitle }}</h2>
      </div>
      <div class="flex-1 p-6 overflow-auto">
        <slot name="left">
          <p class="text-gray-500">Contenu du panneau gauche</p>
        </slot>
      </div>
    </div>

    <!-- Colonne droite avec 2 panneaux -->
    <div class="w-1/2 flex flex-col gap-4">
      <!-- Panneau haut droite -->
      <div class="flex-1 bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col">
        <div class="px-6 py-4 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white">
          <h2 class="text-lg font-semibold">{{ topRightTitle }}</h2>
        </div>
        <div class="flex-1 p-6 overflow-auto">
          <slot name="top-right">
            <p class="text-gray-500">Contenu du panneau haut droite</p>
          </slot>
        </div>
      </div>

      <!-- Panneau bas droite -->
      <div class="flex-1 bg-white rounded-2xl shadow-lg overflow-hidden flex flex-col">
        <div class="px-6 py-4 bg-gradient-to-r from-amber-500 to-amber-600 text-white">
          <h2 class="text-lg font-semibold">{{ bottomRightTitle }}</h2>
        </div>
        <div class="flex-1 p-6 overflow-auto">
          <slot name="bottom-right">
            <p class="text-gray-500">Contenu du panneau bas droite</p>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>
