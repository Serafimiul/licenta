<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import ProductList from '@/components/product/ProductList.vue'
import ProductFilters from '@/components/product/ProductFilters.vue'
import BasePagination from '@/components/common/BasePagination.vue'
import BaseSelect from '@/components/common/BaseSelect.vue'
import { FunnelIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const products = useProductsStore()

const showMobileFilters = ref(false)
const currentPage = ref(1)

const slug = computed(() => route.params.slug)
const filters = ref({})

const sortOptions = [
  { value: '-created_at', label: 'Cele mai noi' },
  { value: 'price', label: 'Preț: Crescător' },
  { value: '-price', label: 'Preț: Descrescător' },
  { value: 'name', label: 'Nume A-Z' },
]
const ordering = ref('-created_at')

onMounted(() => {
  const q = route.query
  if (q.ordering) ordering.value = q.ordering
  if (q.price_min) filters.value.price_min = q.price_min
  if (q.price_max) filters.value.price_max = q.price_max
  if (q.platform) filters.value.platform = q.platform
  if (q.search) filters.value.search = q.search
  Object.keys(q).filter(k => k.startsWith('attr_')).forEach(k => {
    filters.value[k] = q[k]
  })
  fetchData()
})

watch([slug], () => {
  filters.value = {}
  currentPage.value = 1
  fetchData()
})

function onFiltersChange(newFilters) {
  filters.value = newFilters
  currentPage.value = 1
  syncUrlAndFetch()
}

function onSortChange(val) {
  ordering.value = val
  currentPage.value = 1
  syncUrlAndFetch()
}

function onPageChange(page) {
  currentPage.value = page
  syncUrlAndFetch()
}

function syncUrlAndFetch() {
  const query = { ...filters.value, ordering: ordering.value }
  if (currentPage.value > 1) query.page = currentPage.value
  router.replace({ query })
  fetchData()
}

function fetchData() {
  products.fetchProducts({
    category: slug.value,
    ...filters.value,
    ordering: ordering.value,
    page: currentPage.value,
  })
}

const activeFilterTags = computed(() => {
  return Object.entries(filters.value)
    .filter(([, v]) => v)
    .map(([k, v]) => ({ key: k, label: `${k.replace('attr_', '').replace('_', ' ')}: ${v}` }))
})

function removeFilter(key) {
  delete filters.value[key]
  syncUrlAndFetch()
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <nav class="text-sm text-gray-500 mb-6">
      <RouterLink to="/" class="hover:text-primary-600">Acasă</RouterLink>
      <span class="mx-2">/</span>
      <span class="text-gray-900 capitalize">{{ slug?.replace(/-/g, ' ') }}</span>
    </nav>

    <div class="flex gap-8">
      <aside class="hidden lg:block w-64 flex-shrink-0">
        <ProductFilters
          :categorySlug="slug"
          :modelValue="filters"
          @update:modelValue="onFiltersChange"
        />
      </aside>

      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-4 gap-4">
          <div class="flex items-center gap-2">
            <button
              @click="showMobileFilters = true"
              class="lg:hidden btn border px-3 py-2 text-sm"
            >
              <FunnelIcon class="w-4 h-4 mr-1 inline" /> Filtre
            </button>
            <span class="text-sm text-gray-500">{{ products.pagination.count }} produse</span>
          </div>
          <BaseSelect
            :options="sortOptions"
            :modelValue="ordering"
            @update:modelValue="onSortChange"
            class="w-48"
          />
        </div>

        <div v-if="activeFilterTags.length" class="flex flex-wrap gap-2 mb-4">
          <span
            v-for="tag in activeFilterTags"
            :key="tag.key"
            class="inline-flex items-center gap-1 px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded-full"
          >
            {{ tag.label }}
            <button @click="removeFilter(tag.key)">
              <XMarkIcon class="w-3 h-3" />
            </button>
          </span>
        </div>

        <ProductList :products="products.list" :loading="products.isLoading" />

        <BasePagination
          :currentPage="currentPage"
          :totalItems="products.pagination.count"
          @page-change="onPageChange"
        />
      </div>
    </div>
    <Teleport to="body">
      <div v-if="showMobileFilters" class="fixed inset-0 z-50 lg:hidden">
        <div class="absolute inset-0 bg-black/50" @click="showMobileFilters = false" />
        <div class="absolute inset-y-0 left-0 w-80 bg-white p-6 overflow-y-auto">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold">Filtre</h3>
            <button @click="showMobileFilters = false" class="text-gray-400">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>
          <ProductFilters
            :categorySlug="slug"
            :modelValue="filters"
            @update:modelValue="(f) => { onFiltersChange(f); showMobileFilters = false }"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>
