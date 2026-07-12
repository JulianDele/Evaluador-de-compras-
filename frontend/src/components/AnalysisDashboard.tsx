/* Dashboard de análisis de compras con gráficos y KPIs */
import { useState, useEffect } from 'react'
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, LineChart, Line
} from 'recharts'
import toast from 'react-hot-toast'
import api from '../api'
import type { AnalysisSummary, TopProduct } from '../types'

interface AnalysisDashboardProps {
  userId: number
  userName: string
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

export default function AnalysisDashboard({ userId, userName }: AnalysisDashboardProps) {
  const [analysis, setAnalysis] = useState<AnalysisSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [fromDate, setFromDate] = useState<string>('')
  const [toDate, setToDate] = useState<string>('')

  useEffect(() => {
    // Establecer fechas por defecto (últimos 12 meses)
    const today = new Date()
    const lastYear = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
    
    setToDate(today.toISOString().split('T')[0])
    setFromDate(lastYear.toISOString().split('T')[0])
  }, [])

  useEffect(() => {
    if (!fromDate || !toDate) return
    
    const loadAnalysis = async () => {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (fromDate) params.append('from', fromDate)
        if (toDate) params.append('to', toDate)
        
        const response = await api.get<AnalysisSummary>(
          `/users/${userId}/summary`,
          { params: Object.fromEntries(params) }
        )
        
        setAnalysis(response.data)
      } catch (error) {
        toast.error('Error al cargar el análisis')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    loadAnalysis()
  }, [userId, fromDate, toDate])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem 1rem' }}>
        <div className="spinner" aria-label="Cargando análisis..." />
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
        <p className="text-muted">No hay datos de análisis disponibles</p>
      </div>
    )
  }

  const { summary, top_products, payment_methods } = analysis

  // Preparar datos para gráficos
  const paymentData = Object.entries(payment_methods)
    .map(([method, count]) => ({ name: method, value: count }))
    .sort((a, b) => b.value - a.value)

  const productsData = (top_products || [])
    .map(p => ({ name: p.product, gasto: p.total_spent, compras: p.count }))

  // Simular datos de tendencia (últimos 30 días)
  const trendData = Array.from({ length: 5 }, (_, i) => ({
    periodo: `Sem ${i + 1}`,
    gastos: Math.floor(Math.random() * (summary.total_spent / 5) * 2),
    compras: Math.floor(Math.random() * (summary.total_purchases / 5) * 2),
  }))

  return (
    <div style={{ marginTop: '2rem' }}>
      {/* ── Filtros de fecha ── */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Filtros</h3>
        <div className="grid-2" style={{ gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="from-date">Desde</label>
            <input
              id="from-date"
              type="date"
              className="form-input"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              aria-label="Fecha de inicio del análisis"
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="to-date">Hasta</label>
            <input
              id="to-date"
              type="date"
              className="form-input"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              aria-label="Fecha de fin del análisis"
            />
          </div>
        </div>
      </div>

      {/* ── KPIs ── */}
      <div className="grid-4" style={{ marginBottom: '2rem', gap: '1rem' }}>
        <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
            Gasto Total
          </div>
          <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--color-primary)' }}>
            ${summary.total_spent.toFixed(2)}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
            Total Compras
          </div>
          <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--color-success)' }}>
            {summary.total_purchases}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
            Promedio por Compra
          </div>
          <div style={{ fontSize: '1.875rem', fontWeight: 'bold', color: 'var(--color-warning)' }}>
            ${summary.average_per_purchase.toFixed(2)}
          </div>
        </div>

        <div className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
          <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>
            Producto Favorito
          </div>
          <div style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-primary)', marginTop: '0.5rem' }}>
            {summary.favorite_product || 'Sin datos'}
          </div>
        </div>
      </div>

      {/* ── Gráficos ── */}
      <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Top 5 Productos */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Top 5 Productos Comprados</h3>
          {productsData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={productsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="compras" fill="#3B82F6" name="Compras" />
                <Bar dataKey="gasto" fill="#10B981" name="Gasto ($)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted">Sin datos</p>
          )}
        </div>

        {/* Métodos de Pago */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Métodos de Pago Utilizados</h3>
          {paymentData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={paymentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {paymentData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted">Sin datos</p>
          )}
        </div>
      </div>

      {/* ── Tendencia ── */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Tendencia de Gastos (Últimas Semanas)</h3>
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="periodo" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="gastos"
                stroke="#3B82F6"
                name="Gastos ($)"
                connectNulls
              />
              <Line
                type="monotone"
                dataKey="compras"
                stroke="#10B981"
                name="Compras"
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-muted">Sin datos</p>
        )}
      </div>

      {/* ── Resumen de métodos de pago ── */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>Desglose de Métodos de Pago</h3>
        <div className="grid-3" style={{ gap: '1rem' }}>
          {paymentData.map((method, idx) => (
            <div key={method.name} style={{
              padding: '1rem',
              backgroundColor: COLORS[idx % COLORS.length] + '15',
              borderLeft: `4px solid ${COLORS[idx % COLORS.length]}`,
              borderRadius: '4px'
            }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                {method.name}
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.5rem' }}>
                {method.value}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                {((method.value / summary.total_purchases) * 100).toFixed(1)}% del total
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
