<template>
  <div class="max-w-5xl mx-auto px-4 py-8">

    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">My Leave</h1>
      <p class="text-sm text-gray-500 mt-1">Apply for leave and track your applications</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4 mb-8">
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

    <div class="grid grid-cols-3 gap-6">

      <!-- Apply form -->
      <div class="col-span-1">
        <div class="bg-white rounded-lg border border-gray-200 p-5">
          <h2 class="font-semibold text-gray-800 mb-4">Apply for Leave</h2>

          <div v-if="formError" class="mb-3 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
            {{ formError }}
          </div>

          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">
                Leave Type
              </label>
              <select v-model="form.leave_type"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option value="">Select type</option>
                <option>Sick Leave</option>
                <option>Casual Leave</option>
                <option>Annual Leave</option>
                <option>Maternity / Paternity Leave</option>
                <option>Bereavement Leave</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">
                Start Date
              </label>
              <input v-model="form.start_date" type="date"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">
                End Date
              </label>
              <input v-model="form.end_date" type="date"
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1 uppercase tracking-wide">
                Reason
                <span class="text-gray-400 normal-case font-normal">(min. 10 chars)</span>
              </label>
              <textarea v-model="form.reason" rows="3"
                placeholder="Briefly describe the reason..."
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
            </div>

            <button @click="submitLeave" :disabled="submitting"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                     text-white font-medium py-2 rounded-md text-sm transition-colors">
              {{ submitting ? 'Submitting...' : 'Submit Application' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Leave history -->
      <div class="col-span-2">
        <div class="bg-white rounded-lg border border-gray-200">
          <div class="px-5 py-4 border-b border-gray-100">
            <h2 class="font-semibold text-gray-800">Application History</h2>
          </div>

          <div v-if="loading" class="px-5 py-8 text-center text-sm text-gray-400">
            Loading...
          </div>
          <div v-else-if="!leaves.length" class="px-5 py-10 text-center">
            <p class="text-gray-400 text-sm">No applications yet</p>
            <p class="text-gray-300 text-xs mt-1">Submit your first leave request</p>
          </div>
          <div v-else>
            <table class="w-full text-sm">
              <thead>
                <tr class="text-xs text-gray-400 uppercase tracking-wide border-b border-gray-100">
                  <th class="text-left px-5 py-3 font-medium">Type</th>
                  <th class="text-left px-5 py-3 font-medium">Dates</th>
                  <th class="text-left px-5 py-3 font-medium">Days</th>
                  <th class="text-left px-5 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="leave in leaves" :key="leave.id"
                  class="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                  <td class="px-5 py-3 font-medium text-gray-800">{{ leave.leave_type }}</td>
                  <td class="px-5 py-3 text-gray-600">
                    {{ formatDate(leave.start_date) }} → {{ formatDate(leave.end_date) }}
                  </td>
                  <td class="px-5 py-3 text-gray-500">{{ daysBetween(leave.start_date, leave.end_date) }}</td>
                  <td class="px-5 py-3"><StatusBadge :status="leave.status" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
import StatusBadge from '../components/StatusBadge.vue'
import { useToast } from '../composables/useToast'

const { showToast } = useToast()

const leaves     = ref([])
const loading    = ref(false)
const submitting = ref(false)
const formError  = ref('')

const form = reactive({ leave_type: '', start_date: '', end_date: '', reason: '' })

const countByStatus = (status) => leaves.value.filter((l) => l.status === status).length

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
    const { data } = await api.get('/leaves/mine')
    leaves.value = data
  } catch {
    showToast('Failed to load leaves', 'error')
  } finally {
    loading.value = false
  }
}

async function submitLeave() {
  formError.value = ''
  if (!form.leave_type || !form.start_date || !form.end_date || !form.reason.trim()) {
    formError.value = 'All fields are required'
    return
  }
  if (form.reason.trim().length < 10) {
    formError.value = 'Reason must be at least 10 characters'
    return
  }
  if (form.start_date > form.end_date) {
    formError.value = 'Start date cannot be after end date'
    return
  }

  submitting.value = true
  try {
    await api.post('/leaves', { ...form })
    showToast('Leave application submitted!', 'success')
    Object.assign(form, { leave_type: '', start_date: '', end_date: '', reason: '' })
    await fetchLeaves()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Submission failed'
  } finally {
    submitting.value = false
  }
}

onMounted(fetchLeaves)
</script>
