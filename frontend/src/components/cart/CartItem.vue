<script setup>
import { useCartStore } from '@/stores/cart'
import { MinusIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

defineProps({
  item: { type: Object, required: true },
  compact: { type: Boolean, default: false },
})

const cart = useCartStore()
</script>

<template>
  <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
    <img
      v-if="item.product_detail?.image"
      :src="item.product_detail.image"
      :alt="item.product_detail.name"
      class="w-16 h-16 object-contain rounded bg-white border"
    />
    <div v-else class="w-16 h-16 bg-white border rounded flex items-center justify-center text-gray-300 text-xl">&#9881;</div>

    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 truncate">
        {{ item.product_detail?.name || 'Produs' }}
      </p>
      <p class="text-sm text-primary-600 font-semibold">
        {{ item.product_detail?.price }} RON
      </p>

      <div v-if="!compact" class="flex items-center gap-2 mt-2">
        <button
          @click="cart.updateQuantity(item.id, item.quantity - 1)"
          class="p-1 border rounded hover:bg-gray-100"
        >
          <MinusIcon class="w-3 h-3" />
        </button>
        <span class="text-sm font-medium w-8 text-center">{{ item.quantity }}</span>
        <button
          @click="cart.updateQuantity(item.id, item.quantity + 1)"
          class="p-1 border rounded hover:bg-gray-100"
        >
          <PlusIcon class="w-3 h-3" />
        </button>
      </div>
      <p v-else class="text-xs text-gray-500">Cant.: {{ item.quantity }}</p>
    </div>

    <div class="text-right">
      <p class="text-sm font-semibold">{{ parseFloat(item.subtotal).toFixed(2) }}</p>
      <button @click="cart.removeItem(item.id)" class="text-red-400 hover:text-red-600 mt-1">
        <TrashIcon class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
