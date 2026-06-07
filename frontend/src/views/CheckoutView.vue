<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { orderService } from '@/services/api'
import { useToast } from '@/composables/useToast'
import CheckoutForm from '@/components/checkout/CheckoutForm.vue'
import PaymentSimulator from '@/components/checkout/PaymentSimulator.vue'

const router = useRouter()
const cart = useCartStore()
const { showError } = useToast()

const shippingData = ref({
  shipping_name: '',
  shipping_address: '',
  shipping_city: '',
  shipping_zip: '',
  shipping_country: 'Romania',
  notes: '',
})

onMounted(() => cart.fetchCart())

async function handlePay() {
  const { shipping_name, shipping_address, shipping_city, shipping_zip } = shippingData.value
  if (!shipping_name || !shipping_address || !shipping_city || !shipping_zip) {
    showError('Te rugăm să completezi toate câmpurile obligatorii de livrare.')
    return
  }

  try {
    const { data } = await orderService.createOrder(shippingData.value)
    await cart.fetchCart()
    router.push({ name: 'order-success', query: { id: data.id } })
  } catch (error) {
    showError(error.response?.data?.error || 'Eroare la crearea comenzii.')
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold mb-6">Finalizare Comandă</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
      <div>
        <CheckoutForm v-model="shippingData" />
        <PaymentSimulator @pay="handlePay" />
      </div>

      <div class="bg-gray-50 rounded-xl p-6 h-fit sticky top-24">
        <h3 class="text-lg font-semibold mb-4">Sumar Comandă</h3>
        <div class="space-y-3">
          <div
            v-for="item in cart.items"
            :key="item.id"
            class="flex justify-between text-sm"
          >
            <span class="text-gray-600">
              {{ item.product_detail?.name }} &times; {{ item.quantity }}
            </span>
            <span class="font-medium">{{ parseFloat(item.subtotal).toFixed(2) }} RON</span>
          </div>
        </div>
        <div class="border-t mt-4 pt-4 flex justify-between text-lg font-bold">
          <span>Total</span>
          <span class="text-primary-600">{{ cart.totalPrice.toFixed(2) }} RON</span>
        </div>
      </div>
    </div>
  </div>
</template>
