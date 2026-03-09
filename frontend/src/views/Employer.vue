<template>
  <div class="max-w-5xl mx-auto px-4 py-8">

    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Leave Requests</h1>
      <p class="text-sm text-gray-500 mt-1">Review and action employee leave applications</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="text-2xl font-bold text-gray-900">{{ leaves.length }}</div>
        <div class="text-xs text-gray-500 uppercase tracking-wide mt-1">Total</div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="text-2xl font-bold text-yellow-500">{{ countByStatus('Pending') }}</div>
        <div class="text-xs text-gray-500 uppercase tracking-wide mt-1">Pending</div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="text-2xl font-bold text-green-500">{{ countByStatus('Approved') }}</div>
        <div class="text-xs text-gray-500 uppercase tracking-wide mt-1">Approved</div>
      </div>
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div class="text-2xl font-bold text-red-500">{{ countByStatus('Rejected') }}</div>
        <div class="text-xs text-gray-500 uppercase tracking-wide mt-1">Rejected</div>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-2 mb-4">
      <button v-for="tab in tabs" :key="tab" @click="activeFilter = tab"
        :class="[
          'px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
          activeFilter === tab
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300'
        ]">
        {{ tab }}
        <span class="ml-1 text-xs opacity-70">
          {{ tab === 'All' ? leaves.length : countByStatus(tab) }}
        </span>
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg border border-gray-200">
      <div v-if="loading" class="px-5 py-8 text-center text-sm text-gray-400">Loading...</div>
      <div v-else-if="!filteredLeaves.length" class="px-5 py-10 text-center">
        <p class="text-gray-400 text-sm">No {{ activeFilter === 'All' ? '' : activeFilter.toLowerCase() }} requests</p>
      </div>
      <div v-else>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-xs text-gray-400 uppercase tracking-wide border-b border-gray-100">
              <th class="text-left px-5 py-3 font-medium">Employee</th>
              <th class="text-left px-5 py-3 font-medium">Type</th>
              <th class="text-left px-5 py-3 font-medium">Dates</th>
              <th class="text-left px-5 py-3 font-medium">Days</th>
              <th class="text-left px-5 py-3 font-medium">Reason</th>
              <th class="text-left px-5 py-3 font-medium">Status</th>
              <th class="text-left px-5 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="leave in filteredLeaves" :key="leave.id"
              class="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
              <td class="px-5 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-full bg-blue-100 text-blue-600 text-xs font-bold
                              flex items-center justify-center flex-shrink-0">
                    {{ leave.employee_email?.[0]?.toUpperCase() }}
                  </div>
                  <span class="text-gray-700 text-xs truncate max-w-32">{{ leave.employee_email }}</span>
                </div>
              </td>
              <td class="px-5 py-3 text-gray-700 font-medium">{{ leave.leave_type }}</td>
              <td class="px-5 py-3 text-gray-500 whitespace-nowrap">
                {{ formatDate(leave.start_date) }} → {{ formatDate(leave.end_date) }}
              </td>
              <td class="px-5 py-3 text-gray-400 text-xs">{{ daysBetween(leave.start_date, leave.end_date) }}</td>
              <td class="px-5 py-3 text-gray-500 max-w-40">
                <span class="truncate block" :title="leave.reason">{{ leave.reason }}</span>
              </td>
              <td class="px-5 py-3"><StatusBadge :status="leave.status" /></td>
              <td class="px-5 py-3">
                <div v-if="leave.status === 'Pending'" class="flex gap-2">
                  <button @click="action(leave.id, 'approve')"
                    class="px-3 py-1 bg-green-50 hover:bg-green-100 text-green-700
                           border border-green-200 rounded text-xs font-medium transition-colors">
                    Approve
                  </button>
                  <button @click="action(leave.id, 'reject')"
                    class="px-3 py-1 bg-red-50 hover:bg-red-100 text-red-600
                           border border-red-200 rounded text-xs font-medium transition-colors">
                    Reject
                  </button>
                </div>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import StatusBadge from '../components/StatusBadge.vue'
import { useToast } from '../composables/useToast'

const { showToast } = useToast()

const leaves       = ref([])
const loading      = ref(false)
const activeFilter = ref('All')
const tabs         = ['All', 'Pending', 'Approved', 'Rejected']

const filteredLeaves = computed(() =>
  activeFilter.value === 'All'
    ? leaves.value
    : leaves.value.filter((l) => l.status === activeFilter.value)
)
const countByStatus = (s) => leaves.value.filter((l) => l.status === s).length

function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}
function daysBetween(start, end) {
  if (!start || !end) return '—'
  return `${Math.round((new Date(end) - new Date(start)) / 86400000) + 1}d`
}

async function fetchLeaves() {
  loading.value = true
  try {
    const { data } = await api.get('/leaves')
    leaves.value = data
  } catch {
    showToast('Failed to load requests', 'error')
  } finally {
    loading.value = false
  }
}

async function action(id, type) {
  try {
    await api.patch(`/leaves/${id}/${type}`)
    showToast(`Leave ${type}d successfully`, 'success')
    await fetchLeaves()
  } catch (e) {
    showToast(e.response?.data?.detail || `Failed to ${type}`, 'error')
  }
}

onMounted(fetchLeaves)
</script>
