<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useCompare } from '@/composables/useCompare'
import { useToast } from '@/composables/useToast'
import ProductImageGallery from '@/components/product/ProductImageGallery.vue'
import ProductSpecs from '@/components/product/ProductSpecs.vue'
import RecommendationsSection from '@/components/product/RecommendationsSection.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const products = useProductsStore()
const cart = useCartStore()
const auth = useAuthStore()
const { isInCompare, addToCompare, removeFromCompare } = useCompare()
const { showInfo } = useToast()

const quantity = ref(1)
const activeTab = ref('description')

const slug = computed(() => route.params.slug)
const product = computed(() => products.currentProduct)

onMounted(() => products.fetchProduct(slug.value))
watch(slug, (val) => { if (val) products.fetchProduct(val) })

const stockStatus = computed(() => {
  if (!product.value) return {}
  if (product.value.stock === 0) return { label: 'Stoc epuizat', variant: 'danger' }
  if (product.value.stock <= 5) return { label: `Doar ${product.value.stock} în stoc`, variant: 'warning' }
  return { label: 'În stoc', variant: 'success' }
})

const inCompare = computed(() => product.value && isInCompare(product.value.id))

function toggleCompare() {
  if (inCompare.value) {
    removeFromCompare(product.value.id)
    return
  }
  const added = addToCompare(product.value)
  showInfo(added ? 'Adăugat la comparare' : 'Poți compara maxim 4 produse')
}

function handleAddToCart() {
  if (!auth.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  if (product.value) {
    cart.addToCart(product.value.id, quantity.value)
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <LoadingSpinner v-if="products.isLoading" />

    <template v-else-if="product">
      <nav class="text-sm text-gray-500 mb-6">
        <RouterLink to="/" class="hover:text-primary-600">Acasă</RouterLink>
        <span class="mx-2">/</span>
        <RouterLink
          :to="{ name: 'category', params: { slug: product.category?.slug } }"
          class="hover:text-primary-600"
        >{{ product.category?.name }}</RouterLink>
        <span class="mx-2">/</span>
        <span class="text-gray-900">{{ product.name }}</span>
      </nav>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <ProductImageGallery :image="product.image" :name="product.name" />
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
          <p class="text-sm text-gray-500 mb-4">
            SKU: {{ product.sku }} | {{ product.manufacturer }}
          </p>

          <div class="flex items-center gap-3 mb-4">
            <span class="text-3xl font-bold text-primary-600">{{ product.price }} RON</span>
            <BaseBadge :variant="stockStatus.variant">{{ stockStatus.label }}</BaseBadge>
          </div>

          <div v-if="product.compatible_platforms?.length" class="mb-6">
            <p class="text-sm font-medium text-gray-700 mb-2">Platforme Compatibile:</p>
            <div class="flex flex-wrap gap-2">
              <BaseBadge v-for="p in product.compatible_platforms" :key="p.id" variant="info">
                {{ p.name }}
              </BaseBadge>
            </div>
          </div>

          <div class="flex items-center gap-3 mb-4">
            <div class="flex items-center border rounded-lg">
              <button @click="quantity = Math.max(1, quantity - 1)" class="px-3 py-2 hover:bg-gray-50">-</button>
              <span class="px-4 py-2 border-x text-sm">{{ quantity }}</span>
              <button @click="quantity++" class="px-3 py-2 hover:bg-gray-50">+</button>
            </div>
            <BaseButton
              variant="primary"
              size="lg"
              :disabled="product.stock === 0"
              @click="handleAddToCart"
            >Adaugă în Coș</BaseButton>
          </div>

          <button
            @click="toggleCompare"
            class="text-sm text-primary-600 hover:underline"
          >
            {{ inCompare ? 'Elimină din comparare' : 'Adaugă la comparare' }}
          </button>
        </div>
      </div>

      <div class="mt-12 border-b">
        <nav class="flex space-x-8">
          <button
            v-for="tab in [{key: 'description', label: 'Descriere'}, {key: 'specifications', label: 'Specificații'}, {key: 'downloads', label: 'Descărcări'}]"
            :key="tab.key"
            @click="activeTab = tab.key"
            class="py-3 text-sm font-medium border-b-2"
            :class="activeTab === tab.key ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >{{ tab.label }}</button>
        </nav>
      </div>

      <div class="py-6">
        <div v-if="activeTab === 'description'" class="prose prose-sm max-w-none text-gray-700">
          <p>{{ product.description }}</p>
        </div>
        <div v-else-if="activeTab === 'specifications'">
          <ProductSpecs :attributes="product.attributes" />
        </div>
        <div v-else-if="activeTab === 'downloads'">
          <a
            v-if="product.datasheet"
            :href="product.datasheet"
            target="_blank"
            class="inline-flex items-center gap-2 text-primary-600 hover:underline"
          >
            Descarcă Fișa Tehnică (PDF)
          </a>
          <p v-else class="text-gray-500">Nicio fișă tehnică disponibilă pentru acest produs.</p>
        </div>
      </div>

      <RecommendationsSection :productSlug="product.slug" />
    </template>
  </div>
</template>
