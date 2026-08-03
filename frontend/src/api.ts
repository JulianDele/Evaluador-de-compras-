/* Cliente HTTP centralizado con manejo de autenticación */
import axios from 'axios'
import toast from 'react-hot-toast'

const rawUrl = (import.meta.env.VITE_API_URL || '').trim()
const normalizedUrl = rawUrl.replace(/\/+$/, '')
export const API_BASE_URL = normalizedUrl
  ? normalizedUrl.endsWith('/api/v1')
    ? normalizedUrl
    : `${normalizedUrl}/api/v1`
  : '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adjuntar token JWT automáticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Manejo global de errores
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const msg = error.response?.data?.detail || 'Error inesperado. Inténtalo de nuevo.'
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    if (error.response?.status !== 422) {
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return Promise.reject(error)
  }
)

export default api
