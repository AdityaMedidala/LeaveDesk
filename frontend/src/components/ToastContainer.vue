<template>
  <!-- Fixed to top-right corner, renders above everything via z-50 -->
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'px-4 py-3 rounded-lg shadow-lg text-sm font-medium pointer-events-auto',
          'flex items-center gap-2 min-w-64 max-w-80',
          toast.type === 'success' && 'bg-green-50 border border-green-200 text-green-800',
          toast.type === 'error'   && 'bg-red-50   border border-red-200   text-red-800',
          toast.type === 'info'    && 'bg-blue-50  border border-blue-200  text-blue-800',
        ]">
        <!-- Icon based on type -->
        <span v-if="toast.type === 'success'">✓</span>
        <span v-else-if="toast.type === 'error'">✕</span>
        <span v-else>ℹ</span>
        {{ toast.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'
const { toasts } = useToast()
</script>

<style scoped>
/* Slide in from right, fade out */
.toast-enter-active { transition: all 0.25s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(20px); }
.toast-leave-to     { opacity: 0; transform: translateX(20px); }
</style>
