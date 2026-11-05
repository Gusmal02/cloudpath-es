import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getDomainProgress, getStudyQuestion, submitStudyAnswer } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { QuestionCard } from '../components/QuestionCard'
import { useTutorContext } from '../context/TutorContext'
import type { DomainProgress, Provider, Question } from '../types/exam'
import t from '../i18n/es.json'

const domainNames = t.domains as Record<string, string>

export function ReviewMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const { setTutorContext } = useTutorContext()

  const [progress, setProgress] = useState<DomainProgress[]>([])
  const [question, setQuestion] = useState<Question | null>(null)
  const [seen, setSeen] = useState<string[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getDomainProgress(provider).then(setProgress).catch(() => {})
    loadNext([])
    setTutorContext({ page: 'review', provider, answered: false })
  }, [provider]) // eslint-disable-line react-hooks/exhaustive-deps

  function loadNext(excludeIds: string[]) {
    setQuestion(null)
    setSelected(null)
    setAnswered(false)
    getStudyQuestion(provider, excludeIds)
      .then(setQuestion)
      .catch(() => setError(t.error_load))
  }

  async function handleConfirm() {
    if (!question || selected === null) return
    const fb = await submitStudyAnswer(question.id, selected)
    setIsCorrect(fb.is_correct)
    setAnswered(true)
    setSeen((s) => [...s, question.id])
    getDomainProgress(provider).then(setProgress).catch(() => {})
  }

  return (
    <>
      <AppHeader title={t.mode_review} provider={provider} />
      <main className="review-mode">
        {error ? (
          <div className="error-msg">{error}</div>
        ) : (
          <>
            {progress.length > 0 && (
              <div className="review-progress">
                {progress.map((d) => (
                  <div key={d.domain} className="review-domain">
                    <span className="review-domain-name">{domainNames[d.domain] ?? d.domain}</span>
                    <div className="review-domain-bar">
                      <div className="review-domain-fill" style={{ width: `${d.pct}%` }} />
                    </div>
                    <span className="review-domain-pct">{Math.round(d.pct)}%</span>
                  </div>
                ))}
              </div>
            )}

            {!question ? (
              <div className="loading">{t.loading}</div>
            ) : (
              <>
                <QuestionCard
                  question={question}
                  selectedIndex={selected}
                  onSelect={setSelected}
                  disabled={answered}
                />
                {answered && (
                  <ExplanationPanel
                    isCorrect={isCorrect}
                    explanation={question.explanation}
                    correctOption={question.options[question.correct_index]}
                  />
                )}
                <div className="exam-actions">
                  {!answered ? (
                    <button className="btn btn--primary" onClick={handleConfirm} disabled={selected === null}>
                      {t.confirm_answer}
                    </button>
                  ) : (
                    <button className="btn btn--primary" onClick={() => loadNext([...seen, question.id])}>
                      {t.next_question}
                    </button>
                  )}
                </div>
              </>
            )}
          </>
        )}
      </main>
    </>
  )
}
