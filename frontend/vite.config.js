import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: true,          // bind to 0.0.0.0 (expose on LAN / tunnels)
    allowedHosts: 'all', // accept requests from any hostname (ngrok, etc.)
  },
})
