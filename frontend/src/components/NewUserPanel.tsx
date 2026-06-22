/* Panel para crear un usuario nuevo */
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'
import Modal from './Modal'
import api from '../api'

const schema = z.object({
  name:  z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  email: z.string().email('Ingresa un correo electrónico válido'),
})
type FormData = z.infer<typeof schema>

interface Props {
  onClose: () => void
  onCreated: (userId: number) => void
}

export default function NewUserPanel({ onClose, onCreated }: Props) {
  const [loading, setLoading] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      const res = await api.post<{ id: number }>('/users', data)
      toast.success('Usuario creado correctamente')
      onCreated(res.data.id)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title="Registrar nuevo usuario"
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>Cancelar</button>
          <button className="btn btn-primary" form="new-user-form" type="submit" disabled={loading}>
            {loading ? <><span className="spinner" />Creando...</> : 'Iniciar registro de compras'}
          </button>
        </>
      }
    >
      <form id="new-user-form" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="form-group mb-4" style={{ marginBottom: '1rem' }}>
          <label className="form-label" htmlFor="name">
            Nombre completo <span className="required" aria-hidden>*</span>
          </label>
          <input
            id="name"
            className={`form-input ${errors.name ? 'error' : ''}`}
            placeholder="Ej: Ana García"
            {...register('name')}
            aria-describedby={errors.name ? 'name-error' : undefined}
          />
          {errors.name && (
            <span id="name-error" className="form-error" role="alert">{errors.name.message}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="email">
            Correo electrónico <span className="required" aria-hidden>*</span>
          </label>
          <input
            id="email"
            type="email"
            className={`form-input ${errors.email ? 'error' : ''}`}
            placeholder="Ej: ana@correo.com"
            {...register('email')}
            aria-describedby={errors.email ? 'email-error' : undefined}
          />
          {errors.email && (
            <span id="email-error" className="form-error" role="alert">{errors.email.message}</span>
          )}
        </div>

        <p className="text-xs text-muted mt-4" style={{ marginTop: '1rem' }}>
          ⚠ Los campos marcados con * son obligatorios
        </p>
      </form>
    </Modal>
  )
}
