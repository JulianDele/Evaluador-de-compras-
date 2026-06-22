/* Enrutamiento principal de la aplicación */
import type { ReactNode } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import MainPage from './pages/MainPage'
import PurchasePage from './pages/PurchasePage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  return user ? <>{children}</> : <Navigate to="/login" replace />
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <>
      {user && <Navbar />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <ProtectedRoute><MainPage /></ProtectedRoute>
        } />
        <Route path="/users/:userId/purchases" element={
          <ProtectedRoute><PurchasePage /></ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
