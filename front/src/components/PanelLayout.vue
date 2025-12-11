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
  <div class="h-[calc(100%-56px)] md:h-full flex flex-col md:flex-row gap-3 md:gap-6 p-3 md:p-6 bg-cm-gray overflow-auto md:overflow-hidden">
    <!-- Panneau gauche (Config campagne) - Hidden in edit mode (v-show to preserve state) -->
    <div 
      v-show="!editMode" 
      :class="[
        'w-full md:w-1/2 min-h-0 bg-white rounded-xl md:rounded-2xl shadow-lg flex flex-col overflow-hidden flex-shrink-0 transition-all duration-300',
        editMode ? 'opacity-0 -translate-x-8' : 'opacity-100 translate-x-0'
      ]"
    >
      <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-red text-white flex-shrink-0 rounded-t-xl md:rounded-t-2xl flex items-center justify-between">
        <h2 class="text-base md:text-lg font-semibold">{{ leftTitle }}</h2>
        <slot name="left-header-actions"></slot>
      </div>
      <div class="flex-1 p-3 md:p-4 overflow-y-auto min-h-0">
        <slot name="left">
          <p class="text-cm-dark/60">Contenu du panneau gauche</p>
        </slot>
      </div>
    </div>

    <!-- Panneau Edit Mode (Plan Média en édition) - Shown in edit mode, fullscreen on mobile -->
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
        class="fixed inset-0 z-50 md:relative md:inset-auto md:z-auto flex-1 min-h-0 bg-white md:rounded-2xl shadow-lg flex flex-col overflow-hidden"
      >
        <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-red text-white flex-shrink-0 md:rounded-t-2xl flex items-center justify-between">
          <h2 class="text-base md:text-lg font-semibold flex items-center gap-2">
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
    <div :class="['w-full md:w-1/2 min-h-0 flex flex-col gap-2 md:gap-4 relative transition-all duration-300', editMode ? 'hidden md:flex md:w-80 md:flex-shrink-0' : '']">
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
          class="panel-top-right min-h-[300px] md:h-1/2 md:min-h-0 bg-white rounded-xl md:rounded-2xl shadow-lg flex flex-col relative overflow-visible md:panel-cutout-bottom"
          style="box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
        >
          <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-dark text-white flex-shrink-0 rounded-t-xl md:rounded-t-2xl">
            <h2 class="text-base md:text-lg font-semibold">{{ topRightTitle }}</h2>
          </div>
          <div class="flex-1 p-3 md:p-4 overflow-y-auto min-h-0">
            <slot name="top-right">
              <p class="text-cm-dark/60">Contenu du panneau haut droite</p>
            </slot>
          </div>
        </div>
      </Transition>

      <!-- Panneau bas droite (KPI) - Full height in edit mode -->
      <div :class="[
        'panel-bottom-right min-h-[300px] md:min-h-0 bg-white rounded-xl md:rounded-2xl shadow-lg flex flex-col relative overflow-visible transition-all duration-300',
        editMode ? 'flex-1' : 'md:h-1/2 md:panel-cutout-top'
      ]" style="box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div class="px-4 md:px-6 py-2 md:py-3 bg-cm-dark text-white flex-shrink-0 rounded-t-xl md:rounded-t-2xl">
          <h2 class="text-base md:text-lg font-semibold">{{ bottomRightTitle }}</h2>
        </div>
        <div class="flex-1 p-3 md:p-4 overflow-y-auto min-h-0">
          <slot name="bottom-right">
            <p class="text-cm-dark/60">Contenu du panneau bas droite</p>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Cutout decorations only on desktop (md and up) */
@media (min-width: 768px) {
  .md\:panel-cutout-bottom::after {
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

  .md\:panel-cutout-top::before {
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
}
</style>
