import { Link, useSearchParams } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import { ExplanationPanel } from '../components/ExplanationPanel'
import { QuestionCard } from '../components/QuestionCard'
import { useStudyFlow } from '../hooks/useStudyFlow'
import type { Provider } from '../types/exam'
import t from '../i18n/es.json'

export function StudyMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider

  const {
    question,
    seen,
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
  } = useStudyFlow(provider, 'study')

  return (
    <>
      <AppHeader title={t.mode_study} provider={provider} />
      <main className="study-mode">
        {error ? (
          <div className="error-msg">{error}</div>
        ) : exhausted ? (
          <div className="study-exhausted">
            <p>🎉 ¡Completaste todas las preguntas disponibles para {provider}!</p>
            <button className="btn btn--primary" onClick={restart}>
              Volver a empezar
            </button>
          </div>
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
                  explanation={feedbackExplanation}
                  correctOptions={feedbackCorrectIndices.map((i) => question.options[i])}
                />
                {!isCorrect && (
                  <div className="study-arch-hint">
                    <span>¿Quieres ver cómo encaja en una arquitectura?</span>
                    <Link to={`/arch?provider=${provider}`} className="study-arch-link">
                      Explorar en el simulador →
                    </Link>
                  </div>
                )}
              </>
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
      </main>
    </>
  )
}
