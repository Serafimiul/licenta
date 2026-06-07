<script setup>
import { ref, computed } from 'vue'
import { productService } from '@/services/api'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const currentStep = ref(0)
const answers = ref({ category: '', environment: '', platform: '', budget: 200 })
const results = ref([])
const loading = ref(false)

const steps = [
  { title: 'Ce dorești să măsori?', key: 'category' },
  { title: 'Care este mediul de utilizare?', key: 'environment' },
  { title: 'Ce platformă vei folosi?', key: 'platform' },
  { title: 'Care este bugetul tău?', key: 'budget' },
]

const categoryOptions = [
  { value: 'temperature-sensors', label: 'Temperatură', icon: '🌡️' },
  { value: 'pressure-sensors', label: 'Presiune', icon: '⏲️' },
  { value: 'motion-sensors', label: 'Mișcare', icon: '📡' },
  { value: 'proximity-sensors', label: 'Distanță', icon: '📏' },
  { value: 'gas-sensors', label: 'Gaz / Calitatea Aerului', icon: '💨' },
]

const environmentOptions = [
  { value: 'indoor', label: 'Interior', icon: '🏠' },
  { value: 'outdoor', label: 'Exterior', icon: '🌳' },
  { value: 'industrial', label: 'Industrial', icon: '🏭' },
  { value: 'underwater', label: 'Subacvatic', icon: '💧' },
]

const platformOptions = [
  { value: 'arduino', label: 'Arduino', icon: '🔵' },
  { value: 'esp32', label: 'ESP32', icon: '📶' },
  { value: 'raspberry-pi', label: 'Raspberry Pi', icon: '🍓' },
  { value: 'plc-siemens', label: 'PLC', icon: '⚙️' },
  { value: '', label: 'Orice / Altele', icon: '🔄' },
]

const totalSteps = computed(() => steps.length)
const isLastStep = computed(() => currentStep.value === totalSteps.value - 1)
const showResults = computed(() => currentStep.value > totalSteps.value - 1)

function selectOption(key, value) {
  answers.value[key] = value
  next()
}

function next() {
  if (isLastStep.value) {
    fetchResults()
    currentStep.value++
  } else {
    currentStep.value++
  }
}

function prev() {
  if (currentStep.value > 0) currentStep.value--
}

function restart() {
  currentStep.value = 0
  answers.value = { category: '', environment: '', platform: '', budget: 200 }
  results.value = []
}

async function fetchResults() {
  loading.value = true
  const params = {
    category: answers.value.category,
    price_max: answers.value.budget,
  }
  if (answers.value.platform) {
    params.platform = answers.value.platform
  }
  try {
    const { data } = await productService.list(params)
    results.value = data.results || data
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="mb-8">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-500">Pasul {{ Math.min(currentStep + 1, totalSteps) }} din {{ totalSteps }}</span>
        <button v-if="showResults" @click="restart" class="text-sm text-primary-600 hover:underline">Începe Din Nou</button>
      </div>
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          class="h-full bg-primary-600 rounded-full transition-all duration-300"
          :style="{ width: `${((Math.min(currentStep + 1, totalSteps)) / totalSteps) * 100}%` }"
        />
      </div>
    </div>

    <div v-if="showResults">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Produse Recomandate</h2>
      <p class="text-gray-600 mb-6">Pe baza cerințelor tale, iată cele mai bune potriviri:</p>
      <LoadingSpinner v-if="loading" />
      <div v-else-if="results.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <ProductCard v-for="product in results" :key="product.id" :product="product" />
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <p>Niciun produs nu corespunde criteriilor tale. Încearcă să ajustezi bugetul sau platforma.</p>
        <BaseButton variant="outline" class="mt-4" @click="restart">Încearcă Din Nou</BaseButton>
      </div>
    </div>

    <div v-else-if="currentStep === 0">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ steps[0].title }}</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <button
          v-for="opt in categoryOptions"
          :key="opt.value"
          @click="selectOption('category', opt.value)"
          class="flex flex-col items-center justify-center p-6 border-2 rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-colors"
          :class="answers.category === opt.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
        >
          <span class="text-3xl mb-2">{{ opt.icon }}</span>
          <span class="text-sm font-medium">{{ opt.label }}</span>
        </button>
      </div>
    </div>

    <div v-else-if="currentStep === 1">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ steps[1].title }}</h2>
      <div class="grid grid-cols-2 gap-4">
        <button
          v-for="opt in environmentOptions"
          :key="opt.value"
          @click="selectOption('environment', opt.value)"
          class="flex flex-col items-center justify-center p-6 border-2 rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-colors"
          :class="answers.environment === opt.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
        >
          <span class="text-3xl mb-2">{{ opt.icon }}</span>
          <span class="text-sm font-medium">{{ opt.label }}</span>
        </button>
      </div>
    </div>

    <div v-else-if="currentStep === 2">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ steps[2].title }}</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <button
          v-for="opt in platformOptions"
          :key="opt.value"
          @click="selectOption('platform', opt.value)"
          class="flex flex-col items-center justify-center p-6 border-2 rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-colors"
          :class="answers.platform === opt.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200'"
        >
          <span class="text-3xl mb-2">{{ opt.icon }}</span>
          <span class="text-sm font-medium">{{ opt.label }}</span>
        </button>
      </div>
    </div>

    <div v-else-if="currentStep === 3">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ steps[3].title }}</h2>
      <div class="text-center space-y-6">
        <p class="text-4xl font-bold text-primary-600">{{ answers.budget }} RON</p>
        <input
          type="range"
          v-model.number="answers.budget"
          min="5"
          max="500"
          step="5"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
        />
        <div class="flex justify-between text-sm text-gray-500">
          <span>5 RON</span>
          <span>500 RON</span>
        </div>
        <BaseButton variant="primary" size="lg" @click="next">Caută Produse</BaseButton>
      </div>
    </div>

    <div v-if="!showResults && currentStep > 0 && currentStep < totalSteps" class="mt-8 flex justify-between">
      <BaseButton variant="outline" @click="prev">Înapoi</BaseButton>
    </div>
  </div>
</template>
