import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import path from 'path' // Install via 'npm i -D @types/node' if missing

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        // Removes /api from the front of the URL before forwarding
        rewrite: (path) => path.replace(/^\/api/, ''), 
      },
    },
  },
  resolve: {
    alias: {
      // Force everything to point to your main node_modules copy
      react: path.resolve('./node_modules/react'),
      'react-dom': path.resolve('./node_modules/react-dom'),
    },
  },
})
