import axios from 'axios'
import { useCallback, useEffect, useState } from 'react'
import { getStudyQuestion, submitStudyAnswer } from '../api/client'
import { useTutorContext } from '../context/TutorContext'
import type { AnswerFeedback, Provider, Question } from '../types/exam'
import t from '../i18n/es.json'

export type StudyMode = 'study' | 'review'

export interface StudyFlowState {
  question: Question | null
  seen: string[]
  selected: number | null
  selectedIndices: number[]
  answered: boolean
  isCorrect: boolean
  feedbackExplanation: string
  feedbackCorrectIndices: number[]
  error: string
  exhausted: boolean
  handleSelect: (i: number) => void
  handleConfirm: () => Promise<void>
  advance: () => void
  restart: () => void
}

export function useStudyFlow(provider: Provider, mode: StudyMode): StudyFlowState {
  const { setTutorContext, clearTutorHistory } = useTutorContext()
  const [question, setQuestion] = useState<Question | null>(null)
  const [seen, setSeen] = useState<string[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [feedbackExplanation, setFeedbackExplanation] = useState('')
  const [feedbackCorrectIndices, setFeedbackCorrectIndices] = useState<number[]>([])
  const [error, setError] = useState('')
  const [exhausted, setExhausted] = useState(false)

  const loadNext = useCallback(
    (excludeIds: string[]) => {
      setQuestion(null)
      setSelected(null)
      setSelectedIndices([])
      setAnswered(false)
      setFeedbackExplanation('')
      setFeedbackCorrectIndices([])
      setError('')
      getStudyQuestion(provider, excludeIds)
        .then(setQuestion)
        .catch((err) => {
          if (axios.isAxiosError(err) && err.response?.status === 404) {
            setExhausted(true)
          } else {
            setError(t.error_load)
          }
        })
    },
    [provider],
  )

  // Reset and load when provider changes
  useEffect(() => {
    clearTutorHistory()
    setSeen([])
    setExhausted(false)
    loadNext([])
  }, [loadNext]) // eslint-disable-line react-hooks/exhaustive-deps

  // Keep tutor context in sync with current question and answered state
  useEffect(() => {
    setTutorContext({
      page: mode,
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
    const fb: AnswerFeedback = await submitStudyAnswer(question.id, chosen)
    setIsCorrect(fb.is_correct)
    setFeedbackExplanation(fb.explanation ?? '')
    setFeedbackCorrectIndices(
      fb.correct_indices ?? (fb.correct_index != null ? [fb.correct_index] : [])
    )
    setAnswered(true)
    setSeen((s) => [...s, question.id])
  }

  function advance() {
    if (!question) return
    loadNext([...seen, question.id])
  }

  function restart() {
    setSeen([])
    setExhausted(false)
    loadNext([])
  }

  return {
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
  }
}
