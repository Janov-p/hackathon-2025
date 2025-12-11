<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { isLoginModalOpen, isLoggedIn, matricule } = storeToRefs(authStore)

const inputMatricule = ref('')
const inputPassword = ref('')
const error = ref('')

// Reset form when modal opens
watch(isLoginModalOpen, (isOpen) => {
  if (isOpen) {
    inputMatricule.value = ''
    inputPassword.value = ''
    error.value = ''
  }
})

function handleLogin() {
  if (!inputMatricule.value.trim()) {
    error.value = 'Veuillez entrer votre matricule'
    return
  }
  
  if (!inputPassword.value.trim()) {
    error.value = 'Veuillez entrer un mot de passe'
    return
  }

  // Le mot de passe n'est pas vérifié, on accepte tout
  authStore.login(inputMatricule.value.trim())
  authStore.closeLoginModal()
}

function handleClose() {
  authStore.closeLoginModal()
}

function handleBackdropClick(e) {
  if (e.target === e.currentTarget) {
    handleClose()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div 
        v-if="isLoginModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click="handleBackdropClick"
      >
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden transform transition-all">
          <!-- Header -->
          <div class="bg-cm-red px-6 py-4">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-bold text-white">Connexion</h2>
              <button 
                @click="handleClose"
                class="text-white/80 hover:text-white transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="p-6">
            <p class="text-cm-dark/70 text-sm mb-6">
              Connectez-vous pour sauvegarder et retrouver vos campagnes.
            </p>

            <form @submit.prevent="handleLogin" class="space-y-4">
              <!-- Matricule -->
              <div>
                <label for="matricule" class="block text-sm font-medium text-cm-dark mb-1">
                  Matricule commercial
                </label>
                <input
                  id="matricule"
                  v-model="inputMatricule"
                  type="text"
                  placeholder="Ex: CM12345"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cm-red/20 focus:border-cm-red transition-colors"
                />
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-cm-dark mb-1">
                  Mot de passe
                </label>
                <input
                  id="password"
                  v-model="inputPassword"
                  type="password"
                  placeholder="••••••••"
                  class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cm-red/20 focus:border-cm-red transition-colors"
                />
              </div>

              <!-- Error message -->
              <p v-if="error" class="text-red-500 text-sm">
                {{ error }}
              </p>

              <!-- Submit -->
              <button
                type="submit"
                class="w-full bg-cm-red text-white font-medium py-2.5 px-4 rounded-lg hover:bg-cm-red/90 transition-colors"
              >
                Se connecter
              </button>
            </form>

            <p class="text-xs text-cm-dark/50 mt-4 text-center">
              Système de démonstration - Aucune vérification du mot de passe
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.95);
}
</style>
