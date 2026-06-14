import { ref } from 'vue'

const items = ref([])

export function useSidebarItems() {
  return { items }
}
