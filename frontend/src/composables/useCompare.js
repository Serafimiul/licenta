import { ref } from 'vue'

const MAX_COMPARE = 4
const STORAGE_KEY = 'compare_list'
const compareList = ref(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'))

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(compareList.value))
}

export function useCompare() {
  function addToCompare(product) {
    if (compareList.value.length >= MAX_COMPARE) return false
    if (compareList.value.find((p) => p.id === product.id)) return false
    compareList.value.push({
      id: product.id,
      name: product.name,
      slug: product.slug,
      image: product.image
    })
    persist()
    return true
  }

  function removeFromCompare(productId) {
    compareList.value = compareList.value.filter((p) => p.id !== productId)
    persist()
  }

  function isInCompare(productId) {
    return compareList.value.some((p) => p.id === productId)
  }

  function clearCompare() {
    compareList.value = []
    persist()
  }

  return { compareList, addToCompare, removeFromCompare, isInCompare, clearCompare }
}
