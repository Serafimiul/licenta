<script setup>
import { ref, watch, onMounted } from 'vue'
import { categoryService, productService } from '@/services/api'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseSelect from '@/components/common/BaseSelect.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps({
  initialData: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const form = ref({
  name: '',
  price: '',
  stock: 0,
  manufacturer: '',
  sku: '',
  description: '',
  category: '',
  is_active: true,
})

const imageFile = ref(null)
const imagePreview = ref(null)

const attributes = ref([])     
const attrValues = ref({})   
const categories = ref([])     
const categoryMap = ref({})    
const platforms = ref([])
const selectedPlatforms = ref([])

onMounted(async () => {
  await Promise.all([loadCategories(), loadPlatforms()])
  if (props.initialData) hydrateFromInitial(props.initialData)
})

watch(() => props.initialData, (val) => { if (val) hydrateFromInitial(val) })

function hydrateFromInitial(data) {
  form.value = {
    name: data.name ?? '',
    price: data.price ?? '',
    stock: data.stock ?? 0,
    manufacturer: data.manufacturer ?? '',
    sku: data.sku ?? '',
    description: data.description ?? '',
    category: data.category?.id ?? data.category ?? '',
    is_active: data.is_active !== false,
  }
  selectedPlatforms.value = (data.compatible_platforms || []).map(p => p.id)
  imagePreview.value = typeof data.image === 'string' ? data.image : null

  const seed = {}
  for (const a of data.attributes || []) {
    if (a.data_type === 'range') {
      seed[a.slug] = [a.value_min, a.value_max]
    } else if (a.data_type === 'int' || a.data_type === 'float') {
      seed[a.slug] = a.value_number
    } else {
      seed[a.slug] = a.value_string
    }
  }
  attrValues.value = seed
}

async function loadCategories() {
  try {
    const { data } = await categoryService.getTree()
    const flat = []
    for (const cat of data) {
      flat.push({ value: cat.id, label: cat.name })
      categoryMap.value[cat.id] = cat.slug
      for (const child of cat.children || []) {
        flat.push({ value: child.id, label: `  └ ${child.name}` })
        categoryMap.value[child.id] = child.slug
      }
    }
    categories.value = flat
  } catch { /* empty */ }
}

async function loadPlatforms() {
  try {
    const { data } = await productService.getPlatforms()
    platforms.value = data.results || data
  } catch { /* empty */ }
}

watch(() => form.value.category, async (catId) => {
  if (!catId) { attributes.value = []; return }
  const slug = categoryMap.value[catId]
  if (!slug) return
  try {
    const { data } = await categoryService.getCategoryAttributes(slug)
    attributes.value = data
  } catch { /* empty */ }
})

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
}

function handleSubmit() {
  const payload = {
    name: form.value.name,
    price: form.value.price,
    stock: form.value.stock,
    manufacturer: form.value.manufacturer,
    sku: form.value.sku,
    description: form.value.description,
    category: form.value.category,
    is_active: form.value.is_active,
    platforms: selectedPlatforms.value,
    attributes: attrValues.value,
  }
  if (imageFile.value) payload.image = imageFile.value
  emit('submit', payload)
}
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <BaseInput v-model="form.name" label="Nume Produs" required />
      <BaseInput v-model="form.sku" label="SKU" required />
      <BaseInput v-model="form.price" label="Preț (RON)" type="number" required />
      <BaseInput v-model="form.stock" label="Stoc" type="number" required />
      <BaseInput v-model="form.manufacturer" label="Producător" />
      <BaseSelect v-model="form.category" label="Categorie" :options="categories" />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Descriere</label>
      <textarea v-model="form.description" rows="3" class="input-field w-full border rounded p-2" />
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Imagine produs</label>
      <div class="flex items-center gap-4">
        <img
          v-if="imagePreview"
          :src="imagePreview"
          class="w-24 h-24 rounded border object-contain bg-gray-50"
        />
        <input
          type="file"
          accept="image/*"
          @change="onFileChange"
          class="text-sm"
        />
      </div>
      <p class="text-xs text-gray-500 mt-1">
        Lasă gol pentru a păstra imaginea existentă.
      </p>
    </div>

    <div v-if="platforms.length">
      <label class="block text-sm font-medium text-gray-700 mb-2">Platforme Compatibile</label>
      <div class="flex flex-wrap gap-3">
        <label v-for="p in platforms" :key="p.id" class="flex items-center space-x-2 text-sm">
          <input type="checkbox" :value="p.id" v-model="selectedPlatforms" class="rounded text-primary-600" />
          <span>{{ p.name }}</span>
        </label>
      </div>
    </div>

    <div v-if="attributes.length">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">Specificații Tehnice</h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <template v-for="attr in attributes" :key="attr.id">
          <div v-if="attr.data_type === 'range'" class="grid grid-cols-2 gap-2">
            <BaseInput
              :label="`${attr.name} min${attr.unit ? ' (' + attr.unit + ')' : ''}`"
              type="number"
              :modelValue="(attrValues[attr.slug] || [])[0] ?? ''"
              @update:modelValue="(v) => attrValues[attr.slug] = [Number(v), (attrValues[attr.slug] || [])[1] ?? 0]"
            />
            <BaseInput
              :label="`${attr.name} max${attr.unit ? ' (' + attr.unit + ')' : ''}`"
              type="number"
              :modelValue="(attrValues[attr.slug] || [])[1] ?? ''"
              @update:modelValue="(v) => attrValues[attr.slug] = [(attrValues[attr.slug] || [])[0] ?? 0, Number(v)]"
            />
          </div>
          <BaseInput
            v-else
            :label="`${attr.name}${attr.unit ? ' (' + attr.unit + ')' : ''}`"
            v-model="attrValues[attr.slug]"
            :type="['int','float'].includes(attr.data_type) ? 'number' : 'text'"
          />
        </template>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <label class="flex items-center space-x-2">
        <input type="checkbox" v-model="form.is_active" class="rounded text-primary-600" />
        <span class="text-sm">Activ</span>
      </label>
    </div>

    <BaseButton type="submit" variant="primary" size="lg" :loading="loading">
      {{ initialData ? 'Actualizează Produs' : 'Creează Produs' }}
    </BaseButton>
  </form>
</template>
