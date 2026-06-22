/* Wizard de importación de archivos — 3 pasos */
import { useState, useRef, DragEvent } from 'react'
import toast from 'react-hot-toast'
import Modal from './Modal'
import api from '../api'
import type { ImportResponse } from '../types'

const REQUIRED_FIELDS = ['nombre', 'producto', 'cantidad', 'fecha', 'precio'] as const
const OPTIONAL_FIELDS = ['hora', 'metodo_pago'] as const
const ALL_FIELDS = [...REQUIRED_FIELDS, ...OPTIONAL_FIELDS]

const FIELD_LABELS: Record<string, string> = {
  nombre: 'Nombre',
  producto: 'Producto',
  cantidad: 'Cantidad',
  fecha: 'Fecha',
  hora: 'Hora',
  precio: 'Precio',
  metodo_pago: 'Método de pago',
}

interface Props {
  onClose: () => void
}

export default function ImportWizard({ onClose }: Props) {
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [file, setFile] = useState<File | null>(null)
  const [anonymize, setAnonymize] = useState(false)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [importData, setImportData] = useState<ImportResponse | null>(null)
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({})
  const [availableColumns, setAvailableColumns] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  // ── Paso 1: seleccionar archivo ──────────────────────────────────────────

  const handleFile = (f: File) => {
    const allowed = ['.xlsx', '.csv', '.pdf']
    const ext = '.' + f.name.split('.').pop()?.toLowerCase()
    if (!allowed.includes(ext)) {
      toast.error('Archivo no válido. Usa .xlsx, .csv o .pdf')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      toast.error('El archivo supera el límite de 10 MB')
      return
    }
    setFile(f)
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault(); setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('anonymize', String(anonymize))
      const { data } = await api.post<ImportResponse>('/imports', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setImportData(data)
      // Inicializar mapeo con la auto-detección del servidor
      const autoMap = (data as any).column_mapping || {}
      setColumnMapping(autoMap)
      // Columnas disponibles del archivo (de la vista previa)
      if (data.preview.length > 0) {
        setAvailableColumns(Object.keys(data.preview[0]))
      }
      setStep(2)
    } finally {
      setLoading(false)
    }
  }

  // ── Paso 2: mapeo y vista previa ─────────────────────────────────────────

  const handleConfirm = async () => {
    if (!importData) return
    setLoading(true)
    try {
      await api.post(`/imports/${importData.import_id}/confirm`)
      setStep(3)
      toast.success(
        `Importación completada: ${importData.validation.valid_rows} filas insertadas, ${importData.validation.error_rows} con errores`
      )
    } finally {
      setLoading(false)
    }
  }

  // ── Indicador de pasos ───────────────────────────────────────────────────

  const StepIndicator = () => (
    <div className="steps" aria-label="Progreso del asistente">
      {[1, 2, 3].map((s) => (
        <div key={s} className="step" style={{ flex: s < 3 ? '1' : undefined }}>
          <div className={`step-circle ${step > s ? 'done' : step === s ? 'active' : 'inactive'}`}
               aria-current={step === s ? 'step' : undefined}>
            {step > s ? '✓' : s}
          </div>
          {s < 3 && <div className={`step-line ${step > s ? 'done' : ''}`} />}
        </div>
      ))}
    </div>
  )

  const stepTitles: Record<number, string> = {
    1: 'Importar datos — Paso 1: Subir archivo',
    2: 'Importar datos — Paso 2: Mapear columnas',
    3: 'Importar datos — Completado',
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <Modal title={stepTitles[step]} onClose={onClose}>
      <StepIndicator />

      {/* ── Paso 1 ── */}
      {step === 1 && (
        <>
          <div
            className={`dropzone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
            aria-label="Zona de arrastre de archivo"
          >
            <div className="dropzone-icon">📂</div>
            {file ? (
              <p style={{ fontWeight: 600 }}>📄 {file.name}</p>
            ) : (
              <>
                <p style={{ fontWeight: 600 }}>Arrastra o selecciona un archivo</p>
                <p className="text-muted text-sm mt-1">.xlsx, .csv o .pdf · Máx. 10 MB</p>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept=".xlsx,.csv,.pdf"
              style={{ display: 'none' }}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
              aria-hidden
            />
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginTop: '1rem',
                          cursor: 'pointer', fontSize: '.875rem' }}>
            <input
              type="checkbox"
              checked={anonymize}
              onChange={(e) => setAnonymize(e.target.checked)}
              aria-label="Anonimizar datos sensibles"
            />
            Anonimizar datos sensibles (correos → hash)
          </label>

          <div className="modal-footer" style={{ marginTop: '1.5rem', paddingTop: '1rem',
                                                  borderTop: '1px solid var(--color-border)' }}>
            <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
            <button className="btn btn-primary" disabled={!file || loading} onClick={handleUpload}>
              {loading ? <><span className="spinner" />Procesando...</> : 'Siguiente ▶'}
            </button>
          </div>
        </>
      )}

      {/* ── Paso 2 ── */}
      {step === 2 && importData && (
        <>
          <p className="text-sm text-muted mb-4" style={{ marginBottom: '1rem' }}>
            Archivo: <strong>{importData.filename}</strong> ({importData.rows_detected} filas detectadas)
          </p>

          <h3 style={{ marginBottom: '.75rem' }}>Mapeo de columnas</h3>
          <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
            {ALL_FIELDS.map((field) => (
              <div key={field} className="form-group">
                <label className="form-label" htmlFor={`col-${field}`}>
                  {FIELD_LABELS[field]}
                  {REQUIRED_FIELDS.includes(field as any) && (
                    <span className="required" aria-hidden> *</span>
                  )}
                </label>
                <select
                  id={`col-${field}`}
                  className="form-select"
                  value={columnMapping[field] || ''}
                  onChange={(e) => setColumnMapping((m) => ({ ...m, [field]: e.target.value }))}
                  aria-label={`Columna para ${FIELD_LABELS[field]}`}
                >
                  <option value="">-- Sin asignar --</option>
                  {availableColumns.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          <h3 style={{ marginBottom: '.75rem' }}>Vista previa (primeras 10 filas)</h3>
          {importData.preview.length > 0 && (
            <div className="table-wrapper" style={{ marginBottom: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
              <table>
                <thead>
                  <tr>{Object.keys(importData.preview[0]).map((k) => <th key={k}>{k}</th>)}</tr>
                </thead>
                <tbody>
                  {importData.preview.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((v, j) => <td key={j}>{String(v ?? '')}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className={`alert ${importData.validation.error_rows > 0 ? 'alert-warning' : 'alert-success'}`}>
            ✅ {importData.validation.valid_rows} filas válidas
            {importData.validation.error_rows > 0 && (
              <> &nbsp;·&nbsp; ⚠ {importData.validation.error_rows} filas con errores</>
            )}
          </div>

          <div className="modal-footer" style={{ marginTop: '1rem', paddingTop: '1rem',
                                                  borderTop: '1px solid var(--color-border)' }}>
            <button className="btn btn-secondary" onClick={() => setStep(1)}>◀ Atrás</button>
            <button
              className="btn btn-primary"
              disabled={loading || importData.validation.valid_rows === 0}
              onClick={handleConfirm}
            >
              {loading ? <><span className="spinner" />Importando...</> : 'Confirmar importación'}
            </button>
          </div>
        </>
      )}

      {/* ── Paso 3 ── */}
      {step === 3 && importData && (
        <div className="text-center" style={{ padding: '1.5rem 0' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>✅</div>
          <h2>Importación completada</h2>
          <p className="text-muted mt-2" style={{ marginTop: '.5rem' }}>
            {importData.validation.valid_rows} filas insertadas
            {importData.validation.error_rows > 0 && `, ${importData.validation.error_rows} con errores`}
          </p>
          {importData.validation.error_rows > 0 && (
            <a
              href={`${import.meta.env.VITE_API_URL}/imports/${importData.import_id}/errors.csv`}
              className="btn btn-ghost mt-4"
              style={{ marginTop: '1rem', display: 'inline-flex' }}
              download
            >
              📥 Descargar reporte de errores
            </a>
          )}
          <div style={{ marginTop: '1.5rem' }}>
            <button className="btn btn-primary" onClick={onClose}>
              Volver a pantalla principal
            </button>
          </div>
        </div>
      )}
    </Modal>
  )
}
