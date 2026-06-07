import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartService } from '@/services/api'
import { useToast } from '@/composables/useToast'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const isLoading = ref(false)
  const isOpen = ref(false)

  const totalItems = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )
  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + parseFloat(item.subtotal), 0)
  )
  const isEmpty = computed(() => items.value.length === 0)

  async function fetchCart() {
    isLoading.value = true
    try {
      const { data } = await cartService.getCart()
      items.value = data.items || []
    } catch {
      items.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function addToCart(productId, quantity = 1) {
    const { showSuccess } = useToast()
    isLoading.value = true
    try {
      await cartService.addItem(productId, quantity)
      await fetchCart()
      showSuccess('Produs adăugat în coș')
      isOpen.value = true
    } catch (error) {
      const { showError } = useToast()
      showError(error.response?.data?.error || 'Eroare la adăugarea produsului')
    } finally {
      isLoading.value = false
    }
  }

  async function updateQuantity(itemId, quantity) {
    try {
      await cartService.updateItem(itemId, quantity)
      await fetchCart()
    } catch (error) {
      const { showError } = useToast()
      showError(error.response?.data?.error || 'Eroare la actualizarea cantității')
    }
  }

  async function removeItem(itemId) {
    try {
      await cartService.removeItem(itemId)
      await fetchCart()
    } catch {
    }
  }

  async function clearCart() {
    try {
      await cartService.clearCart()
      items.value = []
    } catch {
    }
  }

  return {
    items, isLoading, isOpen,
    totalItems, totalPrice, isEmpty,
    fetchCart, addToCart, updateQuantity, removeItem, clearCart
  }
})
