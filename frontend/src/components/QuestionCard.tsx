import type { Question } from '../types/exam'

interface Props {
  question: Question
  selectedIndex: number | null           // single-answer mode
  selectedIndices?: number[]             // multi-answer mode
  onSelect: (index: number) => void
  disabled?: boolean
}

export function QuestionCard({ question, selectedIndex, selectedIndices, onSelect, disabled }: Props) {
  const isMulti = (question.num_correct ?? 1) > 1
  const selected = isMulti
    ? (selectedIndices ?? [])
    : (selectedIndex !== null ? [selectedIndex] : [])

  return (
    <div className="question-card">
      <p className="question-text">{question.text}</p>
      {isMulti && (
        <p className="question-multi-hint">Selecciona {question.num_correct} respuestas</p>
      )}
      <ul className="options-list">
        {question.options.map((option, i) => {
          const isSelected = selected.includes(i)
          return (
            <li key={i}>
              <button
                className={`option-btn${isSelected ? ' selected' : ''}`}
                onClick={() => onSelect(i)}
                disabled={disabled}
                aria-pressed={isSelected}
              >
                <span className="option-letter">
                  {isMulti ? (isSelected ? '☑' : '☐') : String.fromCharCode(65 + i)}
                </span>
                <span>{option}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
