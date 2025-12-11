<script setup>
import { ref } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'
import { SUPPORTS_PRINT, SUPPORTS_DIGITAL, RESEAUX_SOCIAUX, EVENTS } from '../../data/constants'

const store = useCampaignStore()
const { formData } = storeToRefs(store)

const expandedSections = ref({
  print: false,
  digital: false,
  reseaux: false,
  event: false
})

function toggleSection(section) {
  expandedSections.value[section] = !expandedSections.value[section]
}

function toggleItem(array, value) {
  const index = array.indexOf(value)
  if (index === -1) {
    array.push(value)
  } else {
    array.splice(index, 1)
  }
}

const sections = [
  {
    key: 'print',
    label: 'Print',
    icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
    color: 'indigo',
    data: SUPPORTS_PRINT,
    formKey: 'supportsPrint'
  },
  {
    key: 'digital',
    label: 'Digital',
    icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    color: 'emerald',
    data: SUPPORTS_DIGITAL,
    formKey: 'supportsDigital'
  },
  {
    key: 'reseaux',
    label: 'Réseaux sociaux',
    icon: 'M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z',
    color: 'pink',
    data: RESEAUX_SOCIAUX,
    formKey: 'reseauxSociaux'
  },
  {
    key: 'event',
    label: 'Event',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    color: 'amber',
    data: EVENTS,
    formKey: 'events'
  }
]

function getSelectedCount(section) {
  return formData.value[section.formKey].length
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-xs font-semibold text-gray-700">Supports (optionnel)</label>

    <div class="space-y-1">
      <div
        v-for="section in sections"
        :key="section.key"
        class="border border-gray-200 rounded-lg overflow-hidden"
      >
        <!-- Header -->
        <button
          @click="toggleSection(section.key)"
          class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="section.icon" />
            </svg>
            <span class="text-xs font-medium text-gray-700">{{ section.label }}</span>
            <span
              v-if="getSelectedCount(section) > 0"
              class="px-1.5 py-0.5 rounded-full text-xs font-bold bg-cm-red text-white"
            >
              {{ getSelectedCount(section) }}
            </span>
          </div>
          <svg
            :class="['w-4 h-4 text-gray-400 transition-transform', expandedSections[section.key] ? 'rotate-180' : '']"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Content -->
        <transition
          enter-active-class="transition-all duration-150 ease-out"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-60"
          leave-active-class="transition-all duration-100 ease-in"
          leave-from-class="opacity-100 max-h-60"
          leave-to-class="opacity-0 max-h-0"
        >
          <div v-if="expandedSections[section.key]" class="px-3 py-2 space-y-2 overflow-hidden border-t border-gray-100">
            <!-- Print section with subcategories -->
            <template v-if="section.key === 'print'">
              <div v-for="(items, category) in section.data" :key="category" class="space-y-1">
                <span class="text-xs text-gray-500">{{ category === 'quotidien' ? 'Quotidien' : category === 'supplements' ? 'Suppléments' : 'Magazines' }}</span>
                <div class="flex flex-wrap gap-1">
                  <button
                    v-for="item in items"
                    :key="item.value"
                    @click="toggleItem(formData[section.formKey], item.value)"
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium transition-all border',
                      formData[section.formKey].includes(item.value)
                        ? 'border-cm-red bg-cm-red/5 text-cm-red'
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                    ]"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>
            </template>

            <!-- Digital section with subcategories -->
            <template v-else-if="section.key === 'digital'">
              <div v-for="(items, category) in section.data" :key="category" class="space-y-1">
                <span class="text-xs text-gray-500">{{ category === 'sites' ? 'Sites' : 'Formats' }}</span>
                <div class="flex flex-wrap gap-1">
                  <button
                    v-for="item in items"
                    :key="item.value"
                    @click="toggleItem(formData[section.formKey], item.value)"
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium transition-all border',
                      formData[section.formKey].includes(item.value)
                        ? 'border-cm-dark bg-cm-dark/5 text-cm-dark'
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                    ]"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>
            </template>

            <!-- Simple list for reseaux and events -->
            <template v-else>
              <div class="flex flex-wrap gap-1">
                <button
                  v-for="item in section.data"
                  :key="item.value"
                  @click="toggleItem(formData[section.formKey], item.value)"
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium transition-all border',
                    formData[section.formKey].includes(item.value)
                      ? (section.key === 'reseaux' ? 'border-cm-red bg-cm-red/5 text-cm-red' : 'border-cm-dark bg-cm-dark/5 text-cm-dark')
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                  ]"
                >
                  {{ item.label }}
                </button>
              </div>
            </template>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>
