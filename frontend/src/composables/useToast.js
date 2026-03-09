// src/composables/useToast.js
// Lightweight toast notification system — no external library needed.
// Usage: const { toasts, showToast } = useToast()
//        showToast('Saved!', 'success')

import { ref } from 'vue'

// Module-level state so toasts are shared across all components
const toasts = ref([])
let nextId = 0

function showToast(message, type = 'success', duration = 3000) {
  const id = nextId++
  toasts.value.push({ id, message, type })

  // Auto-remove after duration
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }, duration)
}

// Single shared instance — composable pattern
export function useToast() {
  return { toasts, showToast }
}
