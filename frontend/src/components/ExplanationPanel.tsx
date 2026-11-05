import t from '../i18n/es.json'

interface Props {
  isCorrect: boolean
  explanation: string
  correctOptions?: string[]
}

export function ExplanationPanel({ isCorrect, explanation, correctOptions }: Props) {
  return (
    <div className={`explanation-panel ${isCorrect ? 'explanation--correct' : 'explanation--incorrect'}`}>
      <p className="explanation-verdict">
        {isCorrect ? t.correct : t.incorrect}
      </p>
      {!isCorrect && correctOptions && correctOptions.length > 0 && (
        <div className="explanation-correct-was">
          <strong>{t.correct_was}</strong>
          {correctOptions.length === 1 ? (
            <span> {correctOptions[0]}</span>
          ) : (
            <ul className="explanation-correct-list">
              {correctOptions.map((opt, i) => <li key={i}>{opt}</li>)}
            </ul>
          )}
        </div>
      )}
      <p className="explanation-text">{explanation}</p>
    </div>
  )
}
