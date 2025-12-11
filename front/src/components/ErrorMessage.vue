<script setup>
defineProps({
  message: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
    <p class="font-medium">Erreur</p>
    <p class="text-sm">{{ message }}</p>
  </div>
</template>
