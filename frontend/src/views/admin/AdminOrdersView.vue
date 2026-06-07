<script setup>
import { ref, onMounted } from 'vue'
import { orderService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import AdminOrderTable from '@/components/admin/AdminOrderTable.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const orders = ref([])
const loading = ref(true)
const { showSuccess, showError } = useToast()

async function load() {
  loading.value = true
  try {
    const { data } = await orderService.listOrders()
    orders.value = data.results || data
  } catch {
    showError('Nu am putut încărca comenzile.')
  } finally {
    loading.value = false
  }
}

async function handleStatusChange({ id, status }) {
  try {
    const { data } = await orderService.updateStatus(id, status)
    const idx = orders.value.findIndex((o) => o.id === id)
    if (idx !== -1) orders.value[idx] = data
    showSuccess(`Status comandă #${id} → ${status}`)
  } catch (err) {
    showError(err?.response?.data?.error || 'Eroare la actualizare.')
    load() 
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-6">Comenzi</h2>
    <LoadingSpinner v-if="loading" />
    <AdminOrderTable v-else :orders="orders" @status-change="handleStatusChange" />
  </div>
</template>
