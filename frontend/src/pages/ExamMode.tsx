import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getResult, startExam, submitAnswer } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { ProgressBar } from '../components/ProgressBar'
import { QuestionCard } from '../components/QuestionCard'
import { ResultSummary } from '../components/ResultSummary'
import { Timer } from '../components/Timer'
import { useTutorContext } from '../context/TutorContext'
import type { ExamResult, ExamSession, Provider } from '../types/exam'
import t from '../i18n/es.json'

const EXAM_SECONDS = 90 * 60

interface SavedExam {
  session: ExamSession
  currentIdx: number
  secondsLeft: number
  provider: Provider
}

function storageKey(provider: string) {
  return `cloudpath_exam_${provider}`
}

function saveExam(provider: string, data: SavedExam) {
  try {
    localStorage.setItem(storageKey(provider), JSON.stringify(data))
  } catch {}
}

function loadExam(provider: string): SavedExam | null {
  try {
    const raw = localStorage.getItem(storageKey(provider))
    return raw ? (JSON.parse(raw) as SavedExam) : null
  } catch {
    return null
  }
}

function clearExam(provider: string) {
  try {
    localStorage.removeItem(storageKey(provider))
  } catch {}
}

export function ExamMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const navigate = useNavigate()
  const { setTutorContext, clearTutorHistory } = useTutorContext()

  const [session, setSession] = useState<ExamSession | null>(null)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [secondsLeft, setSecondsLeft] = useState(EXAM_SECONDS)
  const [selected, setSelected] = useState<number | null>(null)
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [result, setResult] = useState<ExamResult | null>(null)
  const [error, setError] = useState('')
  const [finished, setFinished] = useState(false)
  const [resuming, setResuming] = useState(false)
  const sessionRef = useRef<ExamSession | null>(null)

  useEffect(() => {
    clearTutorHistory()
  }, [provider]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const saved = loadExam(provider)
    if (saved) {
      setResuming(true)
      setSession(saved.session)
      sessionRef.current = saved.session
      setCurrentIdx(saved.currentIdx)
      setSecondsLeft(saved.secondsLeft)
    } else {
      startExam(provider, 30)
        .then((s) => {
          if (s.questions.length < 30) {
            console.warn(`Examen iniciado con ${s.questions.length} preguntas (esperadas 30) para ${provider}`)
          }
          setSession(s)
          sessionRef.current = s
          saveExam(provider, { session: s, currentIdx: 0, secondsLeft: EXAM_SECONDS, provider })
        })
        .catch(() => setError(t.error_load))
    }
  }, [provider])

  // Keep localStorage in sync as the exam progresses
  useEffect(() => {
    if (session && !finished) {
      saveExam(provider, { session, currentIdx, secondsLeft, provider })
    }
  }, [session, currentIdx, secondsLeft, finished, provider])

  async function handleConfirm() {
    if (!session) return
    const q = session.questions[currentIdx]
    const isMulti = (q.num_correct ?? 1) > 1
    const chosen = isMulti ? selectedIndices : (selected !== null ? [selected] : [])
    if (chosen.length === 0) return
    const feedback = await submitAnswer(session.session_id, q.id, chosen)
    setIsCorrect(feedback.is_correct)
    setAnswered(true)
  }

  async function handleNext() {
    if (!session) return
    setResuming(false)
    if (currentIdx + 1 >= session.questions.length) {
      const r = await getResult(session.session_id)
      setResult(r)
      setFinished(true)
      clearExam(provider)
    } else {
      const next = currentIdx + 1
      setCurrentIdx(next)
      setSelected(null)
      setSelectedIndices([])
      setAnswered(false)
    }
  }

  function handleSelect(i: number) {
    const q = session?.questions[currentIdx]
    if (!q) return
    const isMulti = (q.num_correct ?? 1) > 1
    if (isMulti) {
      setSelectedIndices((prev) =>
        prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i]
      )
    } else {
      setSelected(i)
    }
  }

  async function handleExpire() {
    if (!session) return
    const r = await getResult(session.session_id)
    setResult(r)
    setFinished(true)
    clearExam(provider)
  }

  function handleRestart() {
    clearExam(provider)
    navigate(`/exam?provider=${provider}`)
  }

  // MUST be before any conditional return — Rules of Hooks
  useEffect(() => {
    if (!session) return
    const q = session.questions[currentIdx]
    setTutorContext({
      page: 'exam',
      provider,
      domain: q?.domain ?? null,
      questionText: q?.text ?? null,
      questionOptions: q?.options ?? [],
      answered,
    })
  }, [currentIdx, answered, session]) // eslint-disable-line react-hooks/exhaustive-deps

  if (error) return (
    <>
      <AppHeader title={t.mode_exam} provider={provider} />
      <div className="error-msg">{error} <button className="btn btn--ghost" onClick={() => navigate('/')}>{t.back_home}</button></div>
    </>
  )
  if (!session) return (
    <>
      <AppHeader title={t.mode_exam} provider={provider} />
      <div className="loading">{t.loading}</div>
    </>
  )

  if (finished && result) {
    return (
      <>
        <AppHeader title={t.mode_exam} provider={provider} />
        <ResultSummary result={result} onRestart={handleRestart} onHome={() => navigate('/')} />
      </>
    )
  }

  const question = session.questions[currentIdx]

  return (
    <>
      <AppHeader title={t.mode_exam} provider={provider} />
      {resuming && (
        <div className="resume-banner">
          Retomando examen guardado — pregunta {currentIdx + 1} de {session.questions.length}
        </div>
      )}
      <main className="exam-mode">
        <div className="exam-top">
          <ProgressBar current={currentIdx + 1} total={session.questions.length} />
          <Timer seconds={secondsLeft} onExpire={handleExpire} onTick={setSecondsLeft} />
        </div>

        <QuestionCard
          question={question}
          selectedIndex={selected}
          selectedIndices={selectedIndices}
          onSelect={handleSelect}
          disabled={answered}
        />

        {answered && (
          <ExplanationPanel
            isCorrect={isCorrect}
            explanation={question.explanation}
            correctOptions={(question.correct_indices ?? [question.correct_index]).map((i: number) => question.options[i])}
          />
        )}

        <div className="exam-actions">
          {!answered ? (
            <button className="btn btn--primary" onClick={handleConfirm} disabled={
            (question.num_correct ?? 1) > 1 ? selectedIndices.length !== question.num_correct : selected === null
          }>
              {t.confirm_answer}
            </button>
          ) : (
            <button className="btn btn--primary" onClick={handleNext}>
              {currentIdx + 1 >= session.questions.length ? t.see_results : t.next_question}
            </button>
          )}
        </div>
      </main>
    </>
  )
}
