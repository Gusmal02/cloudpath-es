# Motor What If — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an AI-powered "What If" panel to the architecture simulator that analyzes a cloud diagram (nodes + edges) using a local Ollama model and returns cost estimates, detected risks, and improvement suggestions — all in Spanish.

**Architecture:** A new FastAPI router `POST /whatif` receives the current diagram (nodes/edges arrays), serializes them into a natural-language prompt describing the architecture, calls the Ollama REST API (`http://localhost:11434/api/generate`), and returns a structured JSON response with three sections: `costo`, `riesgos`, `sugerencias`. The frontend adds a collapsible side panel to ArchMode that opens when the user clicks "Analizar con IA", sends the live diagram state, and renders the three sections. If Ollama is unreachable, the endpoint returns HTTP 503 with a Spanish error message; the frontend shows a friendly fallback instead of crashing.

**Tech Stack:** Python 3.12 + httpx (async HTTP to Ollama), FastAPI, llama3.2:3b via Ollama 0.40.11, React 18 + TypeScript, existing design tokens

**Spec:** inline (this document)

## Global Constraints
- Python 3.12, uv; no new Python dependencies beyond `httpx` (already likely installed; add if missing)
- React 18 + TypeScript + Vite + Tailwind v4 (CSS-first); no new npm packages
- All copy in Spanish
- Existing design tokens: `--accent #1D4ED8`, `--ok #16A34A`, `--fail #DC2626`, `--surface #FFFFFF`
- Ollama model: `llama3.2:3b` — plan includes `ollama pull llama3.2:3b` step
- Backend must degrade gracefully: if Ollama is unreachable → HTTP 503, never 500
- Cost estimates are qualitative approximations by the LLM — not live AWS pricing API calls
- Analysis result is ephemeral (in-memory on the frontend); user can export as plain text
- TDD: write failing test first for every backend endpoint

## Review Focus
- A diagram with 0 nodes sent to POST /whatif must return 400 with a clear Spanish message, not call Ollama
- If Ollama is unreachable, the response must be 503 (not 500/timeout hanging indefinitely); include a 15-second timeout on the httpx call
- The prompt builder must include service descriptions (from cloudServices.ts equivalents in the backend) so the LLM understands what each service does
- The panel must render correctly when analysis text contains markdown-style `**bold**` or bullet lists (strip or render safely)
- Exporting analysis as text must include the diagram name, provider, timestamp, and all three sections

---

## Task 1: Ollama client + prompt builder (backend)

**Files:**
- Create: `backend/whatif/ollama_client.py`
- Create: `backend/whatif/prompt_builder.py`
- Create: `backend/whatif/__init__.py`
- Create: `backend/tests/test_whatif_prompt.py`

**Interfaces:**
- Produces:
  - `build_prompt(nodes: list[dict], edges: list[dict], provider: str) -> str` — converts diagram to natural language prompt
  - `call_ollama(prompt: str, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434") -> str` — async, returns raw LLM text; raises `OllamaUnavailableError` if unreachable or timeout

---

- [ ] **Step 1: Write failing tests for prompt_builder**

```python
# backend/tests/test_whatif_prompt.py
from whatif.prompt_builder import build_prompt

def test_prompt_includes_service_labels():
    nodes = [
        {"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "Instancias virtuales"}},
        {"id": "n2", "data": {"label": "RDS", "category": "Base de datos", "description": "Bases de datos relacionales"}},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    prompt = build_prompt(nodes, edges, "AWS")
    assert "EC2" in prompt
    assert "RDS" in prompt
    assert "AWS" in prompt

def test_prompt_mentions_connections():
    nodes = [
        {"id": "n1", "data": {"label": "Lambda", "category": "Cómputo", "description": "Funciones serverless"}},
        {"id": "n2", "data": {"label": "DynamoDB", "category": "Base de datos", "description": "NoSQL serverless"}},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    prompt = build_prompt(nodes, edges, "AWS")
    assert "Lambda" in prompt
    assert "DynamoDB" in prompt
    # At least one of the connection words
    assert any(w in prompt.lower() for w in ["conecta", "conectado", "→", "->"])

def test_prompt_requests_three_sections():
    nodes = [{"id": "n1", "data": {"label": "S3", "category": "Almacenamiento", "description": "Objetos"}}]
    prompt = build_prompt(nodes, [], "AWS")
    assert "costo" in prompt.lower()
    assert "riesgo" in prompt.lower()
    assert "sugerencia" in prompt.lower()
```

