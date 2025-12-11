<script setup>
import { computed, ref } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { modifiedPlan, budgetFinal } = storeToRefs(store)

const repartition = computed(() => modifiedPlan.value?.repartition || { print: 25, digital: 35, reseaux: 30, event: 10 })

// État des verrous pour chaque catégorie
const locked = ref({
  print: false,
  digital: false,
  reseaux: false,
  event: false
})

function toggleLock(key) {
  locked.value[key] = !locked.value[key]
}

const categories = [
  { key: 'print', label: 'Print', color: '#6366f1', icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z' },
  { key: 'digital', label: 'Digital', color: '#10b981', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { key: 'reseaux', label: 'Réseaux sociaux', color: '#ec4899', icon: 'M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z' },
  { key: 'event', label: 'Event', color: '#f59e0b', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' }
]

const total = computed(() => {
  return Object.values(repartition.value).reduce((a, b) => a + b, 0)
})

function updateRepartition(key, value) {
  if (!modifiedPlan.value) return
  if (locked.value[key]) return // Ne pas modifier si verrouillé
  
  const newValue = Math.max(0, Math.min(100, Number(value)))
  const oldValue = repartition.value[key]
  const diff = newValue - oldValue
  
  // Ne modifier que les catégories non verrouillées
  const otherKeys = Object.keys(repartition.value).filter(k => k !== key && !locked.value[k])
  const otherTotal = otherKeys.reduce((sum, k) => sum + repartition.value[k], 0)
  
  if (otherTotal > 0 && diff !== 0) {
    otherKeys.forEach(k => {
      const proportion = repartition.value[k] / otherTotal
      modifiedPlan.value.repartition[k] = Math.max(0, Math.round(repartition.value[k] - diff * proportion))
    })
  }
  
  modifiedPlan.value.repartition[key] = newValue
  
  // Normalize to ensure total is 100 (only adjust unlocked keys)
  const newTotal = Object.values(modifiedPlan.value.repartition).reduce((a, b) => a + b, 0)
  if (newTotal !== 100 && otherKeys.length > 0) {
    const adjustment = 100 - newTotal
    const maxKey = otherKeys.reduce((a, b) => 
      modifiedPlan.value.repartition[a] > modifiedPlan.value.repartition[b] ? a : b
    )
    modifiedPlan.value.repartition[maxKey] += adjustment
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

function getBudgetForCategory(key) {
  return Math.round(budgetFinal.value * repartition.value[key] / 100)
}
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
      <svg class="w-4 h-4 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
      </svg>
      Répartition budgétaire
    </h3>

    <!-- Total indicator -->
    <div 
      :class="[
        'text-center py-2 px-4 rounded-lg text-sm font-medium transition-colors',
        total === 100 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
      ]"
    >
      Total : {{ total }}% {{ total !== 100 ? '(doit être 100%)' : '✓' }}
    </div>

    <!-- Sliders -->
    <div class="space-y-4">
      <div v-for="cat in categories" :key="cat.key" class="space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <!-- Bouton verrou -->
            <button
              @click="toggleLock(cat.key)"
              :class="[
                'w-6 h-6 rounded flex items-center justify-center transition-colors',
                locked[cat.key] 
                  ? 'bg-cm-red/10 text-cm-red' 
                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
              ]"
              :title="locked[cat.key] ? 'Déverrouiller' : 'Verrouiller'"
            >
              <svg v-if="locked[cat.key]" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
              </svg>
            </button>
            <div 
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :style="{ backgroundColor: cat.color + '20' }"
            >
              <svg class="w-4 h-4" :style="{ color: cat.color }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="cat.icon" />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-700">{{ cat.label }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">{{ formatCurrency(getBudgetForCategory(cat.key)) }}</span>
            <div class="relative w-16">
              <input
                type="number"
                :value="repartition[cat.key]"
                @input="updateRepartition(cat.key, $event.target.value)"
                min="0"
                max="100"
                :disabled="locked[cat.key]"
                :class="[
                  'w-full px-2 py-1 text-sm text-right border rounded transition-colors',
                  locked[cat.key] 
                    ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed' 
                    : 'border-gray-200 focus:ring-1 focus:ring-cm-red/20 focus:border-cm-red'
                ]"
              />
              <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400">%</span>
            </div>
          </div>
        </div>
        
        <!-- Slider avec poignée de drag - Plus grand sur mobile -->
        <div class="relative h-6 md:h-3 group">
          <div class="absolute inset-y-2 md:inset-y-0.5 left-0 right-0 bg-gray-200 rounded-full"></div>
          <div 
            class="absolute top-2 md:top-0.5 left-0 h-2 rounded-full transition-all duration-200"
            :style="{ width: repartition[cat.key] + '%', backgroundColor: locked[cat.key] ? '#9ca3af' : cat.color }"
          ></div>
          <!-- Poignée de drag avec points - Plus grande sur mobile -->
          <div 
            class="absolute top-1/2 -translate-y-1/2 w-7 h-7 md:w-5 md:h-5 rounded-full bg-white shadow-md border-2 flex items-center justify-center transition-all"
            :style="{ 
              left: `calc(${repartition[cat.key]}% - 14px)`,
              borderColor: locked[cat.key] ? '#9ca3af' : cat.color
            }"
            :class="locked[cat.key] ? 'cursor-not-allowed' : 'cursor-grab group-active:cursor-grabbing'"
          >
            <!-- Points de grip -->
            <div class="flex gap-0.5" v-if="!locked[cat.key]">
              <div class="w-0.5 h-3 md:h-2 rounded-full" :style="{ backgroundColor: cat.color }"></div>
              <div class="w-0.5 h-3 md:h-2 rounded-full" :style="{ backgroundColor: cat.color }"></div>
            </div>
            <!-- Icône verrou si verrouillé -->
            <svg v-else class="w-3 h-3 md:w-2.5 md:h-2.5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input
            type="range"
            :value="repartition[cat.key]"
            @input="updateRepartition(cat.key, $event.target.value)"
            min="0"
            max="100"
            :disabled="locked[cat.key]"
            :class="[
              'absolute inset-0 w-full h-full opacity-0',
              locked[cat.key] ? 'cursor-not-allowed' : 'cursor-grab'
            ]"
          />
        </div>
      </div>
    </div>

    <!-- Visual summary -->
    <div class="flex h-4 rounded-full overflow-hidden">
      <div 
        v-for="cat in categories" 
        :key="cat.key"
        class="transition-all duration-300"
        :style="{ width: repartition[cat.key] + '%', backgroundColor: cat.color }"
        :title="`${cat.label}: ${repartition[cat.key]}%`"
      ></div>
    </div>
  </div>
</template>
