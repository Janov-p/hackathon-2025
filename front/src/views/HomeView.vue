<script setup>
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center py-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        Bienvenue sur Hackathon 2025
      </h1>
      <p class="text-lg text-gray-600 mb-8">
        Application Vue.js connectée à une API
      </p>
      <RouterLink 
        to="/items" 
        class="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Voir les items
        <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </RouterLink>
    </div>

    <div class="grid md:grid-cols-3 gap-6 mt-12">
      <div class="bg-white p-6 rounded-xl shadow-sm border">
        <div class="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Vue 3</h3>
        <p class="text-gray-600 text-sm">Framework moderne avec Composition API</p>
      </div>

      <div class="bg-white p-6 rounded-xl shadow-sm border">
        <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">API REST</h3>
        <p class="text-gray-600 text-sm">Connexion via Axios avec gestion d'erreurs</p>
      </div>

      <div class="bg-white p-6 rounded-xl shadow-sm border">
        <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
          <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <h3 class="font-semibold text-gray-900 mb-2">Pinia</h3>
        <p class="text-gray-600 text-sm">Store centralisé pour la gestion d'état</p>
      </div>
    </div>
  </div>
</template>
