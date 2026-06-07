<script setup>
import { useCartStore } from '@/stores/cart'
import { RouterLink } from 'vue-router'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import CartItem from './CartItem.vue'

const cart = useCartStore()
</script>

<template>
  <Teleport to="body">
    <Transition name="sidebar">
      <div v-if="cart.isOpen" class="fixed inset-0 z-50 flex justify-end">
        <div class="absolute inset-0 bg-black/40" @click="cart.isOpen = false" />
        <div class="relative w-full max-w-md bg-white shadow-xl flex flex-col">
          <div class="flex items-center justify-between px-4 py-4 border-b">
            <h2 class="text-lg font-semibold">Coș de Cumpărături ({{ cart.totalItems }})</h2>
            <button @click="cart.isOpen = false" class="text-gray-400 hover:text-gray-600">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div v-if="cart.isEmpty" class="text-center py-12 text-gray-500">
              <p>Coșul tău este gol</p>
            </div>
            <CartItem
              v-for="item in cart.items"
              :key="item.id"
              :item="item"
              :compact="true"
            />
          </div>

          <div v-if="!cart.isEmpty" class="border-t px-4 py-4 space-y-3">
            <div class="flex justify-between text-lg font-semibold">
              <span>Total</span>
              <span>{{ cart.totalPrice.toFixed(2) }} RON</span>
            </div>
            <RouterLink
              to="/cart"
              @click="cart.isOpen = false"
              class="block w-full text-center btn bg-primary-600 text-white hover:bg-primary-700 py-2.5 rounded-lg text-sm"
            >
              Vezi Coșul și Finalizează
            </RouterLink>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sidebar-enter-active, .sidebar-leave-active { transition: all 0.3s ease; }
.sidebar-enter-from, .sidebar-leave-to { opacity: 0; }
.sidebar-enter-from > div:last-child, .sidebar-leave-to > div:last-child { transform: translateX(100%); }
</style>
