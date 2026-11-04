import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDomainProgress } from '../api/client'
import type { DomainProgress, ExamMode, Provider } from '../types/exam'
import t from '../i18n/es.json'

const providers: Provider[] = ['AWS', 'GCP', 'AZURE']
const providerNames = t.providers as Record<string, string>
const domainNames = t.domains as Record<string, string>

const archCard = {
  id: 'arch' as const,
  label: 'Arquitecturas',
  desc: 'Diseña diagramas de infraestructura cloud',
  icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="3" width="6" height="5" rx="1"/>
    <rect x="16" y="3" width="6" height="5" rx="1"/>
    <rect x="9" y="16" width="6" height="5" rx="1"/>
    <path d="M5 8v4h14V8M12 12v4"/>
  </svg>`,
}

const modes: { id: ExamMode; label: string; desc: string; icon: string }[] = [
  {
    id: 'exam',
    label: t.mode_exam,
    desc: t.mode_exam_desc,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="5" y="2" width="14" height="20" rx="2"/>
      <path d="M9 7h6M9 11h6M9 15h4"/>
      <circle cx="17" cy="17" r="4" fill="var(--base)" stroke="var(--accent)"/>
      <path d="M15.5 17l1 1 2-2" stroke="var(--ok)" stroke-width="1.5"/>
    </svg>`,
  },
  {
    id: 'study',
    label: t.mode_study,
    desc: t.mode_study_desc,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
    </svg>`,
  },
  {
    id: 'review',
    label: t.mode_review,
    desc: t.mode_review_desc,
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>`,
  },
]

export function Home() {
  const [provider, setProvider] = useState<Provider>('AWS')
  const [progress, setProgress] = useState<DomainProgress[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    getDomainProgress(provider)
      .then(setProgress)
      .catch(() => setProgress([]))
  }, [provider])

  const totalCorrect = progress.reduce((s, d) => s + d.correct, 0)
  const totalAnswered = progress.reduce((s, d) => s + d.total, 0)
  const globalPct = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : null

  function go(mode: ExamMode) {
    navigate(`/${mode}?provider=${provider}`)
  }

  return (
    <main className="home">
      <header className="home-header">
        <div className="home-logo-mark">CP</div>
        <h1 className="home-title">{t.app_name}</h1>
        <p className="home-tagline">{t.tagline}</p>
      </header>

      <div className="provider-selector">
        <span className="provider-label">{t.choose_provider}</span>
        <div className="provider-pills">
          {providers.map((p) => (
            <button
              key={p}
              className={`provider-pill${provider === p ? ' active' : ''}`}
              onClick={() => setProvider(p)}
            >
              {providerNames[p]}
            </button>
          ))}
        </div>
      </div>

      {totalAnswered > 0 && (
        <div className="home-stats">
          <div className="home-stat">
            <span className="home-stat-value">{totalAnswered}</span>
            <span className="home-stat-label">respondidas</span>
          </div>
          <div className="home-stat">
            <span className="home-stat-value">{totalCorrect}</span>
            <span className="home-stat-label">correctas</span>
          </div>
          <div className="home-stat">
            <span className="home-stat-value home-stat-pct">{globalPct}%</span>
            <span className="home-stat-label">acierto global</span>
          </div>
          <div className="home-stat-domains">
            {progress.map((d) => (
              <div key={d.domain} className="home-mini-bar" title={domainNames[d.domain]}>
                <div className="home-mini-fill" style={{ height: `${d.pct}%` }} />
                <span className="home-mini-label">{domainNames[d.domain]?.split(' ')[0]}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="home-choose">{t.choose_mode}</p>
      <div className="mode-cards">
        {modes.map((m) => (
          <button key={m.id} className={`mode-card mode-card--${m.id}`} onClick={() => go(m.id)}>
            <div className="mode-card-icon" dangerouslySetInnerHTML={{ __html: m.icon }} />
            <div className="mode-card-body">
              <h2 className="mode-card-title">{m.label}</h2>
              <p className="mode-card-desc">{m.desc}</p>
            </div>
            <span className="mode-card-arrow">→</span>
          </button>
        ))}
        <button
          className="mode-card mode-card--arch"
          onClick={() => navigate(`/arch?provider=${provider}`)}
        >
          <div className="mode-card-icon" dangerouslySetInnerHTML={{ __html: archCard.icon }} />
          <div className="mode-card-body">
            <h2 className="mode-card-title">{archCard.label}</h2>
            <p className="mode-card-desc">{archCard.desc}</p>
          </div>
          <span className="mode-card-arrow">→</span>
        </button>
      </div>

      <button
        className="home-stats-link"
        onClick={() => navigate(`/stats?provider=${provider}`)}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
        Ver mis estadísticas
      </button>
    </main>
  )
}
