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
  },
  editMode: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="h-full flex gap-4 p-4 bg-cm-gray overflow-hidden">
    <!-- Panneau gauche (Config campagne) - Hidden in edit mode (v-show to preserve state) -->
    <div 
      v-show="!editMode" 
      :class="[
        'w-1/2 min-h-0 bg-white rounded-2xl shadow-lg flex flex-col overflow-hidden flex-shrink-0 transition-all duration-300',
        editMode ? 'opacity-0 -translate-x-8' : 'opacity-100 translate-x-0'
      ]"
    >
      <div class="px-6 py-3 bg-cm-red text-white flex-shrink-0 rounded-t-2xl flex items-center justify-between">
        <h2 class="text-lg font-semibold">{{ leftTitle }}</h2>
        <slot name="left-header-actions"></slot>
      </div>
      <div class="flex-1 p-4 overflow-y-auto min-h-0">
        <slot name="left">
          <p class="text-cm-dark/60">Contenu du panneau gauche</p>
        </slot>
      </div>
    </div>

    <!-- Panneau Edit Mode (Plan Média en édition) - Shown in edit mode, takes left space -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-if="editMode" 
        class="flex-1 min-h-0 bg-white rounded-2xl shadow-lg flex flex-col overflow-hidden"
      >
        <div class="px-6 py-3 bg-cm-red text-white flex-shrink-0 rounded-t-2xl flex items-center justify-between">
          <h2 class="text-lg font-semibold flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Modifier le plan média
          </h2>
        </div>
        <div class="flex-1 overflow-hidden min-h-0">
          <slot name="edit-mode">
            <p class="text-cm-dark/60 p-4">Mode édition</p>
          </slot>
        </div>
      </div>
    </Transition>

    <!-- Colonne droite avec 2 panneaux (or just KPI in edit mode) -->
    <div :class="['min-h-0 flex flex-col gap-4 relative transition-all duration-300', editMode ? 'w-80 flex-shrink-0' : 'w-1/2']">
      <!-- Panneau haut droite (Plan Média) - Hidden in edit mode -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
      >
        <div 
          v-if="!editMode" 
          class="panel-top-right h-1/2 min-h-0 bg-white rounded-2xl shadow-lg flex flex-col relative overflow-visible panel-cutout-bottom"
          style="box-shadow: 0 -10px 15px -3px rgba(0, 0, 0, 0.1), -10px 0 15px -3px rgba(0, 0, 0, 0.1), 10px 0 15px -3px rgba(0, 0, 0, 0.1);"
        >
          <div class="px-6 py-3 bg-cm-dark text-white flex-shrink-0 rounded-t-2xl">
            <h2 class="text-lg font-semibold">{{ topRightTitle }}</h2>
          </div>
          <div class="flex-1 p-4 overflow-y-auto min-h-0">
            <slot name="top-right">
              <p class="text-cm-dark/60">Contenu du panneau haut droite</p>
            </slot>
          </div>
        </div>
      </Transition>

      <!-- Panneau bas droite (KPI) - Full height in edit mode -->
      <div :class="[
        'panel-bottom-right min-h-0 bg-white rounded-2xl shadow-lg flex flex-col relative overflow-visible transition-all duration-300',
        editMode ? 'flex-1' : 'h-1/2 panel-cutout-top'
      ]" :style="editMode ? 'box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);' : 'box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), -10px 0 15px -3px rgba(0, 0, 0, 0.1), 10px 0 15px -3px rgba(0, 0, 0, 0.1);'">
        <div class="px-6 py-3 bg-cm-dark text-white flex-shrink-0 rounded-t-2xl">
          <h2 class="text-lg font-semibold">{{ bottomRightTitle }}</h2>
        </div>
        <div class="flex-1 p-4 overflow-y-auto min-h-0">
          <slot name="bottom-right">
            <p class="text-cm-dark/60">Contenu du panneau bas droite</p>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-cutout-bottom::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 40px;
  background-color: rgb(229, 231, 235);
  border-radius: 100px 100px 0 0;
  z-index: 20;
  box-shadow: inset 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.panel-cutout-top::before {
  content: '';
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 40px;
  background-color: rgb(229, 231, 235);
  border-radius: 0 0 100px 100px;
  z-index: 20;
  box-shadow: inset 0 -10px 15px -3px rgba(0, 0, 0, 0.1);
}
</style>
