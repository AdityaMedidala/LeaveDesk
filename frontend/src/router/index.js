// src/router/index.js
// Vue Router with role-based navigation guards.
// If a route has a `role` meta field, we check localStorage before allowing access.

import { createRouter, createWebHistory } from 'vue-router'
import Login    from '../views/Login.vue'
import Register from '../views/Register.vue'
import Employee from '../views/Employee.vue'
import Employer from '../views/Employer.vue'

const routes = [
  { path: '/',          redirect: '/login' },
  { path: '/login',     component: Login },
  { path: '/register',  component: Register },
  { path: '/employee',  component: Employee, meta: { role: 'employee' } },
  { path: '/employer',  component: Employer, meta: { role: 'employer' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard — runs before every route change
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role  = localStorage.getItem('role')

  // Route requires a specific role
  if (to.meta.role) {
    if (!token)               return '/login'   // not logged in
    if (role !== to.meta.role) return '/login'  // wrong role
  }
})

export default router
