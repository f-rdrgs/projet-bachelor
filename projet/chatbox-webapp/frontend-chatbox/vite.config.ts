import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server:{
    port:4000,
    host: true,
     headers:{
      'Access-Control-Allow-Origin': `:3000`,
      'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Credentials': true,
     },
    //  proxy: {
    //   '/socket.io': {
    //     target: 'http://127.0.0.1:3000',
    //     ws: true,
    //     changeOrigin: true,
    //     secure: false,
    //   },
    // },
  }
})
