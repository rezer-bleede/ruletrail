import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const devBackendUrl = process.env.VITE_DEV_BACKEND_URL || 'http://localhost:8100'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: devBackendUrl,
        changeOrigin: true
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 5173
  }
})
