/* Panel de lista de usuarios guardados */
import { useEffect, useState } from 'react'
import Modal from './Modal'
import api from '../api'
import type { UserSummary } from '../types'

interface Props {
  onClose: () => void
  onSelectUser: (userId: number) => void
}

export default function UserListPanel({ onClose, onSelectUser }: Props) {
  const [users, setUsers] = useState<UserSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get<{ data: UserSummary[] }>('/users', { params: { search, limit: 50 } })
      .then((r) => setUsers(r.data.data))
      .finally(() => setLoading(false))
  }, [search])

  return (
    <Modal title="Usuarios registrados" onClose={onClose}>
      <div className="form-group mb-4" style={{ marginBottom: '1rem' }}>
        <input
          className="form-input"
          placeholder="🔍 Buscar usuario..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Buscar usuario"
        />
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="spinner" style={{ margin: '0 auto' }} aria-label="Cargando..." />
        </div>
      ) : users.length === 0 ? (
        <p className="text-muted text-center">No se encontraron usuarios.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '.75rem' }}>
          {users.map((u) => (
            <div
              key={u.id}
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '.875rem 1rem', border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius)', background: 'var(--color-bg)',
              }}
            >
              <div>
                <p style={{ fontWeight: 600 }}>{u.name}</p>
                <p className="text-sm text-muted">{u.email}</p>
                <p className="text-xs text-muted" style={{ marginTop: '.25rem' }}>
                  📦 {u.total_purchases} compras &nbsp;·&nbsp;
                  💰 ${Number(u.total_spent).toFixed(2)}
                </p>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => onSelectUser(u.id)}
                aria-label={`Seleccionar usuario ${u.name}`}
              >
                Seleccionar
              </button>
            </div>
          ))}
        </div>
      )}
    </Modal>
  )
}
