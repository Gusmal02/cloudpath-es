import t from '../i18n/es.json'

interface Props {
  current: number
  total: number
}

export function ProgressBar({ current, total }: Props) {
  const pct = total > 0 ? (current / total) * 100 : 0
  const label = t.question_n_of_m
    .replace('{{n}}', String(current))
    .replace('{{m}}', String(total))

  return (
    <div className="progress-bar-wrap">
      <span className="progress-label">{label}</span>
      <div className="progress-track" role="progressbar" aria-valuenow={current} aria-valuemax={total}>
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
