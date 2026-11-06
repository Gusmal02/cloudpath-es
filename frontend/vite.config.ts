import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vite'

function readBackendPort(): number {
  const portFile = path.resolve(__dirname, '../data/.port')
  try {
    const raw = fs.readFileSync(portFile, 'utf8').trim()
    const parsed = parseInt(raw, 10)
    if (!isNaN(parsed)) return parsed
  } catch {}
  return parseInt(process.env.VITE_API_PORT ?? '8000', 10)
}

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: `http://localhost:${readBackendPort()}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
