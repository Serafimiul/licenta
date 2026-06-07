<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { productService } from '@/services/api'
import { useProductsStore } from '@/stores/products'
import ProductCard from '@/components/product/ProductCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const products = useProductsStore()
const featuredProducts = ref([])

onMounted(async () => {
  await products.fetchCategories()
  try {
    const { data } = await productService.list({ ordering: '-created_at', page_size: 8 })
    featuredProducts.value = data.results || data
  } catch { /* empty */ }
})

const categoryIcons = {
  sensors: '📡',
  actuators: '⚙️',
  controllers: '🖥️',
}
</script>

<template>
  <div>
    <section class="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 class="text-4xl sm:text-5xl font-bold mb-4">Magazin de Produse pentru Automatizări</h1>
        <p class="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
          Senzori, actuatoare, PLC-uri și plăci de dezvoltare pentru proiectele tale de automatizare.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <RouterLink to="/category/sensors">
            <BaseButton variant="outline" size="lg" class="!border-white !text-white hover:!bg-white/10">
              Explorează Catalogul
            </BaseButton>
          </RouterLink>
          <RouterLink to="/wizard">
            <BaseButton size="lg" class="!bg-white !text-primary-700 hover:!bg-primary-50">
              Asistent Senzori
            </BaseButton>
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h2 class="text-2xl font-bold text-center mb-8">Cumpără pe Categorii</h2>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <RouterLink
          v-for="cat in products.categories"
          :key="cat.id"
          :to="{ name: 'category', params: { slug: cat.slug } }"
          class="bg-white rounded-xl border p-8 text-center hover:shadow-lg transition-shadow group"
        >
          <span class="text-4xl mb-4 block">{{ categoryIcons[cat.slug] || '📦' }}</span>
          <h3 class="text-lg font-semibold group-hover:text-primary-600">{{ cat.name }}</h3>
          <p class="text-sm text-gray-500 mt-2">{{ cat.description }}</p>
        </RouterLink>
      </div>
    </section>

    <section class="bg-gray-50 py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold mb-8">Cele Mai Noi Produse</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <ProductCard v-for="product in featuredProducts" :key="product.id" :product="product" />
        </div>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h2 class="text-2xl font-bold text-center mb-10">Cum Funcționează</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="text-center">
          <div class="w-14 h-14 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
          <h3 class="font-semibold mb-2">Răsfoiește și Filtrează</h3>
          <p class="text-sm text-gray-500">Folosește filtre dinamice pentru a găsi exact senzorul sau componenta de care ai nevoie.</p>
        </div>
        <div class="text-center">
          <div class="w-14 h-14 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
          <h3 class="font-semibold mb-2">Compară Specificații</h3>
          <p class="text-sm text-gray-500">Compară până la 4 produse unul lângă altul pentru a găsi cea mai bună potrivire.</p>
        </div>
        <div class="text-center">
          <div class="w-14 h-14 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
          <h3 class="font-semibold mb-2">Comandă și Construiește</h3>
          <p class="text-sm text-gray-500">Adaugă în coș, finalizează comanda și începe proiectul tău de automatizare.</p>
        </div>
      </div>
    </section>

    <section class="bg-primary-50 border-t border-b border-primary-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col md:flex-row items-center justify-between">
        <div>
          <h3 class="text-xl font-bold text-primary-800">Nu știi ce senzor să alegi?</h3>
          <p class="text-primary-600 mt-1">Încearcă asistentul nostru inteligent de selecție senzori.</p>
        </div>
        <RouterLink to="/wizard" class="mt-4 md:mt-0">
          <BaseButton variant="primary" size="lg">Pornește Asistentul</BaseButton>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
