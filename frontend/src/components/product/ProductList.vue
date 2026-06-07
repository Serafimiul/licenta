<script setup>
import ProductCard from './ProductCard.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps({
  products: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})
</script>

<template>
  <div>
    <LoadingSpinner v-if="loading" />
    <EmptyState
      v-else-if="products.length === 0"
      title="Niciun produs găsit"
      message="Încearcă să ajustezi filtrele sau termenii de căutare."
    />
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <ProductCard v-for="product in products" :key="product.id" :product="product" />
    </div>
  </div>
</template>
