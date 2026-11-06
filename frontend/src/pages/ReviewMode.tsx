import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getDomainProgress } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { QuestionCard } from '../components/QuestionCard'
import { useStudyFlow } from '../hooks/useStudyFlow'
import type { DomainProgress, Provider } from '../types/exam'
import t from '../i18n/es.json'

const domainNames = t.domains as Record<string, string>

export function ReviewMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const [progress, setProgress] = useState<DomainProgress[]>([])

  const {
    question,
    selected,
    selectedIndices,
    answered,
    isCorrect,
    feedbackExplanation,
    feedbackCorrectIndices,
    error,
    exhausted,
    handleSelect,
    handleConfirm,
    advance,
    restart,
  } = useStudyFlow(provider, 'review')

  // Load domain progress on mount/provider change, and after each confirmed answer
  useEffect(() => {
    getDomainProgress(provider).then(setProgress).catch(() => {})
  }, [provider])

  useEffect(() => {
    if (!answered) return
    getDomainProgress(provider).then(setProgress).catch(() => {})
  }, [answered]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <AppHeader title={t.mode_review} provider={provider} />
      <main className="review-mode">
        {error ? (
          <div className="error-msg">{error}</div>
        ) : exhausted ? (
          <div className="study-exhausted">
            <p>🎉 ¡Completaste todas las preguntas disponibles para {provider}!</p>
            <button className="btn btn--primary" onClick={restart}>
              Volver a empezar
            </button>
          </div>
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
                  selectedIndices={selectedIndices}
                  onSelect={handleSelect}
                  disabled={answered}
                />
                {answered && (
                  <ExplanationPanel
                    isCorrect={isCorrect}
                    explanation={feedbackExplanation}
                    correctOptions={feedbackCorrectIndices.map((i) => question.options[i])}
                  />
                )}
                <div className="exam-actions">
                  {!answered ? (
                    <button
                      className="btn btn--primary"
                      onClick={handleConfirm}
                      disabled={
                        (question.num_correct ?? 1) > 1
                          ? selectedIndices.length !== question.num_correct
                          : selected === null
                      }
                    >
                      {t.confirm_answer}
                    </button>
                  ) : (
                    <button className="btn btn--primary" onClick={advance}>
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
