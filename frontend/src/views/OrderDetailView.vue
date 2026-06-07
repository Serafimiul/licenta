<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { orderService } from '@/services/api'
import BaseBadge from '@/components/common/BaseBadge.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const route = useRoute()
const order = ref(null)
const loading = ref(true)

const statusVariants = {
  pending: 'warning', confirmed: 'info', shipped: 'info',
  delivered: 'success', cancelled: 'danger',
}

onMounted(async () => {
  try {
    const { data } = await orderService.getOrder(route.params.id)
    order.value = data
  } catch { /* empty */ }
  finally { loading.value = false }
})

function formatDate(d) {
  return new Date(d).toLocaleDateString('ro-RO', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <LoadingSpinner v-if="loading" />

    <template v-else-if="order">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold">Comanda #{{ order.id }}</h1>
          <p class="text-sm text-gray-500">{{ formatDate(order.created_at) }}</p>
        </div>
        <BaseBadge :variant="statusVariants[order.status]" class="text-sm px-3 py-1">
          {{ order.status }}
        </BaseBadge>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl border p-5">
          <h3 class="font-semibold mb-3">Adresa de Livrare</h3>
          <p class="text-sm text-gray-600">{{ order.shipping_name }}</p>
          <p class="text-sm text-gray-600">{{ order.shipping_address }}</p>
          <p class="text-sm text-gray-600">{{ order.shipping_city }}, {{ order.shipping_zip }}</p>
          <p class="text-sm text-gray-600">{{ order.shipping_country }}</p>
          <p v-if="order.notes" class="text-sm text-gray-500 mt-2 italic">{{ order.notes }}</p>
        </div>
        <div class="bg-white rounded-xl border p-5">
          <h3 class="font-semibold mb-3">Sumar</h3>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Produse</span>
              <span>{{ order.items?.length }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Livrare</span>
              <span class="text-green-600">Gratuită</span>
            </div>
          </div>
          <div class="border-t mt-3 pt-3 flex justify-between text-lg font-bold">
            <span>Total</span>
            <span class="text-primary-600">{{ order.total }} RON</span>
          </div>
        </div>
      </div>

      <div class="mt-6 bg-white rounded-xl border overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b">
            <tr>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Produs</th>
              <th class="text-center px-4 py-3 font-medium text-gray-600">Cant.</th>
              <th class="text-right px-4 py-3 font-medium text-gray-600">Preț Unitar</th>
              <th class="text-right px-4 py-3 font-medium text-gray-600">Subtotal</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="item in order.items" :key="item.id">
              <td class="px-4 py-3">{{ item.product_name }}</td>
              <td class="px-4 py-3 text-center">{{ item.quantity }}</td>
              <td class="px-4 py-3 text-right">{{ item.unit_price }} RON</td>
              <td class="px-4 py-3 text-right font-medium">{{ parseFloat(item.subtotal).toFixed(2) }} RON</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-6">
        <RouterLink to="/orders" class="text-primary-600 hover:underline text-sm">&larr; Înapoi la comenzi</RouterLink>
      </div>
    </template>
  </div>
</template>
