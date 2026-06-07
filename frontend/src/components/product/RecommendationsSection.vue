<script setup>
import { ref, onMounted, watch } from 'vue'
import { productService } from '@/services/api'
import ProductCard from './ProductCard.vue'

const props = defineProps({
  productSlug: { type: String, required: true },
})

const recommendations = ref([])
const loading = ref(false)

async function fetchRecs() {
  loading.value = true
  try {
    const { data } = await productService.getRecommendations(props.productSlug)
    recommendations.value = data
  } catch {
    recommendations.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecs)
watch(() => props.productSlug, fetchRecs)
</script>

<template>
  <section v-if="recommendations.length" class="mt-12">
    <h2 class="text-xl font-bold text-gray-900 mb-6">Produse Similare</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <ProductCard v-for="product in recommendations" :key="product.id" :product="product" />
    </div>
  </section>
</template>
