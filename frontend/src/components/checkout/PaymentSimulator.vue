<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/common/BaseButton.vue'

const emit = defineEmits(['pay'])
const isProcessing = ref(false)

const cardNumber = ref('')
const expiry = ref('')
const cvv = ref('')

async function handlePay() {
  isProcessing.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  isProcessing.value = false
  emit('pay')
}
</script>

<template>
  <div class="space-y-4 mt-6">
    <h3 class="text-lg font-semibold">Plată (Simulată)</h3>
    <p class="text-xs text-gray-500 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2">
      Aceasta este o plată simulată. Nu se vor efectua taxe reale.
    </p>
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1">Număr Card</label>
      <input
        v-model="cardNumber"
        placeholder="4242 4242 4242 4242"
        class="input-field"
      />
    </div>
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Expirare</label>
        <input v-model="expiry" placeholder="12/28" class="input-field" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">CVV</label>
        <input v-model="cvv" placeholder="123" class="input-field" />
      </div>
    </div>
    <BaseButton variant="primary" size="lg" class="w-full" :loading="isProcessing" @click="handlePay">
      {{ isProcessing ? 'Se procesează...' : 'Plătește Acum' }}
    </BaseButton>
  </div>
</template>
