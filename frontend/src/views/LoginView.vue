<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = ref({ username: '', password: '' })
const error = ref('')

async function handleLogin() {
  error.value = ''
  const result = await auth.login(form.value)
  if (result.success) {
    router.push(route.query.redirect || '/')
  } else {
    error.value = result.message
  }
}
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <h1 class="text-2xl font-bold text-center mb-8">Autentificare AutoShop</h1>

      <form @submit.prevent="handleLogin" class="bg-white p-8 rounded-xl shadow-sm border space-y-4">
        <div v-if="error" class="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{{ error }}</div>

        <BaseInput v-model="form.username" label="Nume utilizator" required />
        <BaseInput v-model="form.password" label="Parolă" type="password" required />

        <BaseButton type="submit" variant="primary" class="w-full" :loading="auth.isLoading">
          Autentificare
        </BaseButton>

        <p class="text-center text-sm text-gray-500">
          Nu ai cont?
          <RouterLink to="/register" class="text-primary-600 hover:underline">Înregistrează-te</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>
