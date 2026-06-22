/* Página de login */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../contexts/AuthContext'

const schema = z.object({
  email:    z.string().email('Correo electrónico inválido'),
  password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [serverError, setServerError] = useState('')

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    setServerError('')
    try {
      await login(data.email, data.password)
      navigate('/')
    } catch (err: any) {
      setServerError(err.response?.data?.detail || 'Credenciales incorrectas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ display: 'flex', alignItems: 'center', justifyContent: 'center',
                   minHeight: '100vh', background: 'var(--color-bg)' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '2.5rem' }}>🛒</div>
          <h1 style={{ marginTop: '.5rem' }}>Consumo Estratégico</h1>
          <p className="text-muted text-sm mt-1">Inicia sesión para continuar</p>
        </div>

        {serverError && (
          <div className="alert alert-error" role="alert">{serverError}</div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="form-group mb-4" style={{ marginBottom: '1rem' }}>
            <label className="form-label" htmlFor="email">Correo electrónico</label>
            <input
              id="email" type="email" autoComplete="username"
              className={`form-input ${errors.email ? 'error' : ''}`}
              placeholder="admin@consumo.local"
              {...register('email')}
            />
            {errors.email && <span className="form-error" role="alert">{errors.email.message}</span>}
          </div>

          <div className="form-group mb-4" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label" htmlFor="password">Contraseña</label>
            <input
              id="password" type="password" autoComplete="current-password"
              className={`form-input ${errors.password ? 'error' : ''}`}
              {...register('password')}
            />
            {errors.password && <span className="form-error" role="alert">{errors.password.message}</span>}
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? <><span className="spinner" />Ingresando...</> : 'Iniciar sesión'}
          </button>
        </form>

        
      </div>
    </main>
  )
}
