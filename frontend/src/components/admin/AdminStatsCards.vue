<script setup>
import { CubeIcon, ClipboardDocumentListIcon, CurrencyDollarIcon, UsersIcon } from '@heroicons/vue/24/outline'

defineProps({
  stats: {
    type: Object,
    default: () => ({ products: 0, orders: 0, revenue: 0, users: 0 })
  }
})

const cards = [
  { key: 'products', label: 'Total Produse', icon: CubeIcon, color: 'bg-blue-50 text-blue-600' },
  { key: 'orders', label: 'Total Comenzi', icon: ClipboardDocumentListIcon, color: 'bg-green-50 text-green-600' },
  { key: 'revenue', label: 'Venituri (RON)', icon: CurrencyDollarIcon, color: 'bg-purple-50 text-purple-600' },
  { key: 'users', label: 'Clienți', icon: UsersIcon, color: 'bg-orange-50 text-orange-600' },
]
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <div v-for="card in cards" :key="card.key" class="bg-white rounded-xl border p-5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500">{{ card.label }}</p>
          <p class="text-2xl font-bold mt-1">{{ stats[card.key] }}</p>
        </div>
        <div class="p-3 rounded-lg" :class="card.color">
          <component :is="card.icon" class="w-6 h-6" />
        </div>
      </div>
    </div>
  </div>
</template>
