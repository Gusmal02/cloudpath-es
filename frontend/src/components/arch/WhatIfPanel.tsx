import type { WhatIfResult } from '../../api/client'
import './WhatIfPanel.css'

interface Props {
  result: WhatIfResult | null
  loading: boolean
  error: string | null
  diagramName: string
  provider: string
  onClose: () => void
}

const NIVEL_CLASS: Record<string, string> = {
  bajo: 'whatif-badge--bajo',
  medio: 'whatif-badge--medio',
  alto: 'whatif-badge--alto',
  'muy alto': 'whatif-badge--muy-alto',
}

const SEVERIDAD_CLASS: Record<string, string> = {
  baja: 'whatif-badge--bajo',
  media: 'whatif-badge--medio',
  alta: 'whatif-badge--alto',
  crítica: 'whatif-badge--muy-alto',
}

function exportAsText(result: WhatIfResult, diagramName: string, provider: string): void {
  const ts = new Date().toLocaleString('es-MX')
  const lines: string[] = [
    `Análisis What If — CloudPath ES`,
    `Diagrama: ${diagramName || '(sin nombre)'}`,
    `Proveedor: ${provider}`,
    `Fecha: ${ts}`,
    '',
    '=== COSTO ===',
    `Nivel: ${result.costo.nivel}`,
    `Estimación mensual: ${result.costo.estimacion_mensual}`,
  ]
  if (result.costo.detalle?.length) {
    lines.push('')
    lines.push('Desglose por servicio:')
    for (const d of result.costo.detalle) {
      lines.push(`  - ${d.servicio}: ${d.rango_usd} — ${d.justificacion}`)
    }
  }
  lines.push('')
  lines.push('=== RIESGOS ===')
  if (result.riesgos.length) {
    for (const r of result.riesgos) {
      lines.push(`[${r.severidad.toUpperCase()}] ${r.titulo}`)
      lines.push(`  ${r.descripcion}`)
    }
  } else {
    lines.push('No se detectaron riesgos.')
  }
  lines.push('')
  lines.push('=== SUGERENCIAS ===')
  if (result.sugerencias.length) {
    for (const s of result.sugerencias) {
      lines.push(`[${s.prioridad.toUpperCase()}] ${s.titulo}`)
      lines.push(`  ${s.descripcion}`)
    }
  } else {
    lines.push('Sin sugerencias adicionales.')
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `whatif-${(diagramName || 'diagrama').replace(/\s+/g, '-')}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

export function WhatIfPanel({ result, loading, error, diagramName, provider, onClose }: Props) {
  return (
    <aside className="whatif-panel">
      <div className="whatif-panel__header">
        <span className="whatif-panel__title">Análisis IA ✦</span>
        <button className="whatif-close-btn" onClick={onClose} aria-label="Cerrar panel">✕</button>
      </div>

      {loading && (
        <div className="whatif-loading">
          <div className="whatif-spinner" />
          <span>Analizando arquitectura con IA…</span>
        </div>
      )}

      {error && !loading && (
        <div className="whatif-error">
          <strong>No disponible</strong>
          <p>{error}</p>
        </div>
      )}

      {result && !loading && !error && (
        <>
          {result._parse_error && (
            <div className="whatif-error">
              <strong>Respuesta parcial</strong>
              <p>El modelo no devolvió JSON válido. Intenta de nuevo.</p>
            </div>
          )}

          {/* COSTO */}
          <section className="whatif-section">
            <div className="whatif-section__title">Costo estimado</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <span className={`whatif-badge ${NIVEL_CLASS[result.costo.nivel] ?? ''}`}>
                {result.costo.nivel}
              </span>
              <span className="whatif-cost-summary">{result.costo.estimacion_mensual}</span>
            </div>
            {result.costo.detalle?.length > 0 && (
              <table className="whatif-cost-table">
                <thead>
                  <tr><th>Servicio</th><th>Rango</th></tr>
                </thead>
                <tbody>
                  {result.costo.detalle.map((d, i) => (
                    <tr key={i}>
                      <td>{d.servicio}</td>
                      <td>{d.rango_usd}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          {/* RIESGOS */}
          <section className="whatif-section">
            <div className="whatif-section__title">Riesgos detectados</div>
            {result.riesgos.length === 0 ? (
              <p className="whatif-empty">No se detectaron riesgos.</p>
            ) : (
              result.riesgos.map((r, i) => (
                <div key={i} className="whatif-risk-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.25rem' }}>
                    <span className={`whatif-badge ${SEVERIDAD_CLASS[r.severidad] ?? ''}`}>{r.severidad}</span>
                    <strong className="whatif-card-title">{r.titulo}</strong>
                  </div>
                  <p className="whatif-card-desc">{r.descripcion}</p>
                </div>
              ))
            )}
          </section>

          {/* SUGERENCIAS */}
          <section className="whatif-section">
            <div className="whatif-section__title">Sugerencias</div>
            {result.sugerencias.length === 0 ? (
              <p className="whatif-empty">Sin sugerencias adicionales.</p>
            ) : (
              result.sugerencias.map((s, i) => (
                <div key={i} className="whatif-suggestion-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.25rem' }}>
                    <span className={`whatif-badge ${NIVEL_CLASS[s.prioridad] ?? ''}`}>{s.prioridad}</span>
                    <strong className="whatif-card-title">{s.titulo}</strong>
                  </div>
                  <p className="whatif-card-desc">{s.descripcion}</p>
                </div>
              ))
            )}
          </section>

          <button
            className="btn btn--ghost btn--sm whatif-export-btn"
            onClick={() => exportAsText(result, diagramName, provider)}
          >
            Exportar como .txt
          </button>
        </>
      )}
    </aside>
  )
}
