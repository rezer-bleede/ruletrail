import axios from 'axios'

const stripTrailingSlash = (value: string) =>
  value.endsWith('/') ? value.slice(0, -1) : value

const resolveBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl) {
    return envUrl
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    return `${stripTrailingSlash(window.location.origin)}/api`
  }

  return '/api'
}

const api = axios.create({
  baseURL: resolveBaseUrl()
})

export default api
