/* Barra de navegación principal */
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar" role="navigation" aria-label="Navegación principal">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand" aria-label="Consumo Estratégico — inicio">
          🛒 Consumo Estratégico
        </Link>
        {user && (
          <div className="navbar-actions">
            <span className="text-sm text-muted" aria-label={`Usuario: ${user.name}`}>
              👤 {user.name}
            </span>
            <button className="btn btn-ghost" onClick={handleLogout} aria-label="Cerrar sesión">
              Salir
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
