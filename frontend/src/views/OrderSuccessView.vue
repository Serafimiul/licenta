<script setup>
import { useRoute } from 'vue-router'
import { CheckCircleIcon } from '@heroicons/vue/24/solid'
import BaseButton from '@/components/common/BaseButton.vue'

const route = useRoute()
const orderId = route.query.id
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-20 text-center">
    <CheckCircleIcon class="w-20 h-20 text-green-500 mx-auto mb-6" />
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Comandă Plasată!</h1>
    <p class="text-gray-500 mb-2">Comanda ta a fost creată cu succes.</p>
    <p v-if="orderId" class="text-lg font-semibold text-primary-600 mb-8">
      Comanda #{{ orderId }}
    </p>

    <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
      <RouterLink to="/orders">
        <BaseButton variant="primary">Vezi Comenzile Mele</BaseButton>
      </RouterLink>
      <RouterLink to="/">
        <BaseButton variant="outline">Continuă Cumpărăturile</BaseButton>
      </RouterLink>
    </div>
  </div>
</template>
