import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      // Forward /api to the FastAPI backend in development so the frontend
      // can use same-origin relative URLs (no hardcoded localhost:8000).
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
