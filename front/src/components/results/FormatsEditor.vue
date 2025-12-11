<script setup>
import { computed, ref } from 'vue'
import { useCampaignStore } from '../../stores/campaign'
import { storeToRefs } from 'pinia'

const store = useCampaignStore()
const { modifiedPlan } = storeToRefs(store)

const formats = computed(() => modifiedPlan.value?.formatsProposés || [])

// Available formats from referential
const availableFormats = [
  { support: 'Quotidien', format: '1/4 page', dimensions: '130x180mm', tarifUnitaire: 850 },
  { support: 'Quotidien', format: '1/2 page', dimensions: '260x180mm', tarifUnitaire: 1500 },
  { support: 'Quotidien', format: 'Pleine page', dimensions: '260x360mm', tarifUnitaire: 2800 },
  { support: 'Site web', format: 'Pavé', dimensions: '300x250px', tarifUnitaire: 500 },
  { support: 'Site web', format: 'Bannière', dimensions: '728x90px', tarifUnitaire: 350 },
  { support: 'Site web', format: 'Habillage', dimensions: 'Full page', tarifUnitaire: 1200 },
  { support: 'Facebook', format: 'Carrousel', dimensions: '1080x1080px', tarifUnitaire: 200 },
  { support: 'Facebook', format: 'Vidéo', dimensions: '1280x720px', tarifUnitaire: 400 },
  { support: 'Instagram', format: 'Story', dimensions: '1080x1920px', tarifUnitaire: 150 },
  { support: 'Instagram', format: 'Post', dimensions: '1080x1080px', tarifUnitaire: 180 },
  { support: 'Newsletter', format: 'Encart', dimensions: '600x200px', tarifUnitaire: 300 }
]

const showAddModal = ref(false)
const selectedNewFormat = ref(null)

function formatCurrency(value) {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0
  }).format(value)
}

function updateQuantity(index, value) {
  if (!modifiedPlan.value) return
  const qty = Math.max(0, Number(value))
  modifiedPlan.value.formatsProposés[index].quantite = qty
  modifiedPlan.value.formatsProposés[index].total = qty * modifiedPlan.value.formatsProposés[index].tarifUnitaire
}

function removeFormat(index) {
  if (!modifiedPlan.value) return
  modifiedPlan.value.formatsProposés.splice(index, 1)
}

function addFormat() {
  if (!modifiedPlan.value || !selectedNewFormat.value) return
  
  const format = availableFormats.find(f => 
    f.support === selectedNewFormat.value.support && f.format === selectedNewFormat.value.format
  )
  
  if (format) {
    modifiedPlan.value.formatsProposés.push({
      ...format,
      quantite: 1,
      total: format.tarifUnitaire
    })
  }
  
  showAddModal.value = false
  selectedNewFormat.value = null
}

const totalFormats = computed(() => {
  return formats.value.reduce((sum, f) => sum + f.total, 0)
})

const groupedAvailableFormats = computed(() => {
  const groups = {}
  availableFormats.forEach(f => {
    if (!groups[f.support]) groups[f.support] = []
    groups[f.support].push(f)
  })
  return groups
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider flex items-center gap-2">
        <svg class="w-4 h-4 text-cm-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
        </svg>
        Formats proposés
      </h3>
      <button
        @click="showAddModal = true"
        class="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-cm-red border border-cm-red rounded-lg hover:bg-cm-red hover:text-white transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Ajouter
      </button>
    </div>

    <!-- Formats table -->
    <div class="border border-gray-200 rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-3 py-2 text-left font-semibold text-gray-600">Support</th>
            <th class="px-3 py-2 text-left font-semibold text-gray-600">Format</th>
            <th class="px-3 py-2 text-right font-semibold text-gray-600">Tarif</th>
            <th class="px-3 py-2 text-center font-semibold text-gray-600 w-20">Qté</th>
            <th class="px-3 py-2 text-right font-semibold text-gray-600">Total</th>
            <th class="px-3 py-2 w-10"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="(format, index) in formats" :key="index" class="hover:bg-gray-50">
            <td class="px-3 py-2 text-gray-800">{{ format.support }}</td>
            <td class="px-3 py-2">
              <span class="font-medium text-gray-800">{{ format.format }}</span>
              <span class="text-xs text-gray-500 block">{{ format.dimensions }}</span>
            </td>
            <td class="px-3 py-2 text-right text-gray-600">{{ formatCurrency(format.tarifUnitaire) }}</td>
            <td class="px-3 py-2">
              <input
                type="number"
                :value="format.quantite"
                @input="updateQuantity(index, $event.target.value)"
                min="0"
                class="w-16 px-2 py-1 text-sm text-center border border-gray-200 rounded focus:ring-1 focus:ring-cm-red/20 focus:border-cm-red"
              />
            </td>
            <td class="px-3 py-2 text-right font-semibold text-gray-800">{{ formatCurrency(format.total) }}</td>
            <td class="px-3 py-2">
              <button
                @click="removeFormat(index)"
                class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                title="Supprimer"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="formats.length === 0">
            <td colspan="6" class="px-3 py-8 text-center text-gray-500">
              Aucun format sélectionné. Cliquez sur "Ajouter" pour commencer.
            </td>
          </tr>
        </tbody>
        <tfoot class="bg-gray-50">
          <tr>
            <td colspan="4" class="px-3 py-3 text-right font-semibold text-gray-700">Total HT</td>
            <td class="px-3 py-3 text-right font-bold text-cm-red text-lg">{{ formatCurrency(totalFormats) }}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Add format modal -->
    <teleport to="body">
      <transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 overflow-hidden">
            <div class="px-6 py-4 bg-cm-dark text-white">
              <h4 class="text-lg font-semibold">Ajouter un format</h4>
            </div>
            <div class="p-6 space-y-4 max-h-96 overflow-y-auto">
              <div v-for="(formats, support) in groupedAvailableFormats" :key="support" class="space-y-2">
                <h5 class="text-sm font-semibold text-gray-700">{{ support }}</h5>
                <div class="space-y-1">
                  <label
                    v-for="format in formats"
                    :key="`${format.support}-${format.format}`"
                    class="flex items-center justify-between p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-cm-red transition-colors"
                    :class="{ 'border-cm-red bg-cm-red/5': selectedNewFormat?.support === format.support && selectedNewFormat?.format === format.format }"
                  >
                    <div class="flex items-center gap-3">
                      <input
                        type="radio"
                        name="newFormat"
                        :value="format"
                        v-model="selectedNewFormat"
                        class="text-cm-red focus:ring-cm-red"
                      />
                      <div>
                        <span class="font-medium text-gray-800">{{ format.format }}</span>
                        <span class="text-xs text-gray-500 block">{{ format.dimensions }}</span>
                      </div>
                    </div>
                    <span class="text-sm font-semibold text-gray-600">{{ formatCurrency(format.tarifUnitaire) }}</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3">
              <button
                @click="showAddModal = false; selectedNewFormat = null"
                class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
              >
                Annuler
              </button>
              <button
                @click="addFormat"
                :disabled="!selectedNewFormat"
                class="px-4 py-2 text-sm font-medium text-white bg-cm-red rounded-lg hover:bg-cm-red/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Ajouter
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>
