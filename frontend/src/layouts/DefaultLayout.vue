<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import CartSidebar from '@/components/cart/CartSidebar.vue'
import CompareBar from '@/components/product/CompareBar.vue'
import {
  ShoppingCartIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()
const products = useProductsStore()

const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const categoryMenuOpen = ref(false)
const searchQuery = ref('')

onMounted(() => {
  products.fetchCategories()
  if (auth.isAuthenticated) {
    cart.fetchCart()
  }
})

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'search', query: { search: searchQuery.value } })
    searchQuery.value = ''
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-white shadow-sm sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <RouterLink to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">AS</span>
            </div>
            <span class="text-xl font-bold text-gray-900 hidden sm:block">AutoShop</span>
          </RouterLink>

          <div class="hidden md:flex items-center space-x-4 flex-1 max-w-2xl mx-8">
            <div class="relative">
              <button
                @click="categoryMenuOpen = !categoryMenuOpen"
                class="flex items-center space-x-1 text-sm font-medium text-gray-700 hover:text-primary-600"
              >
                <span>Categorii</span>
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div
                v-if="categoryMenuOpen"
                @mouseleave="categoryMenuOpen = false"
                class="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border py-2 z-50"
              >
                <template v-for="category in products.categories" :key="category.id">
                  <RouterLink
                    :to="{ name: 'category', params: { slug: category.slug } }"
                    class="block px-4 py-2 text-sm font-medium text-gray-800 hover:bg-primary-50"
                    @click="categoryMenuOpen = false"
                  >
                    {{ category.name }}
                  </RouterLink>
                  <RouterLink
                    v-for="child in category.children"
                    :key="child.id"
                    :to="{ name: 'category', params: { slug: child.slug } }"
                    class="block px-8 py-1.5 text-sm text-gray-600 hover:bg-primary-50"
                    @click="categoryMenuOpen = false"
                  >
                    {{ child.name }}
                  </RouterLink>
                </template>
              </div>
            </div>

            <form @submit.prevent="handleSearch" class="flex-1">
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Caută produse..."
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-primary-500 focus:border-primary-500"
                />
                <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
              </div>
            </form>
          </div>

          <div class="flex items-center space-x-3">
            <button
              @click="cart.isOpen = true"
              class="relative p-2 text-gray-600 hover:text-primary-600"
            >
              <ShoppingCartIcon class="w-6 h-6" />
              <span
                v-if="cart.totalItems > 0"
                class="absolute -top-1 -right-1 w-5 h-5 bg-primary-600 text-white rounded-full text-xs flex items-center justify-center"
              >
                {{ cart.totalItems }}
              </span>
            </button>
            <div class="relative">
              <button
                @click="userMenuOpen = !userMenuOpen"
                class="p-2 text-gray-600 hover:text-primary-600"
              >
                <UserIcon class="w-6 h-6" />
              </button>
              <div
                v-if="userMenuOpen"
                @mouseleave="userMenuOpen = false"
                class="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-lg border py-2 z-50"
              >
                <template v-if="auth.isAuthenticated">
                  <div class="px-4 py-2 text-sm text-gray-500 border-b">
                    {{ auth.user?.first_name || auth.user?.username }}
                  </div>
                  <RouterLink
                    to="/profile"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    @click="userMenuOpen = false"
                  >Profil</RouterLink>
                  <RouterLink
                    to="/orders"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    @click="userMenuOpen = false"
                  >Comenzile Mele</RouterLink>
                  <RouterLink
                    v-if="auth.isAdmin"
                    to="/admin"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    @click="userMenuOpen = false"
                  >Panou Admin</RouterLink>
                  <button
                    @click="auth.logout(); userMenuOpen = false"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50"
                  >Deconectare</button>
                </template>
                <template v-else>
                  <RouterLink
                    to="/login"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    @click="userMenuOpen = false"
                  >Autentificare</RouterLink>
                  <RouterLink
                    to="/register"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    @click="userMenuOpen = false"
                  >Înregistrare</RouterLink>
                </template>
              </div>
            </div>
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 text-gray-600"
            >
              <Bars3Icon v-if="!mobileMenuOpen" class="w-6 h-6" />
              <XMarkIcon v-else class="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
      <div v-if="mobileMenuOpen" class="md:hidden border-t bg-white px-4 py-3 space-y-2">
        <form @submit.prevent="handleSearch">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Caută produse..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </form>
        <RouterLink
          v-for="category in products.categories"
          :key="category.id"
          :to="{ name: 'category', params: { slug: category.slug } }"
          class="block py-2 text-sm text-gray-700"
          @click="mobileMenuOpen = false"
        >
          {{ category.name }}
        </RouterLink>
        <RouterLink to="/wizard" class="block py-2 text-sm text-primary-600 font-medium" @click="mobileMenuOpen = false">
          Asistent Senzori
        </RouterLink>
      </div>
    </header>

    <main class="flex-1">
      <router-view />
    </main>
    <footer class="bg-gray-900 text-gray-300 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-white font-bold text-lg mb-3">AutoShop</h3>
            <p class="text-sm">Magazinul tău complet pentru produse de automatizare: senzori, actuatoare, PLC-uri și plăci de dezvoltare.</p>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-3">Linkuri Rapide</h4>
            <nav class="space-y-2 text-sm">
              <RouterLink to="/" class="block hover:text-white">Acasă</RouterLink>
              <RouterLink to="/wizard" class="block hover:text-white">Sensor Wizard</RouterLink>
              <RouterLink to="/compare" class="block hover:text-white">Compară Produse</RouterLink>
            </nav>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-3">Categorii</h4>
            <nav class="space-y-2 text-sm">
              <RouterLink
                v-for="cat in products.categories"
                :key="cat.id"
                :to="{ name: 'category', params: { slug: cat.slug } }"
                class="block hover:text-white"
              >{{ cat.name }}</RouterLink>
            </nav>
          </div>
        </div>
      </div>
    </footer>
    <CartSidebar />
    <CompareBar />
  </div>
</template>
