import { createContext, useContext, useState } from 'react'
import type { ReactNode } from 'react'

export interface TutorContextState {
  page: 'exam' | 'study' | 'review' | 'arch' | null
  provider: string | null
  domain: string | null
  questionText: string | null
  questionOptions: string[]
  answered: boolean
  canvasServices: string[]
}

const defaultState: TutorContextState = {
  page: null,
  provider: null,
  domain: null,
  questionText: null,
  questionOptions: [],
  answered: false,
  canvasServices: [],
}

interface TutorContextValue {
  tutorCtx: TutorContextState
  setTutorContext: (ctx: Partial<TutorContextState>) => void
  clearTutorContext: () => void
}

const TutorContext = createContext<TutorContextValue>({
  tutorCtx: defaultState,
  setTutorContext: () => {},
  clearTutorContext: () => {},
})

export function TutorProvider({ children }: { children: ReactNode }) {
  const [tutorCtx, setCtx] = useState<TutorContextState>(defaultState)

  function setTutorContext(partial: Partial<TutorContextState>) {
    setCtx((prev) => ({ ...prev, ...partial }))
  }

  function clearTutorContext() {
    setCtx(defaultState)
  }

  return (
    <TutorContext.Provider value={{ tutorCtx, setTutorContext, clearTutorContext }}>
      {children}
    </TutorContext.Provider>
  )
}

export function useTutorContext() {
  return useContext(TutorContext)
}
