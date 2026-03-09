<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm w-full max-w-sm p-8">

      <div class="mb-6">
        <h1 class="text-xl font-bold text-gray-900">Create account</h1>
        <p class="text-sm text-gray-500 mt-1">Join LeaveDesk</p>
      </div>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
        {{ error }}
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="you@company.com"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Min. 6 characters"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Role selector -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">I am a</label>
          <div class="grid grid-cols-2 gap-3">
            <button
              @click="role = 'employee'"
              :class="[
                'border rounded-md py-2.5 text-sm font-medium transition-colors',
                role === 'employee'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              ]">
              Employee
            </button>
            <button
              @click="role = 'employer'"
              :class="[
                'border rounded-md py-2.5 text-sm font-medium transition-colors',
                role === 'employer'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              ]">
              Employer
            </button>
          </div>
        </div>

        <button
          @click="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                 text-white font-medium py-2 px-4 rounded-md text-sm transition-colors">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </div>

      <p class="mt-4 text-center text-sm text-gray-500">
        Already have an account?
        <router-link to="/login" class="text-blue-600 hover:underline">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth     = useAuthStore()
const email    = ref('')
const password = ref('')
const role     = ref('employee')
const error    = ref('')
const loading  = ref(false)

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value, role.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
