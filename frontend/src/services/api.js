import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        isRefreshing = false
        clearAuth()
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post('/api/auth/refresh/', {
          refresh: refreshToken
        })
        localStorage.setItem('access_token', data.access)
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh)
        }
        processQueue(null, data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        clearAuth()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

function clearAuth() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.push('/login')
}


export const authService = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (data) => api.post('/auth/register/', data),
  getProfile: () => api.get('/auth/me/'),
  updateProfile: (data) => api.put('/auth/me/', data),
}

export const categoryService = {
  getTree: () => api.get('/categories/'),
  getFlat: () => api.get('/categories/flat/'),
  getCategoryAttributes: (slug) => api.get(`/categories/${slug}/attributes/`),
  create: (data) => api.post('/categories/', data),
  update: (slug, data) => api.patch(`/categories/${slug}/`, data),
  remove: (slug) => api.delete(`/categories/${slug}/`),
}

export const productService = {
  list: (params) => api.get('/products/', { params }),
  detail: (slug) => api.get(`/products/${slug}/`),
  compare: (ids) => api.post('/products/compare/', { ids }),
  getRecommendations: (slug) => api.get(`/products/${slug}/recommendations/`),
  getPlatforms: () => api.get('/platforms/'),
  create: (payload) => api.post('/products/', buildProductFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  update: (slug, payload) => api.patch(`/products/${slug}/`, buildProductFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  remove: (slug) => api.delete(`/products/${slug}/`),
}

function buildProductFormData(payload) {
  const fd = new FormData()
  for (const [key, value] of Object.entries(payload)) {
    if (value === undefined || value === null) continue
    if (key === 'image') {
      if (value instanceof File) fd.append('image', value)
      continue
    }
    if (key === 'platforms' && Array.isArray(value)) {
      value.forEach((id) => fd.append('platforms', id))
      continue
    }
    if (key === 'attributes' && typeof value === 'object') {
      fd.append('attributes', JSON.stringify(value))
      continue
    }
    if (typeof value === 'boolean') {
      fd.append(key, value ? 'true' : 'false')
      continue
    }
    fd.append(key, value)
  }
  return fd
}

export const cartService = {
  getCart: () => api.get('/cart/'),
  addItem: (product, quantity = 1) => api.post('/cart/items/', { product, quantity }),
  updateItem: (itemId, quantity) => api.put(`/cart/items/${itemId}/`, { quantity }),
  removeItem: (itemId) => api.delete(`/cart/items/${itemId}/remove/`),
  clearCart: () => api.delete('/cart/clear/'),
}

export const orderService = {
  createOrder: (data) => api.post('/orders/', data),
  listOrders: () => api.get('/orders/'),
  getOrder: (id) => api.get(`/orders/${id}/`),
  updateStatus: (id, statusValue) => api.patch(`/orders/${id}/`, { status: statusValue }),
}

export default api
