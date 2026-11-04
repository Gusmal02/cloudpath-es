import { useNavigate } from 'react-router-dom'
import type { Provider } from '../types/exam'
import t from '../i18n/es.json'

const providerNames = t.providers as Record<string, string>

interface Props {
  title: string
  provider?: Provider
  backTo?: string
}

export function AppHeader({ title, provider, backTo = '/' }: Props) {
  const navigate = useNavigate()
  return (
    <header className="app-header">
      <button className="app-header-back" onClick={() => navigate(backTo)} aria-label="Volver">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      <div className="app-header-center">
        <span className="app-header-logo">CloudPath ES</span>
        <span className="app-header-sep">·</span>
        <span className="app-header-title">{title}</span>
      </div>
      {provider && (
        <span className="app-header-provider">{providerNames[provider] ?? provider}</span>
      )}
      <button
        className="app-header-settings"
        onClick={() => { window.location.href = `/settings${provider ? `?provider=${provider}` : ''}` }}
        aria-label="Configuración"
        title="Configuración"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
    </header>
  )
}
