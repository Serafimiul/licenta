<script setup>
import { RouterLink } from 'vue-router'
import BaseBadge from '@/components/common/BaseBadge.vue'

defineProps({
  products: { type: Array, default: () => [] },
})
defineEmits(['delete'])
</script>

<template>
  <div class="bg-white rounded-xl border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Produs</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">SKU</th>
          <th class="text-left px-4 py-3 font-medium text-gray-600">Categorie</th>
          <th class="text-right px-4 py-3 font-medium text-gray-600">Preț</th>
          <th class="text-right px-4 py-3 font-medium text-gray-600">Stoc</th>
          <th class="text-center px-4 py-3 font-medium text-gray-600">Status</th>
          <th class="text-right px-4 py-3 font-medium text-gray-600">Acțiuni</th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="product in products" :key="product.id" class="hover:bg-gray-50">
          <td class="px-4 py-3">
            <div class="flex items-center gap-3">
              <img
                v-if="product.image"
                :src="product.image"
                class="w-10 h-10 rounded object-contain border"
              />
              <span class="font-medium truncate max-w-[200px]">{{ product.name }}</span>
            </div>
          </td>
          <td class="px-4 py-3 text-gray-500">{{ product.sku }}</td>
          <td class="px-4 py-3">{{ product.category_name }}</td>
          <td class="px-4 py-3 text-right font-medium">{{ product.price }} RON</td>
          <td class="px-4 py-3 text-right">{{ product.stock }}</td>
          <td class="px-4 py-3 text-center">
            <BaseBadge :variant="product.is_active ? 'success' : 'neutral'">
              {{ product.is_active ? 'Activ' : 'Inactiv' }}
            </BaseBadge>
          </td>
          <td class="px-4 py-3 text-right space-x-2">
            <RouterLink
              :to="{ name: 'admin-product-edit', params: { slug: product.slug } }"
              class="text-primary-600 hover:underline"
            >Editează</RouterLink>
            <button @click="$emit('delete', product.slug)" class="text-red-600 hover:underline">Șterge</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
