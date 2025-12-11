<script setup>
import { computed } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { modifiedPlan, remise, budgetFinal } = storeToRefs(store)

const budgetInitial = computed({
  get: () => modifiedPlan.value?.budget?.initial || 0,
  set: (val) => {
    if (modifiedPlan.value) {
      modifiedPlan.value.budget.initial = Number(val)
      modifiedPlan.value.budget.final = store.budgetFinal
    }
  }
})

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

function updateRemiseField(field, value) {
  store.updateRemise(field, value)
}
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
      <svg class="w-4 h-4 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      Budget
    </h3>

    <!-- Budget initial -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-600">Budget initial</label>
      <div class="relative">
        <input
          type="number"
          v-model="budgetInitial"
          min="0"
          step="100"
          class="w-full px-4 py-2 pr-12 border border-gray-200 rounded-lg focus:ring-2 focus:ring-cm-red/20 focus:border-cm-red transition-colors"
        />
        <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">€</span>
      </div>
    </div>

    <!-- Section Remise -->
    <div class="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50">
      <label class="flex items-center gap-3 cursor-pointer">
        <div class="relative">
          <input
            type="checkbox"
            :checked="remise.active"
            @change="updateRemiseField('active', $event.target.checked)"
            class="sr-only peer"
          />
          <div class="w-10 h-6 bg-gray-300 rounded-full peer-checked:bg-cm-red transition-colors"></div>
          <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-4"></div>
        </div>
        <span class="text-sm font-medium text-gray-700">Appliquer une remise</span>
      </label>

      <transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 max-h-0"
        enter-to-class="opacity-100 max-h-48"
        leave-active-class="transition-all duration-150"
        leave-from-class="opacity-100 max-h-48"
        leave-to-class="opacity-0 max-h-0"
      >
        <div v-if="remise.active" class="space-y-3 overflow-hidden">
          <!-- Type de remise -->
          <div class="flex gap-2">
            <button
              @click="updateRemiseField('type', 'pourcentage')"
              :class="[
                'flex-1 px-3 py-2 text-sm font-medium rounded-lg border transition-colors',
                remise.type === 'pourcentage'
                  ? 'bg-cm-red text-white border-cm-red'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-cm-red'
              ]"
            >
              Pourcentage
            </button>
            <button
              @click="updateRemiseField('type', 'montant')"
              :class="[
                'flex-1 px-3 py-2 text-sm font-medium rounded-lg border transition-colors',
                remise.type === 'montant'
                  ? 'bg-cm-red text-white border-cm-red'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-cm-red'
              ]"
            >
              Montant fixe
            </button>
          </div>

          <!-- Valeur de la remise -->
          <div class="relative">
            <input
              type="number"
              :value="remise.valeur"
              @input="updateRemiseField('valeur', Number($event.target.value))"
              min="0"
              :max="remise.type === 'pourcentage' ? 100 : budgetInitial"
              class="w-full px-4 py-2 pr-12 border border-gray-200 rounded-lg focus:ring-2 focus:ring-cm-red/20 focus:border-cm-red transition-colors"
            />
            <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
              {{ remise.type === 'pourcentage' ? '%' : '€' }}
            </span>
          </div>

          <!-- Toggle visibilité -->
          <label class="flex items-center gap-3 cursor-pointer">
            <div class="relative">
              <input
                type="checkbox"
                :checked="remise.visible"
                @change="updateRemiseField('visible', $event.target.checked)"
                class="sr-only peer"
              />
              <div class="w-8 h-5 bg-gray-300 rounded-full peer-checked:bg-cm-dark transition-colors"></div>
              <div class="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-3"></div>
            </div>
            <span class="text-xs text-gray-600">Afficher la remise sur le document final</span>
          </label>
        </div>
      </transition>
    </div>

    <!-- Résumé budget -->
    <div class="bg-gradient-to-r from-cm-red to-cm-dark rounded-xl p-4 text-white">
      <div class="flex justify-between items-center">
        <div>
          <div class="text-xs opacity-70 uppercase tracking-wider">Budget initial</div>
          <div class="text-lg font-semibold">{{ formatCurrency(budgetInitial) }}</div>
        </div>
        <div v-if="remise.active" class="text-center">
          <div class="text-xs opacity-70 uppercase tracking-wider">Remise</div>
          <div class="text-lg font-semibold">
            -{{ remise.type === 'pourcentage' ? `${remise.valeur}%` : formatCurrency(remise.valeur) }}
          </div>
        </div>
        <div class="text-right">
          <div class="text-xs opacity-70 uppercase tracking-wider">Budget final</div>
          <div class="text-2xl font-bold">{{ formatCurrency(budgetFinal) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
