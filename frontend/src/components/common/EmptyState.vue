<script setup>
import { InboxIcon } from '@heroicons/vue/24/outline'

defineProps({
  title: { type: String, default: 'Nimic aici deocamdată' },
  message: { type: String, default: '' },
  actionLabel: { type: String, default: '' },
  actionTo: { type: String, default: '' },
})
</script>

<template>
  <div class="text-center py-16">
    <InboxIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
    <h3 class="text-lg font-medium text-gray-900 mb-1">{{ title }}</h3>
    <p v-if="message" class="text-gray-500 mb-6">{{ message }}</p>
    <RouterLink
      v-if="actionLabel && actionTo"
      :to="actionTo"
      class="btn bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 text-sm rounded-lg"
    >{{ actionLabel }}</RouterLink>
  </div>
</template>
