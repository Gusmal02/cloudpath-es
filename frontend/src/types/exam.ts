export type Domain =
  | 'CLOUD_CONCEPTS' | 'SECURITY' | 'TECHNOLOGY' | 'BILLING' | 'AI_ML'
  | 'DIGITAL_TRANSFORMATION' | 'DATA_INNOVATION' | 'INFRASTRUCTURE_MODERNIZATION' | 'GCP_SECURITY' | 'GCP_SCALING'
  | 'AZURE_CLOUD_CONCEPTS' | 'AZURE_ARCHITECTURE' | 'AZURE_MANAGEMENT'
export type Provider = 'AWS' | 'GCP' | 'AZURE'
export type Difficulty = 'easy' | 'medium' | 'hard'
export type ExamMode = 'exam' | 'study' | 'review'

export interface Question {
  id: string
  text: string
  options: string[]
  correct_index?: number       // absent in exam questions until answered
  correct_indices?: number[]   // absent in exam questions until answered
  num_correct: number          // how many the user must select
  explanation?: string         // absent in exam questions until answered
  domain: Domain
  provider: Provider
  difficulty: Difficulty
}

export interface ExamSession {
  session_id: string
  questions: Question[]
}

export interface DomainProgress {
  domain: Domain
  correct: number
  total: number
  pct: number
}

export interface ExamResult {
  session_id: string
  score: number
  total: number
  by_domain: DomainProgress[]
}

export interface AnswerFeedback {
  is_correct: boolean
  correct_index?: number
  correct_indices?: number[]
  explanation?: string
}
