import axios from 'axios'

const DEFAULT_API_BASE_URL = 'http://backend:8100/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || DEFAULT_API_BASE_URL
})

export default api
