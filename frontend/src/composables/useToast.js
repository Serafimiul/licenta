import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

export function useToast() {
  function addToast(message, type = 'info', duration = 3000) {
    const id = nextId++
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function showSuccess(message) {
    addToast(message, 'success')
  }

  function showError(message) {
    addToast(message, 'error', 5000)
  }

  function showInfo(message) {
    addToast(message, 'info')
  }

  return { toasts, addToast, removeToast, showSuccess, showError, showInfo }
}
