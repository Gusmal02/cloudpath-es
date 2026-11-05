import axios from 'axios'
import type { Question, ExamSession, ExamResult, AnswerFeedback, DomainProgress } from '../types/exam'

// Vite proxies /api/* to the backend — port resolved by vite.config.ts
const http = axios.create({ baseURL: '/api' })

export async function startExam(provider: string, n_questions: number): Promise<ExamSession> {
  const res = await http.post('/exam/start', { provider, n_questions })
  return res.data
}

export async function submitAnswer(
  session_id: string,
  question_id: string,
  chosen_indices: number[],
): Promise<AnswerFeedback> {
  const res = await http.post('/exam/answer', { session_id, question_id, chosen_indices })
  return res.data
}

export async function getResult(session_id: string): Promise<ExamResult> {
  const res = await http.get(`/exam/result/${session_id}`)
  return res.data
}

export async function getStudyQuestion(
  provider: string,
  exclude_ids: string[],
): Promise<Question> {
  const params = new URLSearchParams({ provider })
  exclude_ids.forEach((id) => params.append('exclude_ids', id))
  const res = await http.get(`/study/question?${params}`)
  return res.data
}

export async function submitStudyAnswer(
  question_id: string,
  chosen_indices: number[],
): Promise<AnswerFeedback> {
  const res = await http.post('/study/answer', { question_id, chosen_indices })
  return res.data
}

export async function getDomainProgress(provider: string): Promise<DomainProgress[]> {
  const res = await http.get('/progress/domains', { params: { provider } })
  return res.data
}

export async function saveArchitecture(
  name: string,
  provider: string,
  nodes: unknown[],
  edges: unknown[],
) {
  const res = await http.post('/arch', {
    name,
    provider,
    nodes_json: JSON.stringify(nodes),
    edges_json: JSON.stringify(edges),
  })
  return res.data
}

export async function listArchitectures(provider?: string) {
  const res = await http.get('/arch', { params: provider ? { provider } : {} })
  return res.data
}

export async function loadArchitecture(id: string) {
  const res = await http.get(`/arch/${id}`)
  return res.data
}

export async function deleteArchitecture(id: string) {
  const res = await http.delete(`/arch/${id}`)
  return res.data
}

export interface WhatIfCostDetail {
  servicio: string
  rango_usd: string
  justificacion: string
}

export interface WhatIfRisk {
  titulo: string
  descripcion: string
  severidad: 'baja' | 'media' | 'alta' | 'crítica'
}

export interface WhatIfSuggestion {
  titulo: string
  descripcion: string
  prioridad: 'baja' | 'media' | 'alta'
}

export interface WhatIfResult {
  costo: {
    nivel: 'bajo' | 'medio' | 'alto' | 'muy alto'
    estimacion_mensual: string
    detalle: WhatIfCostDetail[]
  }
  riesgos: WhatIfRisk[]
  sugerencias: WhatIfSuggestion[]
  _parse_error?: boolean
}

export async function analyzeArchitecture(
  nodes: unknown[],
  edges: unknown[],
  provider: string,
): Promise<WhatIfResult> {
  const res = await http.post('/whatif', { nodes, edges, provider })
  return res.data
}

export interface GeneratedQuestion {
  id: string
  provider: string
  domain: string
  text: string
  options: string[]
  correct_index: number
  explanation: string
  ai_generated: boolean
}

export interface TutorMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface TutorChatRequest {
  message: string
  context: {
    page: string | null
    provider: string | null
    domain: string | null
    question_text: string | null
    question_options: string[]
    answered: boolean
    canvas_services: string[]
  }
  history: TutorMessage[]
}

export interface TutorChatResponse {
  reply: string
  blocked: boolean
  block_reason: string | null
}

export async function chatWithTutor(req: TutorChatRequest): Promise<TutorChatResponse> {
  const res = await http.post('/tutor/chat', req)
  return res.data
}

export async function generateQuestions(
  provider: string,
  domain: string | null,
  count: number,
): Promise<GeneratedQuestion[]> {
  const res = await http.post('/generate/questions', { provider, domain, count })
  return res.data.questions
}
