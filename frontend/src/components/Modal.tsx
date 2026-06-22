/* Modal genérico reutilizable */
import { useEffect } from 'react'

interface ModalProps {
  title: string
  onClose: () => void
  children: React.ReactNode
  footer?: React.ReactNode
}

export default function Modal({ title, onClose, children, footer }: ModalProps) {
  // Cerrar con Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title"
         onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <div className="modal">
        <div className="modal-header">
          <h2 id="modal-title" style={{ fontSize: '1.125rem' }}>{title}</h2>
          <button onClick={onClose} className="btn btn-ghost" aria-label="Cerrar"
                  style={{ padding: '.25rem .5rem', fontSize: '1.25rem', lineHeight: 1 }}>
            ✕
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  )
}
