import { ref, watch } from 'vue'

export function useDebounce(source, delay = 300) {
  const debounced = ref(source.value)
  let timeout = null

  watch(source, (val) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      debounced.value = val
    }, delay)
  })

  return debounced
}
