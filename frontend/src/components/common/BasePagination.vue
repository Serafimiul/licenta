<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalItems: { type: Number, default: 0 },
  perPage: { type: Number, default: 20 },
})
const emit = defineEmits(['page-change'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.perPage))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(totalPages.value, props.currentPage + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})
</script>

<template>
  <nav v-if="totalPages > 1" class="flex items-center justify-center space-x-1 mt-8">
    <button
      :disabled="currentPage <= 1"
      @click="emit('page-change', currentPage - 1)"
      class="px-3 py-2 text-sm rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
    >Anterior</button>
    <button
      v-for="page in visiblePages"
      :key="page"
      @click="emit('page-change', page)"
      class="px-3 py-2 text-sm rounded-lg border"
      :class="page === currentPage ? 'bg-primary-600 text-white border-primary-600' : 'hover:bg-gray-50'"
    >{{ page }}</button>
    <button
      :disabled="currentPage >= totalPages"
      @click="emit('page-change', currentPage + 1)"
      class="px-3 py-2 text-sm rounded-lg border hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
    >Următor</button>
  </nav>
</template>
