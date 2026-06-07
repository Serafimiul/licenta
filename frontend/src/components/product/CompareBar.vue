<script setup>
import { useRouter } from 'vue-router'
import { useCompare } from '@/composables/useCompare'

const router = useRouter()
const { compareList, removeFromCompare, clearCompare } = useCompare()

function openCompare() {
  router.push({ name: 'compare' })
}
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="compareList.length"
      class="fixed bottom-0 inset-x-0 z-40 bg-white border-t shadow-lg"
    >
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <span class="text-sm font-medium text-gray-700 whitespace-nowrap">
            Comparare ({{ compareList.length }}/4)
          </span>
          <div class="flex items-center gap-2 overflow-x-auto">
            <span
              v-for="p in compareList"
              :key="p.id"
              class="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs text-gray-700 whitespace-nowrap"
            >
              {{ p.name }}
              <button class="text-gray-400 hover:text-red-600" @click="removeFromCompare(p.id)">&times;</button>
            </span>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            class="text-sm text-gray-500 hover:text-gray-800 px-3 py-2"
            @click="clearCompare"
          >Golește</button>
          <button
            class="btn bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 text-sm rounded-lg disabled:opacity-50"
            :disabled="compareList.length < 2"
            @click="openCompare"
          >Compară ({{ compareList.length }})</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
