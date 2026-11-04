import t from '../i18n/es.json'

interface Props {
  isCorrect: boolean
  explanation: string
  correctOption?: string
}

export function ExplanationPanel({ isCorrect, explanation, correctOption }: Props) {
  return (
    <div className={`explanation-panel ${isCorrect ? 'explanation--correct' : 'explanation--incorrect'}`}>
      <p className="explanation-verdict">
        {isCorrect ? t.correct : t.incorrect}
      </p>
      {!isCorrect && correctOption && (
        <p className="explanation-correct-was">
          <strong>{t.correct_was}</strong> {correctOption}
        </p>
      )}
      <p className="explanation-text">{explanation}</p>
    </div>
  )
}
