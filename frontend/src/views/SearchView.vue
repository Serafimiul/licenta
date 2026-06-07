<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import ProductList from '@/components/product/ProductList.vue'
import BasePagination from '@/components/common/BasePagination.vue'
import BaseSelect from '@/components/common/BaseSelect.vue'

const route = useRoute()
const products = useProductsStore()

const currentPage = ref(1)
const ordering = ref('-created_at')

const sortOptions = [
  { value: '-created_at', label: 'Cele mai noi' },
  { value: 'price', label: 'Preț: Crescător' },
  { value: '-price', label: 'Preț: Descrescător' },
  { value: 'name', label: 'Nume A-Z' },
]

const term = computed(() => (route.query.search || '').toString())
const heading = computed(() =>
  term.value ? `Rezultate pentru „${term.value}”` : 'Toate produsele'
)

onMounted(fetchData)
watch(() => route.query.search, () => {
  currentPage.value = 1
  fetchData()
})

function fetchData() {
  const params = { ordering: ordering.value, page: currentPage.value }
  if (term.value) params.search = term.value
  products.fetchProducts(params)
}

function onSortChange(val) {
  ordering.value = val
  currentPage.value = 1
  fetchData()
}

function onPageChange(page) {
  currentPage.value = page
  fetchData()
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ heading }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ products.pagination.count }} produse</p>
      </div>
      <BaseSelect
        :options="sortOptions"
        :modelValue="ordering"
        @update:modelValue="onSortChange"
        class="w-48"
      />
    </div>

    <ProductList :products="products.list" :loading="products.isLoading" />

    <BasePagination
      :currentPage="currentPage"
      :totalItems="products.pagination.count"
      @page-change="onPageChange"
    />
  </div>
</template>
