# Contrato técnico: Tutor Virtual CloudPath ES

**Versión:** 1.0  
**Fecha:** 2026-11-05  
**Estado:** Aprobado para implementación

---

## Propósito

Panel de chat flotante y plegable que actúa como tutor de certificaciones cloud. Conoce el contexto de la página activa y la pregunta en pantalla. Solo se activa si el usuario tiene la IA habilitada en Configuración.

---

## Límites funcionales (invariables)

| Puede | No puede |
|---|---|
| Explicar conceptos cloud de distintas formas | Revelar la respuesta correcta durante un examen activo |
| Dar analogías, ejemplos y casos de uso | Responder sobre temas no relacionados con cloud/certificaciones |
| Explicar la respuesta completa *después* de que el usuario respondió | Acceder a archivos, código o estado interno de la app |
| Señalar qué dominios estudiar más según el contexto | Actuar como asistente general (redacción, matemáticas, etc.) |
| Redirigir preguntas fuera de alcance con un mensaje claro | Modificar preguntas, respuestas ni configuración |

---

## Arquitectura

### Backend — `backend/tutor/`

Paquete con responsabilidad única por archivo. **No se mezcla lógica entre archivos.**

```
backend/tutor/
├── __init__.py
├── topics.py          # SOLO datos: certificaciones, dominios, servicios por proveedor
├── prompt_builder.py  # SOLO construcción de texto: recibe contexto, devuelve string
├── guardrails.py      # SOLO validación rápida (Python puro, sin LLM)
└── ollama_chat.py     # SOLO comunicación: llama a /api/chat de Ollama
```

#### `topics.py` — única fuente de verdad para certificaciones

```python
CERTIFICATIONS: dict[str, dict] = {
    "AWS": {
        "name": "AWS Cloud Practitioner (CLF-C02)",
        "exam_domains": ["Cloud Concepts", "Security", "Cloud Technology", "Billing and Pricing"],
        "key_services": ["EC2", "S3", "RDS", "Lambda", "IAM", "VPC", "CloudFront", ...],
    },
    "GCP": {
        "name": "Google Cloud Digital Leader",
        "exam_domains": ["Cloud Concepts", "Storage", "Compute", "Networking", "Security"],
        "key_services": ["Compute Engine", "Cloud Storage", "BigQuery", ...],
    },
    "AZURE": {
        "name": "Microsoft Azure Fundamentals (AZ-900)",
        "exam_domains": ["Cloud Concepts", "Core Services", "Security", "Pricing and Support"],
        "key_services": ["Virtual Machines", "Blob Storage", "Azure Functions", ...],
    },
}
```

**Regla:** para añadir una certificación nueva, solo se modifica este archivo. El resto del tutor se adapta automáticamente.

#### `prompt_builder.py` — construye el system prompt

Recibe un `TutorContext` (dataclass) y devuelve el system prompt completo como string. No importa nada de HTTP ni de Ollama.

Estructura del prompt resultante:
1. Rol y límites fijos (no negociables)
2. Certificación activa y sus dominios
3. Contexto de la página actual
4. Pregunta en pantalla (sin `correct_indices`)
5. Instrucción específica según `answered: bool`

#### `guardrails.py` — filtro rápido sin LLM

Valida el mensaje del usuario antes de enviarlo a Ollama. Implementado en Python puro (sin llamada externa).

Bloquea si el mensaje contiene:
- Petición explícita de respuesta directa durante examen (`answered=False`)
- Palabras clave fuera de alcance (lista configurable)
- Mensajes vacíos o excesivamente largos (>500 caracteres)

Devuelve `(allowed: bool, reason: str | None)`.

#### `ollama_chat.py` — cliente de chat multi-turno

Usa `/api/chat` de Ollama (distinto de `/api/generate` que usa WhatIf).

```python
async def call_ollama_chat(
    system_prompt: str,
    messages: list[dict],   # [{"role": "user"|"assistant", "content": str}]
    model: str,
    base_url: str,
    timeout: float = 90.0,
) -> str:
    ...
```

**No modifica** `whatif/ollama_client.py` — ese archivo sigue intacto.

#### `routers/tutor.py` — router delgado

```
POST /tutor/chat
```

Request:
```json
{
  "message": "string (max 500 chars)",
  "context": {
    "page": "exam | study | review | arch",
    "provider": "AWS | GCP | AZURE",
    "domain": "string | null",
    "question_text": "string | null",
    "question_options": ["string"] | null,
    "answered": false,
    "canvas_services": ["string"] | null
  },
  "history": [
    {"role": "user | assistant", "content": "string"}
  ]
}
```

**NUNCA recibe `correct_indices`, `correct_index` ni `explanation` cuando `answered=false`.**

