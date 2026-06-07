<script setup>
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useCompare } from '@/composables/useCompare'
import { ShoppingCartIcon } from '@heroicons/vue/24/outline'
import BaseBadge from '@/components/common/BaseBadge.vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  product: { type: Object, required: true },
})

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()
const { isInCompare, addToCompare, removeFromCompare } = useCompare()
const { showInfo } = useToast()

const stockStatus = computed(() => {
  if (props.product.stock === 0) return { label: 'Stoc epuizat', variant: 'danger' }
  if (props.product.stock <= 5) return { label: 'Stoc redus', variant: 'warning' }
  return { label: 'În stoc', variant: 'success' }
})

const inCompare = computed(() => isInCompare(props.product.id))

function toggleCompare() {
  if (inCompare.value) {
    removeFromCompare(props.product.id)
    return
  }
  const added = addToCompare(props.product)
  showInfo(added ? 'Adăugat la comparare' : 'Poți compara maxim 4 produse')
}

function handleAddToCart() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: `/product/${props.product.slug}` } })
    return
  }
  cart.addToCart(props.product.id)
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group">
    <RouterLink :to="{ name: 'product-detail', params: { slug: product.slug } }">
      <div class="aspect-square bg-gray-50 p-4 flex items-center justify-center overflow-hidden">
        <img
          v-if="product.image"
          :src="product.image"
          :alt="product.name"
          class="max-h-full object-contain group-hover:scale-105 transition-transform duration-300"
        />
        <div v-else class="text-gray-300 text-4xl">&#9881;</div>
      </div>
    </RouterLink>

    <div class="p-4">
      <p class="text-xs text-gray-500 mb-1">{{ product.category_name }}</p>
      <RouterLink :to="{ name: 'product-detail', params: { slug: product.slug } }">
        <h3 class="font-medium text-gray-900 text-sm leading-tight mb-2 line-clamp-2 hover:text-primary-600">
          {{ product.name }}
        </h3>
      </RouterLink>

      <div v-if="product.compatible_platforms?.length" class="flex flex-wrap gap-1 mb-2">
        <BaseBadge v-for="p in product.compatible_platforms" :key="p.id" variant="info">
          {{ p.name }}
        </BaseBadge>
      </div>

      <div class="flex items-center justify-between mb-3">
        <span class="text-lg font-bold text-primary-600">{{ product.price }} RON</span>
        <BaseBadge :variant="stockStatus.variant">{{ stockStatus.label }}</BaseBadge>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="handleAddToCart"
          :disabled="product.stock === 0"
          class="flex-1 btn bg-primary-600 text-white hover:bg-primary-700 px-3 py-2 text-xs disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ShoppingCartIcon class="w-4 h-4 mr-1" />
          Adaugă în Coș
        </button>
        <label class="flex items-center space-x-1 cursor-pointer text-xs text-gray-500">
          <input type="checkbox" :checked="inCompare" @change="toggleCompare" class="rounded" />
          <span>Compară</span>
        </label>
      </div>
    </div>
  </div>
</template>
