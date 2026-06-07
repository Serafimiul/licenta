<script setup>
import { ref, watch, onMounted } from 'vue'
import { useCompare } from '@/composables/useCompare'
import { productService } from '@/services/api'
import ProductCompareTable from '@/components/product/ProductCompareTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const { compareList, clearCompare } = useCompare()
const products = ref([])
const loading = ref(false)

async function fetchCompareData() {
  if (compareList.value.length < 2) { products.value = []; return }
  loading.value = true
  try {
    const ids = compareList.value.map(p => p.id)
    const { data } = await productService.compare(ids)
    products.value = data
  } catch {
    products.value = []
  } finally {
    loading.value = false
  }
}

onMounted(fetchCompareData)
watch(compareList, fetchCompareData, { deep: true })
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Compară Produse</h1>
      <BaseButton v-if="compareList.length" variant="outline" size="sm" @click="clearCompare">
        Șterge Tot
      </BaseButton>
    </div>

    <EmptyState
      v-if="compareList.length < 2 && !loading"
      title="Nu sunt suficiente produse pentru comparare"
      message="Adaugă cel puțin 2 produse pentru a le compara unul lângă altul."
      actionLabel="Răsfoiește Produse"
      actionTo="/search"
    />

    <LoadingSpinner v-else-if="loading" />

    <ProductCompareTable v-else :products="products" />
  </div>
</template>
