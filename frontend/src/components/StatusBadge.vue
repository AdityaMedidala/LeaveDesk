<template>
  <span
    :class="badgeClass"
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium">
    <span :class="dotClass" class="w-1.5 h-1.5 rounded-full"></span>
    {{ status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (v) => ['Pending', 'Approved', 'Rejected'].includes(v),
  },
})

const badgeClass = computed(() => ({
  'bg-yellow-50 text-yellow-700 border border-yellow-200': props.status === 'Pending',
  'bg-green-50  text-green-700  border border-green-200':  props.status === 'Approved',
  'bg-red-50    text-red-600    border border-red-200':    props.status === 'Rejected',
}))

const dotClass = computed(() => ({
  'bg-yellow-400': props.status === 'Pending',
  'bg-green-500':  props.status === 'Approved',
  'bg-red-400':    props.status === 'Rejected',
}))
</script>
