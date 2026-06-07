<script setup>
import BaseBadge from '@/components/common/BaseBadge.vue'

defineProps({
  orders: { type: Array, default: () => [] },
})
defineEmits(['status-change'])

const statusVariants = {
  pending: 'warning',
  confirmed: 'info',
  shipped: 'info',
  delivered: 'success',
  cancelled: 'danger',
}

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'shipped', label: 'Shipped' },
  { value: 'delivered', label: 'Delivered' },
  { value: 'cancelled', label: 'Cancelled' },
]

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ro-RO', {
    day: '2-digit', month: 'short', year: 'numeric'
  })
}
</script>

<template>
  <div class="bg-white rounded-xl border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Comanda #</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Client</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Data</th>
          <th class="text-right px-4 py-3 font-medium text-gray-600">Total</th>
          <th class="text-center px-4 py-3 font-medium text-gray-600">Status</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Oraș</th>
          <th class="text-center px-4 py-3 font-medium text-gray-600">Actualizează</th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 font-medium">#{{ order.id }}</td>
          <td class="px-4 py-3">
            <div>{{ order.shipping_name }}</div>
            <div class="text-xs text-gray-500">{{ order.user_email || '' }}</div>
          </td>
          <td class="px-4 py-3 text-gray-500">{{ formatDate(order.created_at) }}</td>
          <td class="px-4 py-3 text-right font-medium">{{ order.total }} RON</td>
          <td class="px-4 py-3 text-center">
            <BaseBadge :variant="statusVariants[order.status] || 'neutral'">
              {{ order.status }}
            </BaseBadge>
          </td>
          <td class="px-4 py-3">{{ order.shipping_city }}</td>
          <td class="px-4 py-3 text-center">
            <select
              :value="order.status"
              @change="$emit('status-change', { id: order.id, status: $event.target.value })"
              class="border rounded text-sm py-1 px-2 bg-white"
            >
              <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
