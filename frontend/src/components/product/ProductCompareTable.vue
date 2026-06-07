<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCompare } from '@/composables/useCompare'
import { XMarkIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  products: { type: Array, default: () => [] },
})

const { removeFromCompare } = useCompare()

const allAttributes = computed(() => {
  const map = new Map()
  for (const product of props.products) {
    for (const attr of (product.attributes || [])) {
      if (!map.has(attr.slug)) {
        map.set(attr.slug, { name: attr.name, unit: attr.unit, slug: attr.slug })
      }
    }
  }
  return Array.from(map.values())
})

function getAttrValue(product, attrSlug) {
  const attr = product.attributes?.find(a => a.slug === attrSlug)
  return attr?.display_value || '-'
}
</script>

<template>
  <div class="overflow-x-auto">
    <table class="w-full text-sm border">
      <thead>
        <tr class="bg-gray-50 border-b">
          <th class="p-3 text-left font-medium text-gray-600 min-w-[150px]">Specificație</th>
          <th v-for="product in products" :key="product.id" class="p-3 text-center min-w-[200px]">
            <div class="relative">
              <button
                @click="removeFromCompare(product.id)"
                class="absolute -top-1 -right-1 text-gray-400 hover:text-red-500"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
              <img
                :src="product.image"
                :alt="product.name"
                class="w-16 h-16 mx-auto object-contain mb-2"
              />
              <RouterLink
                :to="{ name: 'product-detail', params: { slug: product.slug } }"
                class="text-xs font-medium text-primary-600 hover:underline line-clamp-2"
              >{{ product.name }}</RouterLink>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr class="border-b">
          <td class="p-3 font-medium text-gray-700">Preț</td>
          <td v-for="product in products" :key="product.id" class="p-3 text-center font-semibold text-primary-600">
            {{ product.price }} RON
          </td>
        </tr>
        <tr class="border-b bg-gray-50">
          <td class="p-3 font-medium text-gray-700">Producător</td>
          <td v-for="product in products" :key="product.id" class="p-3 text-center">
            {{ product.manufacturer || '-' }}
          </td>
        </tr>
        <tr v-for="(attr, idx) in allAttributes" :key="attr.slug" class="border-b" :class="idx % 2 === 0 ? '' : 'bg-gray-50'">
          <td class="p-3 font-medium text-gray-700">
            {{ attr.name }}
            <span v-if="attr.unit" class="text-gray-400 text-xs">({{ attr.unit }})</span>
          </td>
          <td v-for="product in products" :key="product.id" class="p-3 text-center">
            {{ getAttrValue(product, attr.slug) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
