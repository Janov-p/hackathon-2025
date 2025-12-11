import { defineStore } from 'pinia'
import { ref } from 'vue'
import { itemsService } from '../api'

export const useItemsStore = defineStore('items', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchItems() {
    loading.value = true
    error.value = null
    try {
      const response = await itemsService.getAll()
      items.value = response.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Erreur lors du chargement'
    } finally {
      loading.value = false
    }
  }

  async function createItem(data) {
    loading.value = true
    error.value = null
    try {
      const response = await itemsService.create(data)
      items.value.push(response.data)
      return response.data
    } catch (e) {
      error.value = e.response?.data?.message || 'Erreur lors de la création'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteItem(id) {
    loading.value = true
    error.value = null
    try {
      await itemsService.delete(id)
      items.value = items.value.filter(item => item.id !== id)
    } catch (e) {
      error.value = e.response?.data?.message || 'Erreur lors de la suppression'
      throw e
    } finally {
      loading.value = false
    }
  }

  return { items, loading, error, fetchItems, createItem, deleteItem }
})