Response:
```json
{
  "reply": "string",
  "blocked": false,
  "block_reason": null
}
```

Errores:
- `503` si Ollama no está disponible
- `422` si el contexto es inválido
- `200` con `blocked: true` si el guardrail bloqueó el mensaje (no es error HTTP)

---

### Frontend

#### `frontend/src/context/TutorContext.tsx`

Define la interfaz y el provider. Cualquier página puede consumirlo con `useTutorContext()`.

```typescript
interface TutorContextState {
  page: 'exam' | 'study' | 'review' | 'arch' | null
  provider: string | null
  domain: string | null
  questionText: string | null
  questionOptions: string[] | null
  answered: boolean
  canvasServices: string[] | null
}
```

Regla de actualización en cada página:
- Se llama `setTutorContext` en un `useEffect` con dependencia en `currentIdx` (examen) o en `question?.id` (estudio).
- **Nunca** dentro de un tick de timer ni en un render path que se ejecute en cada frame.

#### `frontend/src/components/TutorPanel.tsx`

Responsabilidad única: UI del chat. No conoce las páginas ni la lógica de negocio.

- Lee de `TutorContext`
- Llama a `chatWithTutor()` de `api/client.ts`
- Mantiene historial en `useState` (no persistido — intencional)
- Envía solo los últimos **6 mensajes** al backend
- Estado de carga: botón deshabilitado + indicador "pensando..."
- Si `page === null`: no renderiza nada

Posicionamiento: botón flotante **esquina inferior izquierda** (`position: fixed; bottom: 1.5rem; left: 1.5rem`). Panel se abre hacia arriba. Z-index: 1000 (superior a React Flow).

#### Activación

El tutor se muestra **solo si** `localStorage.getItem('cloudpath_ai_questions') === 'true'`.

Si Ollama retorna 503, el panel muestra: *"El tutor necesita Ollama activo. Instálalo desde ollama.com y ejecuta: `ollama pull llama3.2:3b`"*

#### Páginas que publican contexto

| Página | Publica | Cuándo actualiza |
|---|---|---|
| ExamMode | provider, domain, question_text, options, answered | `useEffect` con dep en `currentIdx` |
| StudyMode | provider, domain, question_text, options, answered | `useEffect` con dep en `question?.id` |
| ReviewMode | provider, domain | Al montar |
| ArchMode | provider, canvas_services (nombres de nodos) | `useEffect` con dep en `nodes` |
| Home / Settings | `page: null` | Al montar (deshabilita el panel) |

---

## Reglas de extensibilidad

| Para hacer esto | Solo tocas |
|---|---|
| Añadir certificación nueva | `backend/tutor/topics.py` |
| Añadir Terraform/K8s como temario | `topics.py` + nuevo valor en `page` del contexto |
| Cambiar tono o estilo del tutor | `backend/tutor/prompt_builder.py` |
| Ajustar palabras bloqueadas | `backend/tutor/guardrails.py` |
| Añadir nueva página con contexto | Esa página llama `setTutorContext({...})` |
| Cambiar modelo de IA | `backend/config.py` (`OLLAMA_MODEL`) |

---

## Lo que este contrato NO cubre (fuera de alcance v1)

- Streaming de respuestas
- Persistencia del historial de chat
- Autenticación o límite de uso por usuario
- Validación semántica de respuestas generadas por IA
- Modo "simulacro completo" (65 preguntas)

---

## Archivos creados/modificados

| Archivo | Acción |
|---|---|
| `backend/tutor/__init__.py` | Crear |
| `backend/tutor/topics.py` | Crear |
| `backend/tutor/prompt_builder.py` | Crear |
| `backend/tutor/guardrails.py` | Crear |
| `backend/tutor/ollama_chat.py` | Crear |
| `backend/routers/tutor.py` | Crear |
| `backend/main.py` | Modificar — registrar router |
| `frontend/src/context/TutorContext.tsx` | Crear |
| `frontend/src/components/TutorPanel.tsx` | Crear |
| `frontend/src/components/TutorPanel.css` | Crear |
| `frontend/src/api/client.ts` | Modificar — añadir `chatWithTutor()` |
| `frontend/src/App.tsx` | Modificar — TutorProvider + TutorPanel global |
| `frontend/src/pages/ExamMode.tsx` | Modificar — `setTutorContext` en `useEffect([currentIdx])` |
| `frontend/src/pages/StudyMode.tsx` | Modificar — `setTutorContext` en `useEffect([question?.id])` |
| `frontend/src/pages/ReviewMode.tsx` | Modificar — `setTutorContext` al montar |
| `frontend/src/pages/ArchMode.tsx` | Modificar — `setTutorContext` en `useEffect([nodes])` |
| `frontend/src/pages/Home.tsx` | Modificar — `setTutorContext({page: null})` |
