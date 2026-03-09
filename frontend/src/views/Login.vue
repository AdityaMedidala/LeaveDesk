<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="bg-white rounded-lg border border-gray-200 shadow-sm w-full max-w-sm p-8">

      <div class="mb-6">
        <h1 class="text-xl font-bold text-gray-900">Sign in</h1>
        <p class="text-sm text-gray-500 mt-1">Welcome back to LeaveDesk</p>
      </div>

      <!-- Error message -->
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
            @keyup.enter="submit"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            @keyup.enter="submit"
            class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button
          @click="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                 text-white font-medium py-2 px-4 rounded-md text-sm transition-colors">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </div>

      <p class="mt-4 text-center text-sm text-gray-500">
        No account?
        <router-link to="/register" class="text-blue-600 hover:underline">
          Create one
        </router-link>
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
const error    = ref('')
const loading  = ref(false)

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please enter your email and password'
    return
  }
  loading.value = true
  try {
    await auth.login(email.value, password.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