Run: `pytest tests/test_whatif_prompt.py -v`
Expected: FAIL — `whatif` module not found

- [ ] **Step 2: Create `backend/whatif/__init__.py`** (empty)

- [ ] **Step 3: Implement `prompt_builder.py`**

`build_prompt` builds a Spanish prompt structured as:

```
Eres un arquitecto cloud senior. Analiza la siguiente arquitectura {provider}:

SERVICIOS ({n} nodos):
- {label} ({category}): {description}
...

CONEXIONES:
- {label_A} → {label_B}
...

Responde ÚNICAMENTE en este formato JSON exacto, sin texto adicional:
{{
  "costo": {{
    "nivel": "bajo|medio|alto|muy alto",
    "estimacion_mensual": "descripción con rangos en USD",
    "detalle": [{{"servicio": "...", "rango_usd": "...", "justificacion": "..."}}]
  }},
  "riesgos": [
    {{"titulo": "...", "descripcion": "...", "severidad": "baja|media|alta|crítica"}}
  ],
  "sugerencias": [
    {{"titulo": "...", "descripcion": "...", "prioridad": "baja|media|alta"}}
  ]
}}
```

- [ ] **Step 4: Run tests — PASS**

Run: `pytest tests/test_whatif_prompt.py -v`
Expected: PASS 3/3

- [ ] **Step 5: Implement `ollama_client.py`**

```python
import httpx

class OllamaUnavailableError(Exception):
    pass

async def call_ollama(
    prompt: str,
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
    timeout: float = 60.0,
) -> str:
    """Call Ollama generate endpoint. Raises OllamaUnavailableError if unreachable or timeout."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                f"{base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json()["response"]
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise OllamaUnavailableError(str(e)) from e
```

- [ ] **Step 6: Commit**

```bash
git add backend/whatif/ backend/tests/test_whatif_prompt.py
git commit -m "feat(whatif): prompt builder and Ollama async client"
```

---

## Task 2: POST /whatif router + response parser (backend)

**Files:**
- Create: `backend/whatif/response_parser.py`
- Create: `backend/routers/whatif.py`
- Modify: `backend/main.py` (include whatif router)
- Modify: `backend/config.py` (add `ollama_url`, `ollama_model`)
- Create: `backend/tests/test_whatif_api.py`

**Interfaces:**
- Consumes: `build_prompt`, `call_ollama`, `OllamaUnavailableError` from Task 1
- Produces:
  - `POST /whatif` body `{nodes: [...], edges: [...], provider: str}` → `{costo: {...}, riesgos: [...], sugerencias: [...]}`
  - 400 if `nodes` is empty
  - 503 `{"detail": "El servicio de IA local no está disponible. Inicia Ollama y ejecuta: ollama pull llama3.2:3b"}` if Ollama unreachable

---

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_whatif_api.py
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_RESPONSE = '''{
  "costo": {"nivel": "medio", "estimacion_mensual": "$50-150/mes", "detalle": []},
  "riesgos": [{"titulo": "Sin redundancia", "descripcion": "EC2 sin ASG", "severidad": "alta"}],
  "sugerencias": [{"titulo": "Agregar Auto Scaling", "descripcion": "...", "prioridad": "alta"}]
}'''

def test_whatif_empty_nodes_returns_400():
    r = client.post("/whatif", json={"nodes": [], "edges": [], "provider": "AWS"})
    assert r.status_code == 400

