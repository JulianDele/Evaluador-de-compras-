/* Pantalla Principal — Selecciona una opción */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import UserListPanel from '../components/UserListPanel'
import NewUserPanel from '../components/NewUserPanel'
import ImportWizard from '../components/ImportWizard'

type ActivePanel = null | 'users' | 'new-user' | 'import'

export default function MainPage() {
  const [active, setActive] = useState<ActivePanel>(null)
  const navigate = useNavigate()

  const cards = [
    {
      id: 'users' as const,
      icon: '👥',
      title: 'Usuarios guardados',
      description: 'Ver y gestionar usuarios ya registrados en el sistema',
      btnLabel: 'Ver usuarios',
    },
    {
      id: 'new-user' as const,
      icon: '➕',
      title: 'Usuario nuevo',
      description: 'Registrar un nuevo usuario para analizar sus compras',
      btnLabel: 'Crear usuario',
    },
    {
      id: 'import' as const,
      icon: '📂',
      title: 'Importar datos',
      description: 'Subir un archivo .xlsx, .csv o .pdf con datos de compras',
      btnLabel: 'Importar',
    },
  ]

  return (
    <main style={{ padding: '2rem 0', minHeight: '80vh' }}>
      <div className="container">
        <div className="text-center mb-4" style={{ marginBottom: '2rem' }}>
          <h1>Selecciona una opción</h1>
          <p className="text-muted mt-1">Sistema de análisis de patrones de compra</p>
        </div>

        <div className="grid-3">
          {cards.map((card) => (
            <div
              key={card.id}
              className="card"
              style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
              aria-label={card.title}
            >
              <div style={{ fontSize: '2.5rem', textAlign: 'center' }}>{card.icon}</div>
              <div>
                <h2 style={{ textAlign: 'center', marginBottom: '.5rem' }}>{card.title}</h2>
                <p className="text-muted text-sm" style={{ textAlign: 'center' }}>
                  {card.description}
                </p>
              </div>
              <button
                className="btn btn-primary btn-full"
                onClick={() => setActive(card.id)}
                aria-label={card.btnLabel}
              >
                {card.btnLabel}
              </button>
            </div>
          ))}
        </div>

        {/* Paneles / Modales */}
        {active === 'users' && (
          <UserListPanel
            onClose={() => setActive(null)}
            onSelectUser={(userId) => navigate(`/users/${userId}/purchases`)}
          />
        )}
        {active === 'new-user' && (
          <NewUserPanel
            onClose={() => setActive(null)}
            onCreated={(userId) => navigate(`/users/${userId}/purchases`)}
          />
        )}
        {active === 'import' && (
          <ImportWizard onClose={() => setActive(null)} />
        )}
      </div>
    </main>
  )
}
