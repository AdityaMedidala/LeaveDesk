<template>
  <div class="min-h-screen bg-gray-50">
    <header v-if="auth.isLoggedIn" class="bg-white border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <span class="font-semibold text-gray-800">LeaveDesk</span>
        <div class="flex items-center gap-4 text-sm">
          <span class="text-gray-500">{{ auth.email }}</span>
          <span class="px-2 py-0.5 rounded text-xs font-medium"
            :class="auth.role === 'employer'
              ? 'bg-purple-100 text-purple-700'
              : 'bg-green-100 text-green-700'">
            {{ auth.role }}
          </span>
          <button @click="auth.logout"
            class="text-gray-400 hover:text-red-500 transition-colors text-sm">
            Sign out
          </button>
        </div>
      </div>
    </header>

    <router-view />

    <!-- Toast notifications — rendered at root so they overlay everything -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import ToastContainer from './components/ToastContainer.vue'
const auth = useAuthStore()
</script>
