<script setup>
import { computed, ref } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { modifiedPlan } = storeToRefs(store)

const calendrier = computed(() => modifiedPlan.value?.calendrier || [])

const supportTypes = ['Print', 'Digital', 'RS', 'Event']
const actionOptions = {
  Print: ['Lancement', 'Rappel', 'Relance', 'Clôture', '-'],
  Digital: ['Diffusion continue', 'Boost', 'Retargeting', '-'],
  RS: ['Post sponsorisé', 'Story', 'Reel', 'Live', '-'],
  Event: ['Préparation', 'Événement', 'Suivi', '-']
}

function addWeek() {
  if (!modifiedPlan.value) return
  
  const newWeekNum = calendrier.value.length + 1
  modifiedPlan.value.calendrier.push({
    semaine: newWeekNum,
    actions: supportTypes.map(support => ({
      support,
      action: '-'
    }))
  })
}

function removeWeek(index) {
  if (!modifiedPlan.value || calendrier.value.length <= 1) return
  
  modifiedPlan.value.calendrier.splice(index, 1)
  // Renumber weeks
  modifiedPlan.value.calendrier.forEach((week, i) => {
    week.semaine = i + 1
  })
}

function updateAction(weekIndex, actionIndex, newAction) {
  if (!modifiedPlan.value) return
  modifiedPlan.value.calendrier[weekIndex].actions[actionIndex].action = newAction
}

function getActionForSupport(week, support) {
  const action = week.actions.find(a => a.support === support)
  return action?.action || '-'
}

function setActionForSupport(weekIndex, support, newAction) {
  if (!modifiedPlan.value) return
  
  const actionIndex = modifiedPlan.value.calendrier[weekIndex].actions.findIndex(a => a.support === support)
  if (actionIndex !== -1) {
    modifiedPlan.value.calendrier[weekIndex].actions[actionIndex].action = newAction
  } else {
    modifiedPlan.value.calendrier[weekIndex].actions.push({ support, action: newAction })
  }
}

const supportColors = {
  Print: '#6366f1',
  Digital: '#10b981',
  RS: '#ec4899',
  Event: '#f59e0b'
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
        <svg class="w-4 h-4 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Calendrier de diffusion
      </h3>
      <button
        @click="addWeek"
        class="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-cm-red border border-cm-red rounded-lg hover:bg-cm-red hover:text-white transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Semaine
      </button>
    </div>

    <!-- Calendar grid -->
    <div class="border border-gray-200 rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-3 py-2 text-left font-semibold text-gray-600 sticky left-0 bg-gray-100">Support</th>
              <th 
                v-for="week in calendrier" 
                :key="week.semaine"
                class="px-3 py-2 text-center font-semibold text-gray-600 min-w-32"
              >
                <div class="flex items-center justify-center gap-2">
                  <span>S{{ week.semaine }}</span>
                  <button
                    v-if="calendrier.length > 1"
                    @click="removeWeek(week.semaine - 1)"
                    class="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
                    title="Supprimer cette semaine"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="support in supportTypes" :key="support" class="hover:bg-gray-50">
              <td class="px-3 py-2 sticky left-0 bg-white">
                <div class="flex items-center gap-2">
                  <div 
                    class="w-3 h-3 rounded-full"
                    :style="{ backgroundColor: supportColors[support] }"
                  ></div>
                  <span class="font-medium text-gray-700">{{ support }}</span>
                </div>
              </td>
              <td 
                v-for="(week, weekIndex) in calendrier" 
                :key="week.semaine"
                class="px-2 py-2"
              >
                <select
                  :value="getActionForSupport(week, support)"
                  @change="setActionForSupport(weekIndex, support, $event.target.value)"
                  class="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg focus:ring-1 focus:ring-cm-red/20 focus:border-cm-red bg-white"
                  :style="getActionForSupport(week, support) !== '-' ? { borderColor: supportColors[support] + '80', backgroundColor: supportColors[support] + '10' } : {}"
                >
                  <option v-for="action in actionOptions[support]" :key="action" :value="action">
                    {{ action }}
                  </option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Visual timeline -->
    <div class="space-y-2">
      <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Aperçu</h4>
      <div class="flex gap-1">
        <div 
          v-for="week in calendrier" 
          :key="week.semaine"
          class="flex-1 bg-gray-100 rounded-lg p-2"
        >
          <div class="text-xs font-bold text-gray-500 mb-1 text-center">S{{ week.semaine }}</div>
          <div class="space-y-1">
            <div
              v-for="action in week.actions.filter(a => a.action !== '-')"
              :key="action.support"
              class="text-xs px-1.5 py-0.5 rounded text-white truncate"
              :style="{ backgroundColor: supportColors[action.support] }"
              :title="`${action.support}: ${action.action}`"
            >
              {{ action.action }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
