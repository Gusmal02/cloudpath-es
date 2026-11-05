import { useEffect, useRef, useState } from 'react'
import { chatWithTutor } from '../api/client'
import type { TutorMessage } from '../api/client'
import { useTutorContext } from '../context/TutorContext'
import './TutorPanel.css'

const AI_ENABLED_KEY = 'cloudpath_ai_questions'
const MAX_HISTORY_SENT = 6

function isAiEnabled() {
  try { return localStorage.getItem(AI_ENABLED_KEY) === 'true' } catch { return false }
}

export function TutorPanel() {
  const { tutorCtx, tutorHistory, appendTutorHistory } = useTutorContext()
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [unavailable, setUnavailable] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' })
  }, [tutorHistory, loading])

  if (!isAiEnabled() || tutorCtx.page === null) return null

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg: TutorMessage = { role: 'user', content: text }
    appendTutorHistory(userMsg)
    setInput('')
    setLoading(true)
    setUnavailable(false)

    try {
      const res = await chatWithTutor({
        message: text,
        context: {
          page: tutorCtx.page,
          provider: tutorCtx.provider,
          domain: tutorCtx.domain,
          question_text: tutorCtx.questionText,
          question_options: tutorCtx.questionOptions,
          answered: tutorCtx.answered,
          canvas_services: tutorCtx.canvasServices,
        },
        history: tutorHistory.slice(-MAX_HISTORY_SENT),
      })
      appendTutorHistory({ role: 'assistant', content: res.reply })
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 503) {
        setUnavailable(true)
      } else {
        appendTutorHistory({ role: 'assistant', content: 'Ocurrió un error al contactar al tutor. Intenta de nuevo.' })
      }
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const pageLabel: Record<string, string> = {
    exam: 'Examen',
    study: 'Estudio',
    review: 'Repaso',
    arch: 'Arquitecturas',
  }

  return (
    <>
      <button
        className="tutor-fab"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Cerrar tutor' : 'Abrir tutor'}
        title="Tutor CloudPath"
      >
        {open ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )}
      </button>

      {open && (
        <div className="tutor-panel" role="dialog" aria-label="Tutor virtual">
          <div className="tutor-panel__header">
            Tutor CloudPath
            <span>· {pageLabel[tutorCtx.page ?? ''] ?? tutorCtx.page}</span>
          </div>

          <div className="tutor-panel__messages">
            {tutorHistory.length === 0 && (
              <p className="tutor-msg tutor-msg--thinking">
                Hola, soy tu tutor de certificaciones cloud. Pregúntame cualquier duda sobre los conceptos que estás estudiando.
              </p>
            )}
            {tutorHistory.map((m, i) => (
              <div key={i} className={`tutor-msg tutor-msg--${m.role}`}>
                {m.content}
              </div>
            ))}
            {loading && <div className="tutor-msg tutor-msg--thinking">Pensando…</div>}
            {unavailable && (
              <div className="tutor-unavailable">
                El tutor necesita Ollama activo.<br />
                Instálalo en <strong>ollama.com</strong> y ejecuta:<br />
                <code>ollama pull llama3.2:3b</code>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="tutor-panel__input">
            <textarea
              rows={2}
              placeholder="Escribe tu pregunta… (Enter para enviar)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading}
              maxLength={500}
            />
            <button
              className="tutor-panel__send"
              onClick={handleSend}
              disabled={loading || !input.trim()}
            >
              Enviar
            </button>
          </div>
        </div>
      )}
    </>
  )
}
