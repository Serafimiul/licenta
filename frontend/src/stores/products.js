import { defineStore } from 'pinia'
import { ref } from 'vue'
import { productService, categoryService } from '@/services/api'

export const useProductsStore = defineStore('products', () => {
  const list = ref([])
  const currentProduct = ref(null)
  const filters = ref({})
  const categories = ref([])
  const platforms = ref([])
  const isLoading = ref(false)
  const pagination = ref({ count: 0, next: null, previous: null, page: 1 })

  async function fetchProducts(params = {}) {
    isLoading.value = true
    try {
      const { data } = await productService.list({ ...filters.value, ...params })
      list.value = data.results || data
      pagination.value = {
        count: data.count || list.value.length,
        next: data.next,
        previous: data.previous,
        page: params.page || 1
      }
    } catch {
      list.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function fetchProduct(slug) {
    isLoading.value = true
    try {
      const { data } = await productService.detail(slug)
      currentProduct.value = data
    } catch {
      currentProduct.value = null
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const { data } = await categoryService.getTree()
      categories.value = data
    } catch {
      categories.value = []
    }
  }

  async function fetchPlatforms() {
    try {
      const { data } = await productService.getPlatforms()
      platforms.value = data.results || data
    } catch {
      platforms.value = []
    }
  }

  function setFilter(key, value) {
    if (value === null || value === undefined || value === '') {
      delete filters.value[key]
    } else {
      filters.value[key] = value
    }
  }

  function clearFilters() {
    filters.value = {}
  }

  return {
    list, currentProduct, filters, categories, platforms, isLoading, pagination,
    fetchProducts, fetchProduct, fetchCategories, fetchPlatforms, setFilter, clearFilters
  }
})
