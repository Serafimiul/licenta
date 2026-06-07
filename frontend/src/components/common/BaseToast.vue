<script setup>
import { useToast } from '@/composables/useToast'
import { CheckCircleIcon, XCircleIcon, InformationCircleIcon } from '@heroicons/vue/24/solid'

const { toasts, removeToast } = useToast()

const icons = { success: CheckCircleIcon, error: XCircleIcon, info: InformationCircleIcon }
const colors = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}
</script>

<template>
  <div class="fixed top-4 right-4 z-[100] space-y-2 max-w-sm">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="flex items-center space-x-3 px-4 py-3 rounded-lg border shadow-lg"
        :class="colors[toast.type]"
      >
        <component :is="icons[toast.type]" class="w-5 h-5 flex-shrink-0" />
        <span class="text-sm flex-1">{{ toast.message }}</span>
        <button @click="removeToast(toast.id)" class="opacity-60 hover:opacity-100">&times;</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to { opacity: 0; transform: translateX(100%); }
</style>
