import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getDomainProgress } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import type { DomainProgress, Provider } from '../types/exam'
import t from '../i18n/es.json'

const domainNames = t.domains as Record<string, string>
const providerNames = t.providers as Record<string, string>
const providers: Provider[] = ['AWS', 'GCP', 'AZURE']

function verdict(pct: number): { label: string; cls: string } {
  if (pct >= 80) return { label: 'Dominado', cls: 'verdict--strong' }
  if (pct >= 60) return { label: 'En progreso', cls: 'verdict--mid' }
  if (pct > 0)   return { label: 'Necesita refuerzo', cls: 'verdict--weak' }
  return { label: 'Sin datos', cls: 'verdict--none' }
}

export function StatsMode() {
  const [params] = useSearchParams()
  const [provider, setProvider] = useState<Provider>((params.get('provider') ?? 'AWS') as Provider)
  const [progress, setProgress] = useState<DomainProgress[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getDomainProgress(provider)
      .then(setProgress)
      .catch(() => setProgress([]))
      .finally(() => setLoading(false))
  }, [provider])

  const totalCorrect = progress.reduce((s, d) => s + d.correct, 0)
  const totalAnswered = progress.reduce((s, d) => s + d.total, 0)
  const globalPct = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : null

  const strong = progress.filter((d) => d.pct >= 80)
  const weak = progress.filter((d) => d.total > 0 && d.pct < 60)
  const untouched = progress.filter((d) => d.total === 0)

  return (
    <>
      <AppHeader title="Mis estadísticas" provider={provider} />
      <main className="stats-page">
        <div className="stats-provider-tabs">
          {providers.map((p) => (
            <button
              key={p}
              className={`stats-tab${provider === p ? ' active' : ''}`}
              onClick={() => setProvider(p)}
            >
              {providerNames[p]}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="loading">{t.loading}</div>
        ) : totalAnswered === 0 ? (
          <div className="stats-empty">
            <p>Aún no tienes datos para <strong>{providerNames[provider]}</strong>.</p>
            <p>Completa algunas preguntas en modo Estudio o Examen para ver tu progreso aquí.</p>
          </div>
        ) : (
          <>
            {/* Global score */}
            <div className="stats-global">
              <div className="stats-global-ring">
                <svg viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="34" fill="none" stroke="var(--border)" strokeWidth="8"/>
                  <circle
                    cx="40" cy="40" r="34" fill="none"
                    stroke="var(--accent)" strokeWidth="8"
                    strokeDasharray={`${(globalPct! / 100) * 213.6} 213.6`}
                    strokeLinecap="round"
                    transform="rotate(-90 40 40)"
                  />
                </svg>
                <div className="stats-global-pct">{globalPct}%</div>
              </div>
              <div className="stats-global-detail">
                <p className="stats-global-label">Acierto global</p>
                <p className="stats-global-sub">{totalCorrect} de {totalAnswered} preguntas correctas</p>
                {globalPct !== null && (
                  <p className={`stats-global-verdict ${globalPct >= 72 ? 'verdict--strong' : globalPct >= 50 ? 'verdict--mid' : 'verdict--weak'}`}>
                    {globalPct >= 72 ? '🎯 Listo para el examen' : globalPct >= 50 ? '📈 Buen avance, sigue practicando' : '💪 Sigue reforzando'}
                  </p>
                )}
              </div>
            </div>

            {/* Domain bars */}
            <h3 className="stats-section-title">Progreso por dominio</h3>
            <div className="stats-domains">
              {progress.map((d) => {
                const v = verdict(d.pct)
                return (
                  <div key={d.domain} className="stats-domain-row">
                    <div className="stats-domain-header">
                      <span className="stats-domain-name">{domainNames[d.domain] ?? d.domain}</span>
                      <span className={`stats-domain-verdict ${v.cls}`}>{v.label}</span>
                    </div>
                    <div className="stats-domain-bar-wrap">
                      <div className="stats-domain-track">
                        <div
                          className={`stats-domain-fill ${d.pct >= 80 ? 'fill--strong' : d.pct >= 60 ? 'fill--mid' : 'fill--weak'}`}
                          style={{ width: `${Math.max(d.pct, d.total > 0 ? 4 : 0)}%` }}
                        />
                      </div>
                      <span className="stats-domain-nums">
                        {d.total > 0 ? `${d.correct}/${d.total} (${Math.round(d.pct)}%)` : '—'}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Insights */}
            {(strong.length > 0 || weak.length > 0 || untouched.length > 0) && (
              <div className="stats-insights">
                {strong.length > 0 && (
                  <div className="stats-insight stats-insight--strong">
                    <span className="stats-insight-icon">✓</span>
                    <div>
                      <p className="stats-insight-title">Temas dominados</p>
                      <p className="stats-insight-body">{strong.map((d) => domainNames[d.domain]).join(', ')}</p>
                    </div>
                  </div>
                )}
                {weak.length > 0 && (
                  <div className="stats-insight stats-insight--weak">
                    <span className="stats-insight-icon">!</span>
                    <div>
                      <p className="stats-insight-title">Necesitan refuerzo</p>
                      <p className="stats-insight-body">{weak.map((d) => domainNames[d.domain]).join(', ')}</p>
                    </div>
                  </div>
                )}
                {untouched.length > 0 && (
                  <div className="stats-insight stats-insight--none">
                    <span className="stats-insight-icon">○</span>
                    <div>
                      <p className="stats-insight-title">Sin explorar todavía</p>
                      <p className="stats-insight-body">{untouched.map((d) => domainNames[d.domain]).join(', ')}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </>
  )
}
