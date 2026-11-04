import type { ExamResult } from '../types/exam'
import t from '../i18n/es.json'

interface Props {
  result: ExamResult
  onRestart: () => void
  onHome: () => void
}

const domainNames = t.domains as Record<string, string>

export function ResultSummary({ result, onRestart, onHome }: Props) {
  const pct = Math.round((result.score / result.total) * 100)
  const scoreLabel = t.correct_of
    .replace('{{score}}', String(result.score))
    .replace('{{total}}', String(result.total))

  return (
    <div className="result-summary">
      <h2 className="result-title">{t.your_score}</h2>
      <div className="result-score">
        <span className="result-pct">{pct}%</span>
        <span className="result-label">{scoreLabel}</span>
      </div>

      <h3 className="result-domains-title">{t.by_domain}</h3>
      <ul className="result-domains">
        {result.by_domain.map((d) => (
          <li key={d.domain} className="result-domain-row">
            <span className="result-domain-name">{domainNames[d.domain] ?? d.domain}</span>
            <span className="result-domain-pct">{d.correct}/{d.total}</span>
            <div className="result-domain-bar">
              <div className="result-domain-fill" style={{ width: `${d.pct}%` }} />
            </div>
          </li>
        ))}
      </ul>

      <div className="result-actions">
        <button className="btn btn--primary" onClick={onRestart}>{t.study_again}</button>
        <button className="btn btn--ghost" onClick={onHome}>{t.back_home}</button>
      </div>
    </div>
  )
}