def test_whatif_returns_structured_analysis():
    with patch("routers.whatif.call_ollama", new=AsyncMock(return_value=MOCK_RESPONSE)):
        r = client.post("/whatif", json={
            "nodes": [{"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "VMs"}}],
            "edges": [],
            "provider": "AWS",
        })
    assert r.status_code == 200
    body = r.json()
    assert "costo" in body
    assert "riesgos" in body
    assert "sugerencias" in body

def test_whatif_ollama_unavailable_returns_503():
    from whatif.ollama_client import OllamaUnavailableError
    with patch("routers.whatif.call_ollama", new=AsyncMock(side_effect=OllamaUnavailableError("down"))):
        r = client.post("/whatif", json={
            "nodes": [{"id": "n1", "data": {"label": "S3", "category": "Almacenamiento", "description": "Objetos"}}],
            "edges": [],
            "provider": "AWS",
        })
    assert r.status_code == 503
```

Run: `pytest tests/test_whatif_api.py -v`
Expected: FAIL — `/whatif` not found

- [ ] **Step 2: Add `ollama_url` and `ollama_model` to `config.py`**

```python
ollama_url: str = field(default_factory=lambda: os.environ.get("OLLAMA_URL", "http://localhost:11434"))
ollama_model: str = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "llama3.2:3b"))
```

- [ ] **Step 3: Implement `response_parser.py`**

`parse_whatif_response(raw: str) -> dict` — extracts the JSON object from the LLM response. The LLM may wrap the JSON in markdown fences (` ```json ... ``` `); strip them first. If JSON parsing fails, return a fallback dict with `{"costo": {...}, "riesgos": [], "sugerencias": [], "_parse_error": true}` — never raise.

- [ ] **Step 4: Implement `routers/whatif.py`**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import get_settings
from whatif.ollama_client import call_ollama, OllamaUnavailableError
from whatif.prompt_builder import build_prompt
from whatif.response_parser import parse_whatif_response

router = APIRouter(prefix="/whatif", tags=["whatif"])

class WhatIfRequest(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    provider: str = "AWS"

@router.post("")
async def whatif_analysis(req: WhatIfRequest):
    if not req.nodes:
        raise HTTPException(status_code=400, detail="El diagrama no tiene nodos. Agrega al menos un servicio.")
    settings = get_settings()
    prompt = build_prompt(req.nodes, req.edges, req.provider)
    try:
        raw = await call_ollama(prompt, model=settings.ollama_model, base_url=settings.ollama_url)
    except OllamaUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="El servicio de IA local no está disponible. Inicia Ollama y ejecuta: ollama pull llama3.2:3b",
        )
    return parse_whatif_response(raw)
```

- [ ] **Step 5: Include router in main.py**

```python
from routers import whatif
app.include_router(whatif.router)
```

- [ ] **Step 6: Run tests — PASS**

Run: `pytest tests/test_whatif_api.py -v`
Expected: PASS 3/3

- [ ] **Step 7: Pull model (one-time setup step)**

```bash
ollama pull llama3.2:3b
```

Expected: model downloaded, `ollama list` shows `llama3.2:3b`

- [ ] **Step 8: Commit**

```bash
git add backend/whatif/response_parser.py backend/routers/whatif.py backend/main.py backend/config.py backend/tests/test_whatif_api.py
git commit -m "feat(whatif): POST /whatif endpoint with Ollama integration and 503 degradation"
```

---

## Task 3: What If panel (frontend)

**Files:**
- Create: `frontend/src/components/arch/WhatIfPanel.tsx`
- Create: `frontend/src/components/arch/WhatIfPanel.css`
- Modify: `frontend/src/api/client.ts` (add `analyzeArchitecture`)
- Modify: `frontend/src/pages/ArchMode.tsx` (add "Analizar con IA" button + panel state)

**Interfaces:**
- Consumes: `POST /whatif` from Task 2; `nodes` and `edges` live state from ArchMode
- Produces: collapsible side panel rendering `costo`, `riesgos`, `sugerencias` sections; "Exportar" button

---

- [ ] **Step 1: Add `analyzeArchitecture` to `client.ts`**

```typescript
export interface WhatIfResult {
  costo: {
    nivel: 'bajo' | 'medio' | 'alto' | 'muy alto'
    estimacion_mensual: string
    detalle: { servicio: string; rango_usd: string; justificacion: string }[]
  }
  riesgos: { titulo: string; descripcion: string; severidad: 'baja' | 'media' | 'alta' | 'crítica' }[]
  sugerencias: { titulo: string; descripcion: string; prioridad: 'baja' | 'media' | 'alta' }[]
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
```

- [ ] **Step 2: Implement `WhatIfPanel.tsx`**

The panel renders in three named sections using the design tokens:

- **Costo** — colored badge for `nivel` (verde=bajo, amarillo=medio, naranja=alto, rojo=muy alto) + `estimacion_mensual` text + collapsible table of `detalle` rows
- **Riesgos** — list of risk cards with severity badge (colores de `--ok`/`--fail`) + title + description
- **Sugerencias** — list of suggestion cards with priority badge + title + description
- **Exportar** — button that generates a `.txt` blob: diagram name, provider, timestamp, then the three sections as plain text, and triggers browser download

Props: `result: WhatIfResult | null`, `loading: boolean`, `error: string | null`, `diagramName: string`, `provider: string`, `onClose: () => void`

Loading state shows a spinner and "Analizando arquitectura con IA…" message.

Error state (503) shows the backend's `detail` message in a styled error box.

