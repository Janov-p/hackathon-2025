<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isLoggedIn, matricule } = storeToRefs(authStore)

const isMenuOpen = ref(false)

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function closeMenu() {
  isMenuOpen.value = false
}

function handleLogin() {
  authStore.openLoginModal()
  closeMenu()
}

function handleLogout() {
  authStore.logout()
  closeMenu()
}
</script>

<template>
  <div class="relative">
    <!-- User Button -->
    <button
      @click="toggleMenu"
      class="flex items-center gap-2 px-3 py-2 rounded-lg transition-colors"
      :class="isLoggedIn ? 'bg-cm-gray hover:bg-gray-200' : 'bg-cm-red text-white hover:bg-cm-red/90'"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
      <span class="text-sm font-medium">
        {{ isLoggedIn ? matricule : 'Connexion' }}
      </span>
      <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': isMenuOpen }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown Menu -->
    <Transition name="dropdown">
      <div 
        v-if="isMenuOpen"
        class="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
      >
        <template v-if="isLoggedIn">
          <!-- User Info -->
          <div class="px-4 py-3 bg-cm-gray/50 border-b border-gray-100">
            <p class="text-sm text-cm-dark/60">Connecté en tant que</p>
            <p class="font-semibold text-cm-dark">{{ matricule }}</p>
          </div>

          <!-- Logout -->
          <div class="p-2">
            <button
              @click="handleLogout"
              class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-50 transition-colors text-left"
            >
              <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="text-sm text-red-500">Déconnexion</span>
            </button>
          </div>
        </template>

        <template v-else>
          <!-- Login prompt -->
          <div class="p-4">
            <p class="text-sm text-cm-dark/70 mb-3">
              Connectez-vous pour sauvegarder vos campagnes.
            </p>
            <button
              @click="handleLogin"
              class="w-full bg-cm-red text-white font-medium py-2 px-4 rounded-lg hover:bg-cm-red/90 transition-colors"
            >
              Se connecter
            </button>
          </div>
        </template>
      </div>
    </Transition>

    <!-- Backdrop -->
    <div 
      v-if="isMenuOpen"
      class="fixed inset-0 z-40"
      @click="closeMenu"
    />
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
