import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig(() => ({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
  // Keep dependency discovery inside this restricted Windows workspace while
  // still converting React's CommonJS entry points into browser-safe ESM.
  optimizeDeps: {
    noDiscovery: true,
    include: [
      'react',
      'react/jsx-runtime',
      'react/jsx-dev-runtime',
      'react-dom',
      'react-dom/client',
    ],
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
}))
