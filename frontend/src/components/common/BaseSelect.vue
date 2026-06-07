<script setup>
defineProps({
  label: { type: String, default: '' },
  options: { type: Array, default: () => [] }, 
  modelValue: { type: [String, Number], default: '' },
  placeholder: { type: String, default: 'Selectează...' },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <div>
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="input-field"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>
