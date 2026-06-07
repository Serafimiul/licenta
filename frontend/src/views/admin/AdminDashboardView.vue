<script setup>
import { ref, onMounted } from 'vue'
import { productService, orderService } from '@/services/api'
import AdminStatsCards from '@/components/admin/AdminStatsCards.vue'

const stats = ref({ products: 0, orders: 0, revenue: 0, users: 0 })

onMounted(async () => {
  try {
    const [productsRes, ordersRes] = await Promise.all([
      productService.list({ page_size: 1 }),
      orderService.listOrders(),
    ])
    const productCount = productsRes.data.count || (productsRes.data.results || productsRes.data).length
    const orders = ordersRes.data.results || ordersRes.data
    const revenue = orders
      .filter(o => o.status === 'delivered')
      .reduce((sum, o) => sum + parseFloat(o.total), 0)

    stats.value = {
      products: productCount,
      orders: orders.length,
      revenue: revenue.toFixed(0),
      users: '-',
    }
  } catch { /* empty */ }
})
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-6">Panou de Control</h2>
    <AdminStatsCards :stats="stats" />
  </div>
</template>
