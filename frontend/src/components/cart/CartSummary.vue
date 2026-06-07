<script setup>
import { useCartStore } from '@/stores/cart'
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'

const cart = useCartStore()
</script>

<template>
  <div class="bg-white rounded-xl border p-6 sticky top-24">
    <h3 class="text-lg font-semibold mb-4">Sumar Comandă</h3>

    <div class="space-y-2 text-sm">
      <div class="flex justify-between">
        <span class="text-gray-600">Subtotal ({{ cart.totalItems }} produse)</span>
        <span>{{ cart.totalPrice.toFixed(2) }} RON</span>
      </div>
      <div class="flex justify-between">
        <span class="text-gray-600">Livrare</span>
        <span class="text-green-600">Gratuită</span>
      </div>
    </div>

    <div class="border-t mt-4 pt-4 flex justify-between text-lg font-bold">
      <span>Total</span>
      <span class="text-primary-600">{{ cart.totalPrice.toFixed(2) }} RON</span>
    </div>

    <RouterLink to="/checkout" class="block mt-4">
      <BaseButton variant="primary" class="w-full">Finalizează Comanda</BaseButton>
    </RouterLink>
  </div>
</template>
