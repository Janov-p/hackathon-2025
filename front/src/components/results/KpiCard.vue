<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'indigo'
  },
  tooltip: {
    type: String,
    default: ''
  },
  isUpdating: {
    type: Boolean,
    default: false
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return new Intl.NumberFormat('fr-FR').format(props.value)
  }
  return props.value
})

const colorClasses = computed(() => {
  const colors = {
    red: {
      bg: 'bg-red-50',
      icon: 'bg-cm-red/10 text-cm-red',
      text: 'text-cm-red',
      ring: 'ring-cm-red'
    },
    dark: {
      bg: 'bg-gray-100',
      icon: 'bg-cm-dark/10 text-cm-dark',
      text: 'text-cm-dark',
      ring: 'ring-cm-dark'
    },
    indigo: {
      bg: 'bg-gray-50',
      icon: 'bg-cm-dark/10 text-cm-dark',
      text: 'text-cm-dark',
      ring: 'ring-cm-dark'
    },
    emerald: {
      bg: 'bg-gray-50',
      icon: 'bg-cm-red/10 text-cm-red',
      text: 'text-cm-red',
      ring: 'ring-cm-red'
    },
    amber: {
      bg: 'bg-gray-100',
      icon: 'bg-cm-dark/10 text-cm-dark',
      text: 'text-cm-dark',
      ring: 'ring-cm-dark'
    },
    pink: {
      bg: 'bg-red-50',
      icon: 'bg-cm-red/10 text-cm-red',
      text: 'text-cm-red',
      ring: 'ring-cm-red'
    }
  }
  return colors[props.color] || colors.dark
})
</script>

<template>
  <div
    :class="[
      'relative p-4 rounded-xl transition-all duration-300',
      colorClasses.bg,
      isUpdating ? 'ring-2 animate-pulse' : '',
      isUpdating ? colorClasses.ring : ''
    ]"
    :title="tooltip"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
          {{ title }}
        </p>
        <p :class="['text-2xl font-bold', colorClasses.text]">
          {{ formattedValue }}
          <span v-if="unit" class="text-sm font-normal text-gray-500">{{ unit }}</span>
        </p>
      </div>
      <div v-if="icon" :class="['w-10 h-10 rounded-lg flex items-center justify-center', colorClasses.icon]">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon" />
        </svg>
      </div>
    </div>
    
    <!-- Tooltip indicator -->
    <div v-if="tooltip" class="absolute top-2 right-2">
      <svg class="w-4 h-4 text-gray-400 cursor-help" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
  </div>
</template>
