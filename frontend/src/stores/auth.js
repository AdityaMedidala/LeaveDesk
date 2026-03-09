// src/stores/auth.js
// Pinia store for authentication state.
// Persists token/role/email to localStorage so state survives page refresh.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  // State — hydrate from localStorage on first load
  const token = ref(localStorage.getItem('token') || null)
  const role  = ref(localStorage.getItem('role')  || null)
  const email = ref(localStorage.getItem('email') || null)

  // Computed
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  async function login(email_, password) {
    // /auth/login expects form-encoded data (OAuth2 spec)
    const form = new URLSearchParams({ username: email_, password })
    const { data } = await api.post('/auth/login', form)

    token.value = data.access_token
    role.value  = data.role
    email.value = email_

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role',  data.role)
    localStorage.setItem('email', email_)

    router.push(data.role === 'employer' ? '/employer' : '/employee')
  }

  async function register(email_, password, role_) {
    await api.post('/auth/register', { email: email_, password, role: role_ })
    await login(email_, password) // auto-login after register
  }

  function logout() {
    token.value = null
    role.value  = null
    email.value = null
    localStorage.clear()
    router.push('/login')
  }

  return { token, role, email, isLoggedIn, login, register, logout }
})
