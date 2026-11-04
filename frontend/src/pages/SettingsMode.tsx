import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { generateQuestions } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import type { Provider } from '../types/exam'
import './SettingsMode.css'

const DOMAINS: Record<Provider, string[]> = {
  AWS: ['Cloud Concepts', 'Security', 'Cloud Technology', 'Billing and Pricing'],
  GCP: ['Cloud Concepts', 'Storage', 'Compute', 'Networking', 'Security'],
  AZURE: ['Cloud Concepts', 'Core Services', 'Security', 'Pricing and Support'],
}

function getAiEnabled(): boolean {
  try { return localStorage.getItem('cloudpath_ai_questions') === 'true' } catch { return false }
}
function setAiEnabled(v: boolean) {
  try { localStorage.setItem('cloudpath_ai_questions', String(v)) } catch {}
}

export function SettingsMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const navigate = useNavigate()

  const [aiEnabled, setAiEnabledState] = useState(getAiEnabled)
  const [genProvider, setGenProvider] = useState<Provider>(provider)
  const [genDomain, setGenDomain] = useState<string>('')
  const [genCount, setGenCount] = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ ok: boolean; message: string } | null>(null)

  function toggleAi(v: boolean) {
    setAiEnabledState(v)
    setAiEnabled(v)
  }

  async function handleGenerate() {
    setLoading(true)
    setResult(null)
    try {
      const questions = await generateQuestions(genProvider, genDomain || null, genCount)
      const existing = JSON.parse(localStorage.getItem('cloudpath_ai_pool') ?? '[]')
      const merged = [...existing, ...questions]
      localStorage.setItem('cloudpath_ai_pool', JSON.stringify(merged))
      setResult({ ok: true, message: `✓ ${questions.length} preguntas generadas y guardadas en caché local.` })
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        ?? 'Error al conectar con Ollama. Asegúrate de que esté corriendo.'
      setResult({ ok: false, message: msg })
    } finally {
      setLoading(false)
    }
  }

  function handleClearPool() {
    localStorage.removeItem('cloudpath_ai_pool')
    setResult({ ok: true, message: 'Caché de preguntas IA borrado.' })
  }

  const poolSize = (() => {
    try { return JSON.parse(localStorage.getItem('cloudpath_ai_pool') ?? '[]').length } catch { return 0 }
  })()

  return (
    <>
      <AppHeader title="Configuración" provider={provider} />
      <main className="settings-page">
        <button className="settings-back btn btn--ghost btn--sm" onClick={() => navigate(-1)}>← Volver</button>

        <section className="settings-section">
          <h2 className="settings-section-title">Generación de preguntas con IA</h2>
          <p className="settings-desc">
            Usa Ollama (IA local) para generar preguntas de práctica adicionales.
            Requiere que Ollama esté instalado y el modelo <code>llama3.2:3b</code> descargado.
          </p>

          <label className="settings-toggle-row">
            <span>Activar preguntas generadas por IA en modo Estudio</span>
            <button
              role="switch"
              aria-checked={aiEnabled}
              className={`settings-toggle${aiEnabled ? ' settings-toggle--on' : ''}`}
              onClick={() => toggleAi(!aiEnabled)}
            >
              <span className="settings-toggle-thumb" />
            </button>
          </label>

          {aiEnabled && (
            <div className="settings-gen-controls">
              <div className="settings-gen-row">
                <label>Proveedor</label>
                <select value={genProvider} onChange={(e) => setGenProvider(e.target.value as Provider)}>
                  <option value="AWS">AWS</option>
                  <option value="GCP">GCP</option>
                  <option value="AZURE">Azure</option>
                </select>
              </div>
              <div className="settings-gen-row">
                <label>Dominio (opcional)</label>
                <select value={genDomain} onChange={(e) => setGenDomain(e.target.value)}>
                  <option value="">Todos los dominios</option>
                  {DOMAINS[genProvider].map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              <div className="settings-gen-row">
                <label>Cantidad (1–20)</label>
                <input
                  type="number"
                  min={1}
                  max={20}
                  value={genCount}
                  onChange={(e) => setGenCount(Math.min(20, Math.max(1, Number(e.target.value))))}
                />
              </div>

              <div className="settings-gen-actions">
                <button
                  className="btn btn--primary btn--sm"
                  onClick={handleGenerate}
                  disabled={loading}
                >
                  {loading ? 'Generando…' : 'Generar preguntas'}
                </button>
                {poolSize > 0 && (
                  <button className="btn btn--ghost btn--sm" onClick={handleClearPool}>
                    Borrar caché ({poolSize} preguntas)
                  </button>
                )}
              </div>

              {result && (
                <p className={`settings-result${result.ok ? '' : ' settings-result--error'}`}>
                  {result.message}
                </p>
              )}
            </div>
          )}
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Instalar Ollama</h2>
          <p className="settings-desc">
            Ollama corre modelos de IA localmente en tu equipo, sin conexión a Internet.
            Necesario para "Analizar con IA" en el simulador de arquitecturas y para generar preguntas.
          </p>
          <ol className="settings-steps">
            <li>Descarga Ollama desde <a href="https://ollama.com" target="_blank" rel="noreferrer">ollama.com</a></li>
            <li>Instala y abre la aplicación</li>
            <li>En la terminal, ejecuta: <code>ollama pull llama3.2:3b</code></li>
            <li>El modelo pesa ~2 GB y solo se descarga una vez</li>
          </ol>
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Acerca de CloudPath ES</h2>
          <p className="settings-desc">
            Plataforma de código abierto para preparar certificaciones cloud en español.<br />
            Versión 0.1.0 · <a href="https://github.com/Gusmal02/cloudpath-es" target="_blank" rel="noreferrer">GitHub</a>
          </p>
        </section>
      </main>
    </>
  )
}
