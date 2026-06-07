<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const auth = useAuthStore()
const { showSuccess, showError } = useToast()

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
})

onMounted(() => {
  if (auth.user) {
    form.value = {
      first_name: auth.user.first_name || '',
      last_name: auth.user.last_name || '',
      email: auth.user.email || '',
      phone: auth.user.phone || '',
    }
  }
})

async function handleUpdate() {
  try {
    await authService.updateProfile(form.value)
    await auth.fetchProfile()
    showSuccess('Profil actualizat cu succes')
  } catch {
    showError('Eroare la actualizarea profilului')
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold mb-6">Profilul Meu</h1>

    <form @submit.prevent="handleUpdate" class="bg-white rounded-xl border p-6 space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <BaseInput v-model="form.first_name" label="Prenume" />
        <BaseInput v-model="form.last_name" label="Nume" />
      </div>
      <BaseInput v-model="form.email" label="Email" type="email" />
      <BaseInput v-model="form.phone" label="Telefon" />

      <BaseButton type="submit" variant="primary">Salvează Modificările</BaseButton>
    </form>
  </div>
</template>
