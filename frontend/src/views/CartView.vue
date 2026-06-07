<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/cart/CartItem.vue'
import CartSummary from '@/components/cart/CartSummary.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const cart = useCartStore()

onMounted(() => cart.fetchCart())
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold mb-6">Coș de Cumpărături</h1>

    <LoadingSpinner v-if="cart.isLoading && cart.isEmpty" />

    <EmptyState
      v-else-if="cart.isEmpty"
      title="Coșul tău este gol"
      message="Răsfoiește catalogul nostru și adaugă produse în coș."
      actionLabel="Continuă Cumpărăturile"
      actionTo="/search"
    />

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-3">
        <CartItem v-for="item in cart.items" :key="item.id" :item="item" />
      </div>

      <div>
        <CartSummary />
      </div>
    </div>
  </div>
</template>
