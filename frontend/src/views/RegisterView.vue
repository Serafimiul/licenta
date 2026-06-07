<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()
const auth = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  phone: '',
})
const errors = ref({})

async function handleRegister() {
  errors.value = {}
  const result = await auth.register(form.value)
  if (result.success) {
    router.push('/')
  } else {
    errors.value = result.errors || {}
  }
}
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <h1 class="text-2xl font-bold text-center mb-8">Creează un Cont</h1>

      <form @submit.prevent="handleRegister" class="bg-white p-8 rounded-xl shadow-sm border space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.first_name" label="Prenume" :error="errors.first_name?.[0]" />
          <BaseInput v-model="form.last_name" label="Nume" :error="errors.last_name?.[0]" />
        </div>
        <BaseInput v-model="form.username" label="Nume utilizator" :error="errors.username?.[0]" required />
        <BaseInput v-model="form.email" label="Email" type="email" :error="errors.email?.[0]" required />
        <BaseInput v-model="form.phone" label="Telefon" :error="errors.phone?.[0]" />
        <BaseInput v-model="form.password" label="Parolă" type="password" :error="errors.password?.[0]" required />
        <BaseInput v-model="form.password_confirm" label="Confirmă Parola" type="password" :error="errors.password_confirm?.[0]" required />

        <BaseButton type="submit" variant="primary" class="w-full" :loading="auth.isLoading">
          Înregistrare
        </BaseButton>

        <p class="text-center text-sm text-gray-500">
          Ai deja cont?
          <RouterLink to="/login" class="text-primary-600 hover:underline">Autentifică-te</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>
