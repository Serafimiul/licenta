<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { productService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import AdminProductForm from '@/components/admin/AdminProductForm.vue'

const route = useRoute()
const router = useRouter()
const { showSuccess, showError } = useToast()

const product = ref(null)
const isEdit = ref(false)
const submitting = ref(false)

onMounted(async () => {
  if (route.params.slug) {
    isEdit.value = true
    try {
      const { data } = await productService.detail(route.params.slug)
      product.value = data
    } catch {
      showError('Nu am putut încărca produsul.')
    }
  }
})

async function handleSubmit(formData) {
  submitting.value = true
  try {
    if (isEdit.value) {
      await productService.update(route.params.slug, formData)
      showSuccess('Produs actualizat!')
    } else {
      await productService.create(formData)
      showSuccess('Produs creat!')
    }
    router.push({ name: 'admin-products' })
  } catch (err) {
    const msg = err?.response?.data
      ? JSON.stringify(err.response.data)
      : 'Eroare la salvare.'
    showError(msg)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-6">{{ isEdit ? 'Editare Produs' : 'Produs Nou' }}</h2>
    <div class="bg-white rounded-xl border p-6">
      <AdminProductForm
        :initialData="product"
        :loading="submitting"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>
