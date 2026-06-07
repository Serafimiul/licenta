<script setup>
import BaseInput from '@/components/common/BaseInput.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
})
const emit = defineEmits(['update:modelValue'])

function update(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-lg font-semibold">Informații de Livrare</h3>
    <BaseInput
      label="Nume Complet"
      :modelValue="modelValue.shipping_name"
      @update:modelValue="update('shipping_name', $event)"
      placeholder="Ion Popescu"
      required
    />
    <BaseInput
      label="Adresă"
      :modelValue="modelValue.shipping_address"
      @update:modelValue="update('shipping_address', $event)"
      placeholder="Str. Republicii 45, Ap. 12"
      required
    />
    <div class="grid grid-cols-2 gap-4">
      <BaseInput
        label="Oraș"
        :modelValue="modelValue.shipping_city"
        @update:modelValue="update('shipping_city', $event)"
        placeholder="Cluj-Napoca"
        required
      />
      <BaseInput
        label="Cod Poștal"
        :modelValue="modelValue.shipping_zip"
        @update:modelValue="update('shipping_zip', $event)"
        placeholder="400015"
        required
      />
    </div>
    <BaseInput
      label="Țară"
      :modelValue="modelValue.shipping_country"
      @update:modelValue="update('shipping_country', $event)"
      placeholder="Romania"
    />
    <BaseInput
      label="Observații (opțional)"
      :modelValue="modelValue.notes"
      @update:modelValue="update('notes', $event)"
      placeholder="Lăsați la ușă"
    />
  </div>
</template>
