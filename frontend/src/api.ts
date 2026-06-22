/* Cliente HTTP centralizado con manejo de autenticación */
import axios from 'axios'
import toast from 'react-hot-toast'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: BASE_URL })

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
