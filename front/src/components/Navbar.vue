<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="bg-white shadow-sm border-b">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <RouterLink to="/" class="text-xl font-bold text-indigo-600">
          Hackathon 2025
        </RouterLink>
        <div class="flex space-x-4">
          <RouterLink 
            to="/" 
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-100 transition-colors"
          >
            Accueil
          </RouterLink>
          <RouterLink 
            to="/items" 
            class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-100 transition-colors"
          >
            Items
          </RouterLink>
        </div>
      </div>
    </div>
  </nav>
</template>
