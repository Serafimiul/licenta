<script setup>
defineProps({
  attributes: { type: Array, default: () => [] },
})
</script>

<template>
  <div class="overflow-hidden rounded-lg border">
    <table class="w-full text-sm">
      <tbody>
        <tr
          v-for="(attr, idx) in attributes"
          :key="attr.id"
          :class="idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'"
        >
          <td class="px-4 py-2.5 font-medium text-gray-700 w-1/3">
            {{ attr.name }}
            <span v-if="attr.unit" class="text-gray-400 font-normal">({{ attr.unit }})</span>
          </td>
          <td class="px-4 py-2.5 text-gray-900">{{ attr.display_value }}</td>
        </tr>
      </tbody>
    </table>
    <div v-if="!attributes.length" class="p-4 text-center text-gray-500 text-sm">
      Nicio specificație disponibilă.
    </div>
  </div>
</template>
