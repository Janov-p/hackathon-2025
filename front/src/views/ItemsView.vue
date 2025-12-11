<script setup>
import { ref, onMounted } from 'vue'
import { useItemsStore } from '../stores/items'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorMessage from '../components/ErrorMessage.vue'

const store = useItemsStore()
const newItemName = ref('')
const showForm = ref(false)

onMounted(() => {
  store.fetchItems()
})

async function handleSubmit() {
  if (!newItemName.value.trim()) return
  
  try {
    await store.createItem({ name: newItemName.value })
    newItemName.value = ''
    showForm.value = false
  } catch (e) {
    // Erreur gérée par le store
  }
}

async function handleDelete(id) {
  if (confirm('Êtes-vous sûr de vouloir supprimer cet item ?')) {
    await store.deleteItem(id)
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Items</h1>
      <button 
        @click="showForm = !showForm"
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Ajouter
      </button>
    </div>

    <!-- Formulaire d'ajout -->
    <div v-if="showForm" class="bg-white p-6 rounded-xl shadow-sm border mb-6">
      <h2 class="text-lg font-semibold mb-4">Nouvel item</h2>
      <form @submit.prevent="handleSubmit" class="flex gap-4">
        <input 
          v-model="newItemName"
          type="text"
          placeholder="Nom de l'item"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
        />
        <button 
          type="submit"
          :disabled="store.loading"
          class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          Créer
        </button>
        <button 
          type="button"
          @click="showForm = false"
          class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Annuler
        </button>
      </form>
    </div>

    <!-- État de chargement -->
    <LoadingSpinner v-if="store.loading && !store.items.length" />

    <!-- Erreur -->
    <ErrorMessage v-else-if="store.error" :message="store.error" />

    <!-- Liste vide -->
    <div v-else-if="!store.items.length" class="text-center py-12 bg-white rounded-xl border">
      <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p class="text-gray-500">Aucun item pour le moment</p>
      <p class="text-gray-400 text-sm mt-1">Cliquez sur "Ajouter" pour créer votre premier item</p>
    </div>

    <!-- Liste des items -->
    <div v-else class="space-y-3">
      <div 
        v-for="item in store.items" 
        :key="item.id"
        class="bg-white p-4 rounded-xl shadow-sm border flex items-center justify-between hover:shadow-md transition-shadow"
      >
        <div>
          <h3 class="font-medium text-gray-900">{{ item.name }}</h3>
          <p v-if="item.createdAt" class="text-sm text-gray-500">
            Créé le {{ new Date(item.createdAt).toLocaleDateString('fr-FR') }}
          </p>
        </div>
        <button 
          @click="handleDelete(item.id)"
          class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="Supprimer"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
