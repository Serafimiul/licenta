<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { orderService } from '@/services/api'
import BaseBadge from '@/components/common/BaseBadge.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const orders = ref([])
const loading = ref(true)

const statusVariants = {
  pending: 'warning',
  confirmed: 'info',
  shipped: 'info',
  delivered: 'success',
  cancelled: 'danger',
}

onMounted(async () => {
  try {
    const { data } = await orderService.listOrders()
    orders.value = data.results || data
  } catch { /* empty */ }
  finally { loading.value = false }
})

function formatDate(d) {
  return new Date(d).toLocaleDateString('ro-RO', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold mb-6">Comenzile Mele</h1>

    <LoadingSpinner v-if="loading" />
    <EmptyState
      v-else-if="!orders.length"
      title="Nicio comandă încă"
      message="Istoricul comenzilor tale va apărea aici."
      actionLabel="Începe Cumpărăturile"
      actionTo="/"
    />

    <div v-else class="space-y-4">
      <RouterLink
        v-for="order in orders"
        :key="order.id"
        :to="{ name: 'order-detail', params: { id: order.id } }"
        class="block bg-white rounded-xl border p-5 hover:shadow-sm transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <span class="font-semibold">Comanda #{{ order.id }}</span>
            <span class="text-sm text-gray-500 ml-3">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="flex items-center gap-3">
            <BaseBadge :variant="statusVariants[order.status]">{{ order.status }}</BaseBadge>
            <span class="font-semibold text-primary-600">{{ order.total }} RON</span>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
