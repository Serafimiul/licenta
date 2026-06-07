import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const routes = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
      { path: 'category/:slug', name: 'category', component: () => import('@/views/CategoryView.vue') },
      { path: 'product/:slug', name: 'product-detail', component: () => import('@/views/ProductDetailView.vue') },
      { path: 'compare', name: 'compare', component: () => import('@/views/CompareView.vue') },
      { path: 'search', name: 'search', component: () => import('@/views/SearchView.vue') },
      { path: 'wizard', name: 'wizard', component: () => import('@/views/WizardView.vue') },
      { path: 'cart', name: 'cart', component: () => import('@/views/CartView.vue'), meta: { requiresAuth: true } },
      { path: 'checkout', name: 'checkout', component: () => import('@/views/CheckoutView.vue'), meta: { requiresAuth: true } },
      { path: 'checkout/success', name: 'order-success', component: () => import('@/views/OrderSuccessView.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
      { path: 'orders', name: 'orders', component: () => import('@/views/OrdersView.vue'), meta: { requiresAuth: true } },
      { path: 'orders/:id', name: 'order-detail', component: () => import('@/views/OrderDetailView.vue'), meta: { requiresAuth: true } },
      { path: 'login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { redirectIfAuth: true } },
      { path: 'register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { redirectIfAuth: true } },
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: () => import('@/views/admin/AdminDashboardView.vue') },
      { path: 'products', name: 'admin-products', component: () => import('@/views/admin/AdminProductsView.vue') },
      { path: 'products/new', name: 'admin-product-new', component: () => import('@/views/admin/AdminProductFormView.vue') },
      { path: 'products/:slug', name: 'admin-product-edit', component: () => import('@/views/admin/AdminProductFormView.vue') },
      { path: 'categories', name: 'admin-categories', component: () => import('@/views/admin/AdminCategoriesView.vue') },
      { path: 'orders', name: 'admin-orders', component: () => import('@/views/admin/AdminOrdersView.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && (!auth.isAuthenticated || !auth.isAdmin)) {
    return { name: 'home' }
  }
  if (to.meta.redirectIfAuth && auth.isAuthenticated) {
    return { name: 'home' }
  }
})

export default router
