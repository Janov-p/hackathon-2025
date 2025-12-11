<script setup>
import { computed } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import { REPARTITION_OPTIONS } from '../../data/constants'

const store = useCampaignStore()
const { formData } = storeToRefs(store)

const formattedBudget = computed(() => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(formData.value.budget)
})

const repartitionTotal = computed(() => {
  return Object.values(formData.value.repartition).reduce((a, b) => a + b, 0)
})

function updateSlider(key, event) {
  store.updateRepartition(key, parseInt(event.target.value))
}

const sliderConfig = [
  { key: 'print', label: 'Print', color: 'red' },
  { key: 'digital', label: 'Digital', color: 'dark' },
  { key: 'reseaux', label: 'Réseaux sociaux', color: 'red' },
  { key: 'event', label: 'Event', color: 'dark' }
]
</script>

<template>
  <div class="space-y-3">
    <!-- Budget global -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1">Budget (€ HT) *</label>
      <div class="relative">
        <input
          type="number"
          v-model.number="formData.budget"
          min="1000"
          step="500"
          class="w-full px-3 py-2 pr-14 border border-gray-300 rounded-lg focus:border-cm-red focus:ring-1 focus:ring-cm-red/20 transition-all text-sm font-semibold"
          placeholder="10000"
        />
        <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs">€ HT</span>
      </div>
      <div class="mt-1.5 flex items-center gap-1">
        <button
          v-for="preset in [5000, 10000, 25000, 50000]"
          :key="preset"
          @click="formData.budget = preset"
          :class="[
            'px-2 py-0.5 rounded-full text-xs font-medium transition-all',
            formData.budget === preset
              ? 'bg-cm-red text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-cm-red/10'
          ]"
        >
          {{ (preset/1000) }}k€
        </button>
      </div>
    </div>

    <!-- Mode de répartition -->
    <div>
      <label class="block text-xs font-semibold text-gray-700 mb-1.5">Répartition</label>
      <div class="flex gap-1">
        <button
          v-for="option in REPARTITION_OPTIONS"
          :key="option.value"
          @click="formData.repartitionMode = option.value"
          :class="[
            'flex-1 px-2 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 border',
            formData.repartitionMode === option.value
              ? 'border-cm-red bg-cm-red/5 text-cm-red'
              : 'border-gray-200 bg-white text-gray-600 hover:border-cm-red/30'
          ]"
        >
          {{ option.label }}
        </button>
      </div>
    </div>

    <!-- Sliders de répartition -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-80"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 max-h-80"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="formData.repartitionMode === 'personnalisee'" class="space-y-2 overflow-hidden">
        <div
          v-for="slider in sliderConfig"
          :key="slider.key"
          class="space-y-1"
        >
          <div class="flex justify-between items-center">
            <span class="text-xs font-medium text-gray-700">{{ slider.label }}</span>
            <span class="text-xs font-bold text-gray-600">{{ formData.repartition[slider.key] }}%</span>
          </div>
          <input
            type="range"
            :value="formData.repartition[slider.key]"
            @input="updateSlider(slider.key, $event)"
            min="0"
            max="100"
            class="w-full h-1.5 rounded-lg appearance-none cursor-pointer bg-gray-200"
            :style="{
              background: `linear-gradient(to right, var(--tw-gradient-stops))`,
              '--tw-gradient-from': slider.color === 'red' ? '#E2001A' : '#232324',
              '--tw-gradient-to': '#e5e7eb',
              '--tw-gradient-stops': `var(--tw-gradient-from) ${formData.repartition[slider.key]}%, var(--tw-gradient-to) ${formData.repartition[slider.key]}%`
            }"
          />
        </div>

        <!-- Total indicator -->
        <div :class="[
          'flex justify-between items-center p-2 rounded-lg text-xs',
          repartitionTotal === 100 ? 'bg-green-50' : 'bg-red-50'
        ]">
          <span class="font-medium">Total</span>
          <span :class="['font-bold', repartitionTotal === 100 ? 'text-green-600' : 'text-red-600']">
            {{ repartitionTotal }}%
          </span>
        </div>
      </div>
    </transition>
  </div>
</template>