- [ ] **Step 3: Wire into `ArchMode.tsx`**

Add state: `const [whatIfOpen, setWhatIfOpen] = useState(false)`, `const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null)`, `const [whatIfLoading, setWhatIfLoading] = useState(false)`, `const [whatIfError, setWhatIfError] = useState<string | null>(null)`.

Add "Analizar con IA ✦" button to the existing `arch-toolbar` div.

On click:
```typescript
async function handleAnalyze() {
  setWhatIfOpen(true)
  setWhatIfLoading(true)
  setWhatIfError(null)
  try {
    const result = await analyzeArchitecture(nodes, edges, provider)
    setWhatIfResult(result)
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      ?? 'Error al analizar la arquitectura'
    setWhatIfError(msg)
  } finally {
    setWhatIfLoading(false)
  }
}
```

Change `arch-layout` to include the panel: when `whatIfOpen`, render `<WhatIfPanel>` as a sibling to `arch-canvas`; apply CSS class `arch-layout--with-panel` that sets `grid-template-columns: 1fr 240px` for the palette + canvas + panel split.

- [ ] **Step 4: Style `WhatIfPanel.css`**

```css
.whatif-panel {
  background: var(--surface);
  border-left: 1px solid color-mix(in srgb, var(--accent) 20%, transparent);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 1rem;
  width: 320px;
}
.whatif-panel__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.whatif-section { margin-bottom: 1.25rem; }
.whatif-section__title { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }
.whatif-badge { border-radius: 4px; font-size: 0.7rem; font-weight: 600; padding: 2px 6px; }
.whatif-badge--bajo    { background: #dcfce7; color: #166534; }
.whatif-badge--medio   { background: #fef9c3; color: #854d0e; }
.whatif-badge--alto    { background: #ffedd5; color: #9a3412; }
.whatif-badge--muy-alto { background: #fee2e2; color: #991b1b; }
.whatif-risk-card, .whatif-suggestion-card {
  border: 1px solid color-mix(in srgb, currentColor 15%, transparent);
  border-radius: 6px;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0.75rem;
}
.whatif-cost-table { font-size: 0.8rem; width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
.whatif-cost-table th, .whatif-cost-table td { padding: 4px 6px; text-align: left; border-bottom: 1px solid #e5e7eb; }
.whatif-cost-table th { font-weight: 600; }
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/arch/WhatIfPanel.tsx frontend/src/components/arch/WhatIfPanel.css frontend/src/api/client.ts frontend/src/pages/ArchMode.tsx
git commit -m "feat(whatif): collapsible AI analysis panel with cost/risks/suggestions"
```

---

## Task 4: End-to-end smoke test + polish

**Files:**
- Modify: `backend/tests/test_whatif_api.py` (add integration test against live Ollama, skipped when unavailable)
- Modify: `frontend/src/pages/ArchMode.tsx` (minor: disable "Analizar" button while loading; re-enable on close)

**Interfaces:**
- Consumes: everything from Tasks 1–3

---

- [ ] **Step 1: Add integration smoke test (skipped when Ollama down)**

```python
# append to backend/tests/test_whatif_api.py
import httpx
import pytest

def ollama_available() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False

@pytest.mark.skipif(not ollama_available(), reason="Ollama not running")
def test_whatif_live_ollama_returns_valid_structure():
    r = client.post("/whatif", json={
        "nodes": [
            {"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "Instancias virtuales"}},
            {"id": "n2", "data": {"label": "RDS", "category": "Base de datos", "description": "SQL administrado"}},
        ],
        "edges": [{"source": "n1", "target": "n2"}],
        "provider": "AWS",
    })
    assert r.status_code == 200
    body = r.json()
    assert "costo" in body
    assert isinstance(body["riesgos"], list)
    assert isinstance(body["sugerencias"], list)
```

Run: `pytest tests/test_whatif_api.py -v`
Expected: 3 unit tests PASS + 1 integration test PASS (or skipped if Ollama is down)

- [ ] **Step 2: Disable "Analizar" button while `whatIfLoading`**

In ArchMode toolbar: `disabled={whatIfLoading || nodes.length === 0}` on the "Analizar con IA" button. Add a tooltip hint when nodes is empty: `title="Agrega servicios al diagrama primero"`.

- [ ] **Step 3: Final commit**

```bash
git add backend/tests/test_whatif_api.py frontend/src/pages/ArchMode.tsx
git commit -m "feat(whatif): integration smoke test + UX polish (disable button, tooltip)"
```
