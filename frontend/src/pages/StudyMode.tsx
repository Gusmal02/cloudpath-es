import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getStudyQuestion, submitStudyAnswer } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { QuestionCard } from '../components/QuestionCard'
import { useTutorContext } from '../context/TutorContext'
import type { Provider, Question } from '../types/exam'
import t from '../i18n/es.json'

export function StudyMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const { setTutorContext } = useTutorContext()
  const [question, setQuestion] = useState<Question | null>(null)
  const [seen, setSeen] = useState<string[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [error, setError] = useState('')

  const loadNext = useCallback(
    (excludeIds: string[]) => {
      setQuestion(null)
      setSelected(null)
      setSelectedIndices([])
      setAnswered(false)
      getStudyQuestion(provider, excludeIds)
        .then(setQuestion)
        .catch(() => setError(t.error_load))
    },
    [provider],
  )

  useEffect(() => {
    loadNext([])
  }, [loadNext])

  useEffect(() => {
    setTutorContext({
      page: 'study',
      provider,
      domain: question?.domain ?? null,
      questionText: question?.text ?? null,
      questionOptions: question?.options ?? [],
      answered,
    })
  }, [question?.id, answered]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSelect(i: number) {
    if (!question) return
    const isMulti = (question.num_correct ?? 1) > 1
    if (isMulti) {
      setSelectedIndices((prev) =>
        prev.includes(i) ? prev.filter((x) => x !== i) : [...prev, i]
      )
    } else {
      setSelected(i)
    }
  }

  async function handleConfirm() {
    if (!question) return
    const isMulti = (question.num_correct ?? 1) > 1
    const chosen = isMulti ? selectedIndices : (selected !== null ? [selected] : [])
    if (chosen.length === 0) return
    const fb = await submitStudyAnswer(question.id, chosen)
    setIsCorrect(fb.is_correct)
    setAnswered(true)
    setSeen((s) => [...s, question.id])
  }

  return (
    <>
      <AppHeader title={t.mode_study} provider={provider} />
      <main className="study-mode">
        {error ? (
          <div className="error-msg">{error}</div>
        ) : !question ? (
          <div className="loading">{t.loading}</div>
        ) : (
          <>
            <QuestionCard
              question={question}
              selectedIndex={selected}
              selectedIndices={selectedIndices}
              onSelect={handleSelect}
              disabled={answered}
            />

            {answered && (
              <>
                <ExplanationPanel
                  isCorrect={isCorrect}
                  explanation={question.explanation}
                  correctOption={question.options[question.correct_index]}
                />
                {!isCorrect && (
                  <div className="study-arch-hint">
                    <span>¿Quieres ver cómo encaja en una arquitectura?</span>
                    <Link
                      to={`/arch?provider=${provider}`}
                      className="study-arch-link"
                    >
                      Explorar en el simulador →
                    </Link>
                  </div>
                )}
              </>
            )}

            <div className="exam-actions">
              {!answered ? (
                <button className="btn btn--primary" onClick={handleConfirm} disabled={
                  (question.num_correct ?? 1) > 1 ? selectedIndices.length !== question.num_correct : selected === null
                }>
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
      </main>
    </>
  )
}
