<script setup>
import { ref } from 'vue'

const props = defineProps({
  image: { type: String, default: null },
  name: { type: String, default: '' },
})

const isZoomed = ref(false)
</script>

<template>
  <div class="space-y-4">
    <div
      class="aspect-square bg-gray-50 rounded-xl overflow-hidden flex items-center justify-center border cursor-zoom-in relative"
      @mouseenter="isZoomed = true"
      @mouseleave="isZoomed = false"
    >
      <img
        v-if="image"
        :src="image"
        :alt="name"
        class="max-h-full object-contain transition-transform duration-300"
        :class="{ 'scale-150': isZoomed }"
      />
      <div v-else class="text-gray-300 text-6xl">&#9881;</div>
    </div>
  </div>
</template>
