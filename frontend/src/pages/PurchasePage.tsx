/* Pantalla de registro de compras */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import toast from 'react-hot-toast'
import api from '../api'
import type { UserDetail, Purchase, PurchaseCreate } from '../types'
import Modal from '../components/Modal'
import AnalysisDashboard from '../components/AnalysisDashboard'

const schema = z.object({
  product:        z.string().min(1, 'Campo requerido'),
  quantity:       z.number().int().positive('Debe ser mayor a 0'),
  price:          z.number().nonnegative('No puede ser negativo'),
  purchase_date:  z.string().min(1, 'Campo requerido'),
  purchase_time:  z.string().min(1, 'Campo requerido'),
  payment_method: z.enum(['Efectivo', 'Tarjeta', 'Transferencia']),
})
type FormData = z.infer<typeof schema>

export default function PurchasePage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()

  const [activeTab, setActiveTab] = useState<'purchases' | 'analysis'>('purchases')
  const [user, setUser]           = useState<UserDetail | null>(null)
  const [purchases, setPurchases] = useState<Purchase[]>([])
  const [loading, setLoading]     = useState(true)
  const [saving, setSaving]       = useState(false)
  const [confirm, setConfirm]     = useState<FormData | null>(null)

  const { register, handleSubmit, watch, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      purchase_date: new Date().toISOString().split('T')[0],
      purchase_time: new Date().toTimeString().slice(0, 5),
      payment_method: 'Efectivo',
      quantity: 1,
      price: 0,
    },
  })

  const quantity = watch('quantity') || 0
  const price    = watch('price')    || 0
  const total    = (Number(quantity) * Number(price)).toFixed(2)

  useEffect(() => {
    if (!userId) return
    Promise.all([
      api.get<UserDetail>(`/users/${userId}`),
      api.get<{ data: Purchase[] }>(`/purchases?user_id=${userId}&limit=5`),
    ]).then(([u, p]) => {
      setUser(u.data)
      setPurchases(p.data.data)
    }).finally(() => setLoading(false))
  }, [userId])

  const onSubmit = (data: FormData) => setConfirm(data)

  const savePurchase = async () => {
    if (!confirm || !userId) return
    setSaving(true)
    try {
      const body: PurchaseCreate = {
        user_id: Number(userId),
        product: confirm.product,
        quantity: confirm.quantity,
        price: confirm.price,
        purchase_date: confirm.purchase_date,
        purchase_time: confirm.purchase_time + ':00',
        payment_method: confirm.payment_method,
      }
      const res = await api.post<Purchase>('/purchases', body)
      toast.success('Compra registrada correctamente')
      setPurchases((prev) => [res.data, ...prev.slice(0, 4)])
      reset({ ...{ purchase_date: body.purchase_date, purchase_time: confirm.purchase_time,
                   payment_method: confirm.payment_method, quantity: 1, price: 0, product: '' } })
      setConfirm(null)
      // Actualizar totales del usuario
      setUser((u) => u ? {
        ...u,
        total_purchases: u.total_purchases + 1,
        total_spent: u.total_spent + Number(total),
      } : u)
    } catch {
      // El interceptor global ya muestra el toast de error
    } finally {
      setSaving(false)
    }
  }

  const exportCSV = async () => {
    try {
      const res = await api.get('/purchases/export/csv', {
        params: { user_id: userId },
        responseType: 'blob',
      })
      const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
      const a = document.createElement('a')
      a.href = url
      a.download = 'compras.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Error al exportar CSV')
    }
  }

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <div className="spinner" aria-label="Cargando..." />
    </div>
  )

  return (
    <main style={{ padding: '2rem 0' }}>
      <div className="container" style={{ maxWidth: '860px' }}>

        {/* ── Encabezado ── */}
        <div className="flex items-center gap-4 mb-4" style={{ marginBottom: '1.5rem' }}>
          <button className="btn btn-ghost" onClick={() => navigate('/')} aria-label="Volver a pantalla principal">
            ◄ Volver
          </button>
          <h1 style={{ fontSize: '1.375rem' }}>
            <span style={{ color: 'var(--color-primary)' }}>{user?.name}</span>
          </h1>
        </div>

        {/* ── Pestañas ── */}
        <div className="card" style={{ marginBottom: '1.5rem', padding: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--color-border)' }}>
            <button
              onClick={() => setActiveTab('purchases')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: activeTab === 'purchases' ? 'var(--color-primary)' : 'transparent',
                color: activeTab === 'purchases' ? 'white' : 'var(--color-text)',
                border: 'none',
                borderRadius: '4px 4px 0 0',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: activeTab === 'purchases' ? '600' : '500',
                transition: 'all 0.2s ease'
              }}
              aria-label="Pestaña de registro de compras"
            >
              📋 Registrar Compra
            </button>
            <button
              onClick={() => setActiveTab('analysis')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: activeTab === 'analysis' ? 'var(--color-primary)' : 'transparent',
                color: activeTab === 'analysis' ? 'white' : 'var(--color-text)',
                border: 'none',
                borderRadius: '4px 4px 0 0',
                cursor: 'pointer',
                fontSize: '0.95rem',
                fontWeight: activeTab === 'analysis' ? '600' : '500',
                transition: 'all 0.2s ease'
              }}
              aria-label="Pestaña de análisis de compras"
            >
              📊 Análisis de Compras
            </button>
          </div>
        </div>

        {/* ── Pestaña: Registrar Compra ── */}
        {activeTab === 'purchases' && (
          <>
        {/* ── Formulario de compra ── */}
        <div className="card mb-4" style={{ marginBottom: '1.5rem' }}>
          <div className="card-title">Datos de la compra</div>
          <form id="purchase-form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="grid-2" style={{ marginBottom: '1rem' }}>
              {/* Usuario (no editable) */}
              <div className="form-group">
                <label className="form-label">Usuario</label>
                <input className="form-input" value={user?.name || ''} disabled
                       aria-label="Usuario (no editable)" />
              </div>
              {/* Método de pago */}
              <div className="form-group">
                <label className="form-label" htmlFor="payment">
                  Método de pago <span className="required" aria-hidden>*</span>
                </label>
                <select id="payment" className="form-select" {...register('payment_method')}>
                  <option>Efectivo</option>
                  <option>Tarjeta</option>
                  <option>Transferencia</option>
                </select>
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '1rem' }}>
              {/* Producto */}
              <div className="form-group">
                <label className="form-label" htmlFor="product">
                  Producto <span className="required" aria-hidden>*</span>
                </label>
                <input id="product" className={`form-input ${errors.product ? 'error' : ''}`}
                       placeholder="Ej: Leche entera" {...register('product')}
                       aria-describedby={errors.product ? 'product-error' : undefined} />
                {errors.product && <span id="product-error" className="form-error" role="alert">{errors.product.message}</span>}
              </div>
              {/* Cantidad */}
              <div className="form-group">
                <label className="form-label" htmlFor="qty">
                  Cantidad <span className="required" aria-hidden>*</span>
                </label>
                <input id="qty" type="number" min="1" className={`form-input ${errors.quantity ? 'error' : ''}`}
                       {...register('quantity', { valueAsNumber: true })}
                       aria-describedby={errors.quantity ? 'qty-error' : undefined} />
                {errors.quantity && <span id="qty-error" className="form-error" role="alert">{errors.quantity.message}</span>}
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '1rem' }}>
              {/* Precio */}
              <div className="form-group">
                <label className="form-label" htmlFor="price">
                  Precio unitario ($) <span className="required" aria-hidden>*</span>
                </label>
                <input id="price" type="number" min="0" step="0.01"
                       className={`form-input ${errors.price ? 'error' : ''}`}
                       {...register('price', { valueAsNumber: true })}
                       aria-describedby={errors.price ? 'price-error' : undefined} />
                {errors.price && <span id="price-error" className="form-error" role="alert">{errors.price.message}</span>}
              </div>
              {/* Total calculado */}
              <div className="form-group">
                <label className="form-label">Total calculado</label>
                <input className="form-input" value={`$${total}`} disabled
                       aria-label="Total calculado automáticamente" />
              </div>
            </div>

            <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
              {/* Fecha */}
              <div className="form-group">
                <label className="form-label" htmlFor="date">
                  Fecha de compra <span className="required" aria-hidden>*</span>
                </label>
                <input id="date" type="date" className={`form-input ${errors.purchase_date ? 'error' : ''}`}
                       {...register('purchase_date')} />
                {errors.purchase_date && <span className="form-error" role="alert">{errors.purchase_date.message}</span>}
              </div>
              {/* Hora */}
              <div className="form-group">
                <label className="form-label" htmlFor="time">
                  Hora de compra <span className="required" aria-hidden>*</span>
                </label>
                <input id="time" type="time" className={`form-input ${errors.purchase_time ? 'error' : ''}`}
                       {...register('purchase_time')} />
                {errors.purchase_time && <span className="form-error" role="alert">{errors.purchase_time.message}</span>}
              </div>
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">Guardar compra</button>
              <button type="button" className="btn btn-secondary" onClick={exportCSV}>📥 Exportar CSV</button>
            </div>
          </form>
        </div>

        {/* ── Historial reciente ── */}
        <div className="card">
          <div className="card-title">Historial reciente (últimas 5 compras)</div>
          {purchases.length === 0 ? (
            <p className="text-muted">Aún no hay compras registradas.</p>
          ) : (
            <div className="table-wrapper">
              <table aria-label="Historial de compras">
                <thead>
                  <tr>
                    <th>Fecha</th><th>Producto</th><th>Cant.</th><th>Precio</th><th>Total</th><th>Método</th>
                  </tr>
                </thead>
                <tbody>
                  {purchases.map((p) => (
                    <tr key={p.id}>
                      <td>{p.purchase_date}</td>
                      <td>{p.product}</td>
                      <td>{p.quantity}</td>
                      <td>${Number(p.price).toFixed(2)}</td>
                      <td><strong>${Number(p.total).toFixed(2)}</strong></td>
                      <td><span className="badge badge-gray">{p.payment_method}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {user && (
            <div className="flex gap-4 mt-4" style={{ marginTop: '1rem', paddingTop: '1rem',
                                                        borderTop: '1px solid var(--color-border)',
                                                        fontSize: '.875rem' }}>
              <span>💰 Total gastado: <strong>${Number(user.total_spent).toFixed(2)}</strong></span>
              <span>📦 Compras totales: <strong>{user.total_purchases}</strong></span>
            </div>
          )}
        </div>
          </>
        )}

        {/* ── Pestaña: Análisis de Compras ── */}
        {activeTab === 'analysis' && userId && user && (
          <AnalysisDashboard userId={Number(userId)} userName={user.name} />
        )}
      </div>

      {/* ── Modal de confirmación ── */}
      {confirm && (
        <Modal
          title="Confirmar compra"
          onClose={() => setConfirm(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setConfirm(null)} disabled={saving}>
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={savePurchase} disabled={saving}>
                {saving ? <><span className="spinner" />Guardando...</> : '✅ Confirmar'}
              </button>
            </>
          }
        >
          <p style={{ marginBottom: '1rem' }}>Por favor revisa los datos:</p>
          <table style={{ width: '100%', fontSize: '.9rem' }}>
            <tbody>
              {[
                ['Usuario',    user?.name],
                ['Producto',   confirm.product],
                ['Cantidad',   `${confirm.quantity} unidades`],
                ['Precio',     `$${Number(confirm.price).toFixed(2)} c/u`],
                ['Total',      `$${total}`],
                ['Fecha',      `${confirm.purchase_date} ${confirm.purchase_time}`],
                ['Método',     confirm.payment_method],
              ].map(([label, value]) => (
                <tr key={label}>
                  <td style={{ padding: '.375rem 0', color: 'var(--color-secondary)', width: '40%' }}>{label}:</td>
                  <td style={{ padding: '.375rem 0', fontWeight: 500 }}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Modal>
      )}
    </main>
  )
}
