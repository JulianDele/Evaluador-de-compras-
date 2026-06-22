import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: { borderRadius: '0.5rem', fontSize: '0.9rem' },
          success: { style: { background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#166534' } },
          error:   { style: { background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' } },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
