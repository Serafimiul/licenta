<script setup>
import { ref, onMounted, computed } from 'vue'
import { categoryService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseSelect from '@/components/common/BaseSelect.vue'

const { showSuccess, showError } = useToast()

const tree = ref([])
const editing = ref(null)        
const showForm = ref(false)

const form = ref({
  name: '',
  slug: '',
  parent: '',
  description: '',
})

const parentOptions = computed(() => {
  const opts = [{ value: '', label: '— Categorie principală —' }]
  for (const cat of tree.value) {
    opts.push({ value: cat.id, label: cat.name })
    for (const child of cat.children || []) {
      opts.push({ value: child.id, label: `  └ ${child.name}` })
    }
  }
  return opts
})

async function load() {
  try {
    const { data } = await categoryService.getTree()
    tree.value = data
  } catch {
    showError('Nu am putut încărca categoriile.')
  }
}

function startNew() {
  editing.value = null
  form.value = { name: '', slug: '', parent: '', description: '' }
  showForm.value = true
}

function startEdit(cat) {
  editing.value = cat
  form.value = {
    name: cat.name,
    slug: cat.slug,
    parent: cat.parent || '',
    description: cat.description || '',
  }
  showForm.value = true
}

function cancel() {
  showForm.value = false
  editing.value = null
}

async function save() {
  const payload = {
    name: form.value.name,
    slug: form.value.slug || undefined,
    parent: form.value.parent || null,
    description: form.value.description,
  }
  try {
    if (editing.value) {
      await categoryService.update(editing.value.slug, payload)
      showSuccess('Categorie actualizată.')
    } else {
      await categoryService.create(payload)
      showSuccess('Categorie creată.')
    }
    showForm.value = false
    await load()
  } catch (err) {
    const msg = err?.response?.data
      ? JSON.stringify(err.response.data)
      : 'Eroare la salvare.'
    showError(msg)
  }
}

async function remove(cat) {
  if (!window.confirm(`Sigur ștergi categoria "${cat.name}"? Toate produsele asociate vor fi șterse în cascadă.`)) return
  try {
    await categoryService.remove(cat.slug)
    showSuccess('Categorie ștearsă.')
    await load()
  } catch (err) {
    showError(err?.response?.data?.detail || 'Eroare la ștergere.')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold">Categorii</h2>
      <BaseButton variant="primary" @click="startNew">Adaugă Categorie</BaseButton>
    </div>

    <div v-if="showForm" class="bg-white rounded-xl border p-4 mb-6 space-y-3">
      <h3 class="font-semibold">{{ editing ? `Editare: ${editing.name}` : 'Categorie nouă' }}</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <BaseInput v-model="form.name" label="Nume" required />
        <BaseInput v-model="form.slug" label="Slug (opțional)" />
        <BaseSelect v-model="form.parent" label="Categorie părinte" :options="parentOptions" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Descriere</label>
        <textarea v-model="form.description" rows="2" class="input-field w-full border rounded p-2" />
      </div>
      <div class="flex gap-2">
        <BaseButton variant="primary" @click="save">Salvează</BaseButton>
        <BaseButton variant="ghost" @click="cancel">Anulează</BaseButton>
      </div>
    </div>

    <div class="bg-white rounded-xl border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nume</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Slug</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Subcategorii</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Acțiuni</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <template v-for="cat in tree" :key="cat.id">
            <tr class="bg-gray-50">
              <td class="px-4 py-3 font-semibold">{{ cat.name }}</td>
              <td class="px-4 py-3 text-gray-500">{{ cat.slug }}</td>
              <td class="px-4 py-3 text-gray-500">{{ cat.children?.length || 0 }}</td>
              <td class="px-4 py-3 text-right space-x-3">
                <button @click="startEdit(cat)" class="text-primary-600 hover:underline">Editează</button>
                <button @click="remove(cat)" class="text-red-600 hover:underline">Șterge</button>
              </td>
            </tr>
            <tr v-for="child in cat.children" :key="child.id">
              <td class="px-4 py-3 pl-10">{{ child.name }}</td>
              <td class="px-4 py-3 text-gray-500">{{ child.slug }}</td>
              <td class="px-4 py-3 text-gray-500">-</td>
              <td class="px-4 py-3 text-right space-x-3">
                <button @click="startEdit(child)" class="text-primary-600 hover:underline">Editează</button>
                <button @click="remove(child)" class="text-red-600 hover:underline">Șterge</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
