<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { productService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import AdminProductTable from '@/components/admin/AdminProductTable.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const products = ref([])
const loading = ref(true)
const { showSuccess, showError } = useToast()

async function load() {
  loading.value = true
  try {
    const { data } = await productService.list({ page_size: 500 })
    products.value = data.results || data
  } catch {
    showError('Nu am putut încărca produsele.')
  } finally {
    loading.value = false
  }
}

async function handleDelete(slug) {
  if (!window.confirm('Sigur ștergi acest produs?')) return
  try {
    await productService.remove(slug)
    products.value = products.value.filter((p) => p.slug !== slug)
    showSuccess('Produs șters.')
  } catch (err) {
    showError(err?.response?.data?.detail || 'Eroare la ștergere.')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold">Produse</h2>
      <RouterLink :to="{ name: 'admin-product-new' }">
        <BaseButton variant="primary">Adaugă Produs</BaseButton>
      </RouterLink>
    </div>

    <LoadingSpinner v-if="loading" />
    <AdminProductTable
      v-else
      :products="products"
      @delete="handleDelete"
    />
  </div>
</template>
