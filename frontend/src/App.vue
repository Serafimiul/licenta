<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BaseToast from '@/components/common/BaseToast.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initAuth()
})
</script>

<template>
  <router-view />
  <BaseToast />
</template>
