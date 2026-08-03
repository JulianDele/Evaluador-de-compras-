/* Componente para mostrar predicciones de compras futuras */
import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell
} from 'recharts'
import toast from 'react-hot-toast'
import api from '../api'

interface PredictedPurchase {
  product: string
  predicted_quantity: number
  predicted_price: number
  predicted_total: number
  predicted_date: string
  frequency_days: number
  confidence: number
  purchase_count: number
  total_spent: number
}

interface RawPredictedPurchase {
  product: string
  predicted_quantity: number | string
  predicted_price: number | string
  predicted_total: number | string
  predicted_date: string
  frequency_days: number | string
  confidence: number | string
  purchase_count: number | string
  total_spent: number | string
}

interface PredictedPurchasesProps {
  userId: number
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316', '#06B6D4', '#84CC16']

export default function PredictedPurchases({ userId }: PredictedPurchasesProps) {
  const [predictions, setPredictions] = useState<PredictedPurchase[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null)

  useEffect(() => {
    const loadPredictions = async () => {
      setLoading(true)
      try {
        const response = await api.get(`/users/${userId}/summary`)
        const rawPredictions: RawPredictedPurchase[] = response.data.predictions || []
        const normalized = rawPredictions.map((p) => ({
          product: p.product,
          predicted_quantity: Number(p.predicted_quantity),
          predicted_price: Number(p.predicted_price),
          predicted_total: Number(p.predicted_total),
          predicted_date: p.predicted_date,
          frequency_days: Number(p.frequency_days),
          confidence: Number(p.confidence),
          purchase_count: Number(p.purchase_count),
          total_spent: Number(p.total_spent),
        }))
        setPredictions(normalized)
      } catch (error) {
        console.error('Error al cargar predicciones:', error)
        toast.error('Error al cargar predicciones')
      } finally {
        setLoading(false)
      }
    }

    loadPredictions()
  }, [userId])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 1rem' }}>
        <div className="spinner" aria-label="Cargando predicciones..." />
      </div>
    )
  }

  if (predictions.length === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '2rem', marginTop: '2rem' }}>
        <p className="text-muted">No hay suficientes datos para hacer predicciones. Continúa registrando compras.</p>
      </div>
    )
  }

  // Preparar datos para gráficos
  const quantityData = predictions.map(p => ({
    name: p.product,
    cantidad: p.predicted_quantity,
    confianza: p.confidence,
  }))

  const priceData = predictions.map(p => ({
    name: p.product,
    precio: p.predicted_price,
    total: p.predicted_total,
  }))

  const frequencyData = predictions.map((p, i) => ({
    product: p.product,
    x: p.frequency_days,
    y: p.confidence,
    z: p.predicted_total,
    color: COLORS[i % COLORS.length],
  }))

  // Tabla de predicciones con estadísticas
  const tableData = predictions.map(p => ({
    ...p,
    predicted_date_formatted: new Date(p.predicted_date).toLocaleDateString('es-ES'),
  }))

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.2rem', fontWeight: 600 }}>
        📊 Predicciones de Compras Futuras
      </h3>

      {/* ── KPI Cards ── */}
      <div className="grid-4" style={{ gap: '1rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#6B7280', marginBottom: '0.5rem' }}>
            Productos Predichos
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>
            {predictions.length}
          </div>
        </div>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#6B7280', marginBottom: '0.5rem' }}>
            Compra Promedio Predicha
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>
            ${(predictions.reduce((sum, p) => sum + p.predicted_total, 0) / predictions.length).toFixed(2)}
          </div>
        </div>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#6B7280', marginBottom: '0.5rem' }}>
            Confianza Promedio
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>
            {Math.round(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length)}%
          </div>
        </div>
        <div className="card" style={{ padding: '1rem' }}>
          <div style={{ fontSize: '0.85rem', color: '#6B7280', marginBottom: '0.5rem' }}>
            Inversión Total Estimada
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 600 }}>
            ${predictions.reduce((sum, p) => sum + p.predicted_total, 0).toFixed(2)}
          </div>
        </div>
      </div>

      {/* ── Gráfico de Cantidades Predichas ── */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <h4 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Cantidades Predichas por Producto</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={quantityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="cantidad" fill="#3B82F6" name="Cantidad (unidades)" />
            <Bar dataKey="confianza" fill="#10B981" name="Confianza (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Gráfico de Precios ── */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <h4 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Precios y Totales Predichos</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={priceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip
              formatter={(value) => {
                const num = Number(value)
                return isNaN(num) ? String(value) : `$${num.toFixed(2)}`
              }}
            />
            <Legend />
            <Bar dataKey="precio" fill="#F59E0B" name="Precio Unitario ($)" />
            <Bar dataKey="total" fill="#EF4444" name="Total Predicho ($)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Scatter: Frecuencia vs Confianza ── */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <h4 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Frecuencia de Compra vs Confianza (tamaño = inversión)</h4>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" name="Días entre compras" />
            <YAxis type="number" dataKey="y" name="Confianza (%)" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Productos" data={frequencyData} fill="#8884d8">
              {frequencyData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* ── Tabla Detallada ── */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <h4 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Detalle de Predicciones</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.9rem',
          }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #E5E7EB', backgroundColor: '#F9FAFB' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: 600 }}>Producto</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Cantidad</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Precio Unit.</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Total Pred.</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Próxima Compra</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Cada (días)</th>
                <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 600 }}>Confianza</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr
                  key={idx}
                  style={{
                    borderBottom: '1px solid #E5E7EB',
                    backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
                    cursor: 'pointer',
                  }}
                  onClick={() => setSelectedProduct(selectedProduct === row.product ? null : row.product)}
                >
                  <td style={{ padding: '0.75rem', fontWeight: 500 }}>{row.product}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>{row.predicted_quantity}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>${row.predicted_price.toFixed(2)}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'center', fontWeight: 500 }}>
                    ${row.predicted_total.toFixed(2)}
                  </td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>{row.predicted_date_formatted}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>{row.frequency_days}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '0.25rem 0.75rem',
                      backgroundColor: row.confidence >= 75 ? '#DCFCE7' : row.confidence >= 50 ? '#FEF3C7' : '#FED7AA',
                      color: row.confidence >= 75 ? '#166534' : row.confidence >= 50 ? '#92400E' : '#B45309',
                      borderRadius: '0.25rem',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                    }}>
                      {row.confidence}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#6B7280' }}>
          💡 La confianza se basa en cuántas veces has comprado ese producto. Más compras = mayor confianza.
        </p>
      </div>

      {/* ── Línea temporal estimada ── */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <h4 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Timeline de Compras Predichas (próximos 30 días)</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart
            data={[
              ...predictions.map(p => ({
                date: new Date(p.predicted_date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
                monto: p.predicted_total,
                product: p.product,
              })),
            ].sort((a, b) => a.date.localeCompare(b.date))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip
              formatter={(value) => {
                const num = Number(value)
                return isNaN(num) ? String(value) : `$${num.toFixed(2)}`
              }}
            />
            <Legend />
            <Line type="monotone" dataKey="monto" stroke="#3B82F6" name="Inversión Estimada ($)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
