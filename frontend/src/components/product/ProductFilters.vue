<script setup>
import { ref, watch, onMounted } from 'vue'
import { categoryService, productService } from '@/services/api'

const props = defineProps({
  categorySlug: { type: String, default: '' },
  modelValue: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:modelValue'])

const attributes = ref([])
const platforms = ref([])
const localFilters = ref({ ...props.modelValue })
let debounceTimer = null

onMounted(async () => {
  if (props.categorySlug) {
    await loadAttributes()
  }
  await loadPlatforms()
})

watch(() => props.categorySlug, async () => {
  if (props.categorySlug) await loadAttributes()
})

watch(() => props.modelValue, (val) => {
  localFilters.value = { ...val }
}, { deep: true })

async function loadAttributes() {
  try {
    const { data } = await categoryService.getCategoryAttributes(props.categorySlug)
    attributes.value = data
  } catch {
    attributes.value = []
  }
}

async function loadPlatforms() {
  try {
    const { data } = await productService.getPlatforms()
    platforms.value = data.results || data
  } catch {
    platforms.value = []
  }
}

function updateFilter(key, value) {
  if (value === '' || value === null || value === undefined) {
    delete localFilters.value[key]
  } else {
    localFilters.value[key] = value
  }
  emitDebounced()
}

function emitDebounced() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('update:modelValue', { ...localFilters.value })
  }, 300)
}

function clearAll() {
  localFilters.value = {}
  emit('update:modelValue', {})
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h4 class="text-sm font-semibold text-gray-700 mb-2">Preț (RON)</h4>
      <div class="flex items-center gap-2">
        <input
          type="number"
          placeholder="Min"
          :value="localFilters.price_min || ''"
          @input="updateFilter('price_min', $event.target.value)"
          class="w-full px-2 py-1.5 text-sm border rounded-md"
        />
        <span class="text-gray-400">-</span>
        <input
          type="number"
          placeholder="Max"
          :value="localFilters.price_max || ''"
          @input="updateFilter('price_max', $event.target.value)"
          class="w-full px-2 py-1.5 text-sm border rounded-md"
        />
      </div>
    </div>

    <div v-if="platforms.length">
      <h4 class="text-sm font-semibold text-gray-700 mb-2">Platformă</h4>
      <div class="space-y-1.5">
        <label
          v-for="platform in platforms"
          :key="platform.id"
          class="flex items-center space-x-2 text-sm cursor-pointer"
        >
          <input
            type="radio"
            name="platform"
            :value="platform.slug"
            :checked="localFilters.platform === platform.slug"
            @change="updateFilter('platform', platform.slug)"
            class="text-primary-600"
          />
          <span>{{ platform.name }}</span>
        </label>
        <label class="flex items-center space-x-2 text-sm cursor-pointer text-gray-500">
          <input
            type="radio"
            name="platform"
            value=""
            :checked="!localFilters.platform"
            @change="updateFilter('platform', '')"
            class="text-primary-600"
          />
          <span>Toate platformele</span>
        </label>
      </div>
    </div>

    <div v-for="attr in attributes" :key="attr.id">
      <h4 class="text-sm font-semibold text-gray-700 mb-2">
        {{ attr.name }}
        <span v-if="attr.unit" class="font-normal text-gray-400">({{ attr.unit }})</span>
      </h4>

      <div v-if="['range', 'int', 'float'].includes(attr.data_type)" class="flex items-center gap-2">
        <input
          type="number"
          placeholder="Min"
          :value="localFilters[`attr_${attr.slug}_min`] || ''"
          @input="updateFilter(`attr_${attr.slug}_min`, $event.target.value)"
          class="w-full px-2 py-1.5 text-sm border rounded-md"
        />
        <span class="text-gray-400">-</span>
        <input
          type="number"
          placeholder="Max"
          :value="localFilters[`attr_${attr.slug}_max`] || ''"
          @input="updateFilter(`attr_${attr.slug}_max`, $event.target.value)"
          class="w-full px-2 py-1.5 text-sm border rounded-md"
        />
      </div>

      <div v-else-if="attr.data_type === 'string'">
        <input
          type="text"
          :placeholder="`Filtrează după ${attr.name.toLowerCase()}`"
          :value="localFilters[`attr_${attr.slug}`] || ''"
          @input="updateFilter(`attr_${attr.slug}`, $event.target.value)"
          class="w-full px-2 py-1.5 text-sm border rounded-md"
        />
      </div>

      <div v-else-if="attr.data_type === 'bool'">
        <label class="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            :checked="localFilters[`attr_${attr.slug}`] === 'true'"
            @change="updateFilter(`attr_${attr.slug}`, $event.target.checked ? 'true' : '')"
            class="rounded text-primary-600"
          />
          <span class="text-sm">Da</span>
        </label>
      </div>
    </div>

    <button
      @click="clearAll"
      class="w-full text-sm text-primary-600 hover:text-primary-800 font-medium py-2 border border-primary-200 rounded-lg hover:bg-primary-50"
    >
      Șterge toate filtrele
    </button>
  </div>
</template>
