<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  CubeIcon,
  TagIcon,
  ClipboardDocumentListIcon,
  HomeIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/outline'

const auth = useAuthStore()

const navItems = [
  { name: 'Panou de Control', to: '/admin', icon: HomeIcon },
  { name: 'Produse', to: '/admin/products', icon: CubeIcon },
  { name: 'Categorii', to: '/admin/categories', icon: TagIcon },
  { name: 'Comenzi', to: '/admin/orders', icon: ClipboardDocumentListIcon },
]
</script>

<template>
  <div class="min-h-screen flex bg-gray-100">
    <aside class="w-64 bg-gray-900 text-white flex flex-col">
      <div class="p-4 border-b border-gray-700">
        <RouterLink to="/admin" class="text-xl font-bold">AutoShop Admin</RouterLink>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
          active-class="!bg-primary-600 !text-white"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.name }}</span>
        </RouterLink>
      </nav>
      <div class="p-4 border-t border-gray-700 space-y-2">
        <RouterLink to="/" class="flex items-center space-x-2 text-sm text-gray-400 hover:text-white">
          <ArrowLeftOnRectangleIcon class="w-4 h-4" />
          <span>Înapoi la Magazin</span>
        </RouterLink>
      </div>
    </aside>

    <div class="flex-1 flex flex-col">
      <header class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <h1 class="text-lg font-semibold text-gray-800">Panou Admin</h1>
        <span class="text-sm text-gray-500">{{ auth.user?.email }}</span>
      </header>
      <main class="flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
