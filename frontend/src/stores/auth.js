import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(null)
  const refreshToken = ref(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function initAuth() {
    const storedToken = localStorage.getItem('access_token')
    const storedRefresh = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken) {
      accessToken.value = storedToken
      refreshToken.value = storedRefresh
      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
      fetchProfile()
    }
  }

  async function login(credentials) {
    isLoading.value = true
    try {
      const { data } = await authService.login(credentials)
      accessToken.value = data.access
      refreshToken.value = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      await fetchProfile()
      return { success: true }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Autentificare eșuată'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function register(data) {
    isLoading.value = true
    try {
      await authService.register(data)
      return await login({ username: data.username, password: data.password })
    } catch (error) {
      const errors = error.response?.data
      return { success: false, errors }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchProfile() {
    try {
      const { data } = await authService.getProfile()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
    } catch {
    }
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return {
    user, accessToken, refreshToken, isLoading,
    isAuthenticated, isAdmin,
    initAuth, login, register, fetchProfile, logout
  }
})
