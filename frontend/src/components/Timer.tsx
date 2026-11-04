import { useEffect, useRef, useState } from 'react'
import t from '../i18n/es.json'

interface Props {
  seconds: number
  onExpire: () => void
  onTick?: (secondsLeft: number) => void
}

export function Timer({ seconds, onExpire, onTick }: Props) {
  const [remaining, setRemaining] = useState(seconds)
  const onExpireRef = useRef(onExpire)
  const onTickRef = useRef(onTick)
  onExpireRef.current = onExpire
  onTickRef.current = onTick

  useEffect(() => {
    setRemaining(seconds)
  }, [seconds])

  useEffect(() => {
    if (remaining <= 0) {
      onExpireRef.current()
      return
    }
    const id = setTimeout(() => {
      setRemaining((r) => {
        const next = r - 1
        onTickRef.current?.(next)
        return next
      })
    }, 1000)
    return () => clearTimeout(id)
  }, [remaining])

  const mm = String(Math.floor(remaining / 60)).padStart(2, '0')
  const ss = String(remaining % 60).padStart(2, '0')
  const critical = remaining < 60

  return (
    <div className={`timer${critical ? ' timer--critical' : ''}`} aria-live="polite">
      <span className="timer-label">{t.time_left}</span>
      <span className="timer-value">{mm}:{ss}</span>
    </div>
  )
}
