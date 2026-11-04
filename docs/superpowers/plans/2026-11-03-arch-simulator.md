# Simulador de Arquitecturas — Implementation Plan

**Goal:** Add an interactive drag-and-drop cloud architecture diagram builder to CloudPath ES.

**Architecture:** React Flow canvas with a service palette; users drag AWS/GCP/Azure service nodes onto the canvas, connect them, name the diagram, and save it. The backend persists diagrams in SQLite. Ollama analysis is wired but gated (disabled when Ollama is unreachable).

**Tech Stack:** @xyflow/react 12, FastAPI, SQLite, React 18 + TypeScript, Tailwind v4

**Spec:** inline (no separate spec file)

## Global Constraints
- Python 3.12, uv
- React 18 + TypeScript + Vite + Tailwind v4 (CSS-first, no tailwind.config.js)
- All copy in Spanish
- Existing design tokens: `--accent #1D4ED8`, `--ok #16A34A`, `--fail #DC2626`, `--base #EEF2F7`, `--surface #FFFFFF`
- No new dependencies beyond `@xyflow/react` on frontend; no new Python deps needed for tasks 1-3
- TDD: write failing test first for every backend endpoint

## Review Focus
- Saving a diagram with 0 nodes should be rejected with a clear message
- Loading a diagram that no longer exists returns 404, not 500
- Provider filter on GET /architectures must not leak other users' diagrams (single-user app — no auth; filter is cosmetic but must work)
- React Flow node positions must round-trip through JSON correctly (float precision)
- Deleting a diagram mid-session while it is open should not crash the frontend

---

### Task 1: @xyflow/react install + ArchMode page skeleton

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/pages/ArchMode.tsx`
- Create: `frontend/src/pages/ArchMode.css`
- Modify: `frontend/src/App.tsx` (add route `/arch`)
- Modify: `frontend/src/pages/Home.tsx` (add Arquitecturas card)

**Interfaces:**
- Produces: `<ArchMode />` exported from `frontend/src/pages/ArchMode.tsx`; route `/arch?provider=AWS`

- [ ] **Step 1: Install @xyflow/react**

```bash
cd frontend && npm install @xyflow/react
```

Expected: package.json lists `"@xyflow/react": "^12.x.x"`

- [ ] **Step 2: Add route in App.tsx**

Add `import { ArchMode } from './pages/ArchMode'` and `<Route path="/arch" element={<ArchMode />} />` alongside existing routes.

- [ ] **Step 3: Write failing render test**

```typescript
// frontend/src/pages/ArchMode.test.tsx
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ArchMode } from './ArchMode'

test('renders arch mode canvas', () => {
  render(<MemoryRouter initialEntries={['/arch?provider=AWS']}><ArchMode /></MemoryRouter>)
  expect(screen.getByText(/Simulador de Arquitecturas/i)).toBeInTheDocument()
})
```

Run: `npm test -- --testPathPattern=ArchMode`
Expected: FAIL — ArchMode not defined

- [ ] **Step 4: Create ArchMode.tsx skeleton**

```typescript
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AppHeader } from '../components/AppHeader'
import type { Provider } from '../types/exam'

export function ArchMode() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  return (
    <>
      <AppHeader title="Simulador de Arquitecturas" provider={provider} />
      <div style={{ height: 'calc(100vh - 56px)' }}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={() => {}} onEdgesChange={() => {}}>
          <Background /><Controls /><MiniMap />
        </ReactFlow>
      </div>
    </>
  )
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `npm test -- --testPathPattern=ArchMode`
Expected: PASS

- [ ] **Step 6: Add Arquitecturas card to Home.tsx**

Add a fourth mode card with SVG network icon, title "Arquitecturas", description "Diseña diagramas de infraestructura cloud" linking to `/arch?provider=${provider}`.

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/src/pages/ArchMode.tsx frontend/src/pages/ArchMode.css frontend/src/App.tsx frontend/src/pages/Home.tsx
git commit -m "feat: ArchMode page skeleton with React Flow canvas"
```

---

### Task 2: Service palette + draggable nodes

**Files:**
- Create: `frontend/src/components/arch/ServicePalette.tsx`
- Create: `frontend/src/components/arch/ServiceNode.tsx`
- Create: `frontend/src/data/cloudServices.ts`
- Modify: `frontend/src/pages/ArchMode.tsx`

**Interfaces:**
- Consumes: `ArchMode` from Task 1
- Produces: `cloudServices[provider]` — array of `{id, label, category, icon}` per provider; `ServiceNode` custom node type registered with React Flow

- [ ] **Step 1: Write failing test for cloudServices data**

```typescript
// frontend/src/data/cloudServices.test.ts
import { cloudServices } from './cloudServices'

test('AWS has at least 10 services', () => {
  expect(cloudServices['AWS'].length).toBeGreaterThanOrEqual(10)
})
test('each service has id, label, category, icon', () => {
  for (const svc of cloudServices['AWS']) {
    expect(svc).toHaveProperty('id')
    expect(svc).toHaveProperty('label')
    expect(svc).toHaveProperty('category')
    expect(svc).toHaveProperty('icon')
  }
})
```

Run: `npm test -- --testPathPattern=cloudServices`
Expected: FAIL

- [ ] **Step 2: Create cloudServices.ts**

```typescript
export interface CloudService { id: string; label: string; category: string; icon: string }
export const cloudServices: Record<string, CloudService[]> = {
  AWS: [
    { id: 'ec2', label: 'EC2', category: 'Compute', icon: '🖥️' },
    { id: 's3', label: 'S3', category: 'Storage', icon: '🪣' },
    { id: 'lambda', label: 'Lambda', category: 'Compute', icon: 'λ' },
    { id: 'rds', label: 'RDS', category: 'Database', icon: '🗄️' },
    { id: 'dynamodb', label: 'DynamoDB', category: 'Database', icon: '⚡' },
    { id: 'vpc', label: 'VPC', category: 'Network', icon: '🔒' },
    { id: 'elb', label: 'Load Balancer', category: 'Network', icon: '⚖️' },
    { id: 'cloudfront', label: 'CloudFront', category: 'Network', icon: '🌐' },
    { id: 'iam', label: 'IAM', category: 'Security', icon: '🔑' },
    { id: 'sqs', label: 'SQS', category: 'Messaging', icon: '📨' },
    { id: 'sns', label: 'SNS', category: 'Messaging', icon: '📢' },
    { id: 'cloudwatch', label: 'CloudWatch', category: 'Monitoring', icon: '📊' },
  ],
  GCP: [
    { id: 'gce', label: 'Compute Engine', category: 'Compute', icon: '🖥️' },
    { id: 'gcs', label: 'Cloud Storage', category: 'Storage', icon: '🪣' },
    { id: 'gcf', label: 'Cloud Functions', category: 'Compute', icon: 'λ' },
    { id: 'cloudsql', label: 'Cloud SQL', category: 'Database', icon: '🗄️' },
    { id: 'firestore', label: 'Firestore', category: 'Database', icon: '⚡' },
    { id: 'vpc_gcp', label: 'VPC', category: 'Network', icon: '🔒' },
    { id: 'lb_gcp', label: 'Cloud LB', category: 'Network', icon: '⚖️' },
    { id: 'cdn_gcp', label: 'Cloud CDN', category: 'Network', icon: '🌐' },
    { id: 'iam_gcp', label: 'IAM', category: 'Security', icon: '🔑' },
    { id: 'pubsub', label: 'Pub/Sub', category: 'Messaging', icon: '📨' },
  ],
  Azure: [
    { id: 'vm', label: 'Virtual Machine', category: 'Compute', icon: '🖥️' },
    { id: 'blob', label: 'Blob Storage', category: 'Storage', icon: '🪣' },
    { id: 'functions', label: 'Azure Functions', category: 'Compute', icon: 'λ' },
    { id: 'sqldb', label: 'SQL Database', category: 'Database', icon: '🗄️' },
    { id: 'cosmos', label: 'Cosmos DB', category: 'Database', icon: '⚡' },
    { id: 'vnet', label: 'VNet', category: 'Network', icon: '🔒' },
    { id: 'lb_az', label: 'Load Balancer', category: 'Network', icon: '⚖️' },
    { id: 'cdn_az', label: 'Azure CDN', category: 'Network', icon: '🌐' },
    { id: 'aad', label: 'Azure AD', category: 'Security', icon: '🔑' },
    { id: 'servicebus', label: 'Service Bus', category: 'Messaging', icon: '📨' },
  ],
}
```

- [ ] **Step 3: Run test — PASS**

Run: `npm test -- --testPathPattern=cloudServices`
Expected: PASS 2/2

- [ ] **Step 4: Create ServiceNode.tsx**

Custom React Flow node type: shows the service icon (large) + label below + a subtle category badge. Styled with design tokens.

```typescript
import { Handle, Position } from '@xyflow/react'
export function ServiceNode({ data }: { data: { icon: string; label: string; category: string } }) {
  return (
    <div className="service-node">
      <Handle type="target" position={Position.Top} />
      <div className="service-node__icon">{data.icon}</div>
      <div className="service-node__label">{data.label}</div>
      <div className="service-node__category">{data.category}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  )
}
```

- [ ] **Step 5: Create ServicePalette.tsx**

Left sidebar listing services grouped by category. Each item has a drag handler that adds a new node to the canvas on drop.

```typescript
export function ServicePalette({ provider, onAdd }: { provider: string; onAdd: (svc: CloudService) => void }) {
  // group by category, render draggable items
}
```

- [ ] **Step 6: Wire into ArchMode.tsx**

Register `ServiceNode` as custom node type with `nodeTypes`. Add palette on left, canvas on right. On palette item click/drag → add node at center of viewport with `useReactFlow().screenToFlowPosition`.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/data/cloudServices.ts frontend/src/components/arch/ frontend/src/pages/ArchMode.tsx
git commit -m "feat: service palette with draggable cloud nodes (AWS/GCP/Azure)"
```

---

### Task 3: Backend — save/load architectures

**Files:**
- Create: `backend/routers/arch.py`
- Modify: `backend/db/schema.sql` (add architectures table)
- Modify: `backend/db/database.py` (ensure table created on startup)
- Modify: `backend/main.py` (include arch router)
- Create: `backend/tests/test_arch.py`

**Interfaces:**
- Produces:
  - `POST /arch` body `{name, provider, nodes_json, edges_json}` → `{id, name, provider, created_at}`
  - `GET /arch?provider=AWS` → `[{id, name, provider, created_at}]`
  - `GET /arch/{id}` → `{id, name, provider, nodes_json, edges_json, created_at}`
  - `DELETE /arch/{id}` → `{deleted: true}`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_arch.py
def test_save_and_load_architecture(client, tmp_db):
    r = client.post("/arch", json={
        "name": "Mi primera arquitectura",
        "provider": "AWS",
        "nodes_json": '[{"id":"1","type":"service"}]',
        "edges_json": "[]"
    })
    assert r.status_code == 200
    arch_id = r.json()["id"]

    r2 = client.get(f"/arch/{arch_id}")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Mi primera arquitectura"

def test_list_architectures_filtered_by_provider(client, tmp_db):
    client.post("/arch", json={"name": "AWS arch", "provider": "AWS", "nodes_json": "[]", "edges_json": "[]"})
    client.post("/arch", json={"name": "GCP arch", "provider": "GCP", "nodes_json": "[]", "edges_json": "[]"})
    r = client.get("/arch?provider=AWS")
    assert r.status_code == 200
    names = [a["name"] for a in r.json()]
    assert "AWS arch" in names
    assert "GCP arch" not in names

def test_delete_architecture(client, tmp_db):
    r = client.post("/arch", json={"name": "borrar", "provider": "AWS", "nodes_json": "[]", "edges_json": "[]"})
    arch_id = r.json()["id"]
    client.delete(f"/arch/{arch_id}")
    r2 = client.get(f"/arch/{arch_id}")
    assert r2.status_code == 404
```

Run: `pytest tests/test_arch.py -v`
Expected: FAIL — router not found

- [ ] **Step 2: Add architectures table to schema**

```sql
CREATE TABLE IF NOT EXISTS architectures (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    nodes_json TEXT NOT NULL DEFAULT '[]',
    edges_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

- [ ] **Step 3: Create arch.py router**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid, sqlite3
from db.database import get_db

router = APIRouter(prefix="/arch", tags=["arch"])

class ArchIn(BaseModel):
    name: str
    provider: str
    nodes_json: str = "[]"
    edges_json: str = "[]"

@router.post("")
def save_arch(body: ArchIn):
    arch_id = str(uuid.uuid4())
    db = get_db()
    db.execute("INSERT INTO architectures (id,name,provider,nodes_json,edges_json) VALUES (?,?,?,?,?)",
               (arch_id, body.name, body.provider, body.nodes_json, body.edges_json))
    db.commit()
    row = db.execute("SELECT id,name,provider,created_at FROM architectures WHERE id=?", (arch_id,)).fetchone()
    return dict(row)

@router.get("")
def list_arch(provider: str | None = None):
    db = get_db()
    if provider:
        rows = db.execute("SELECT id,name,provider,created_at FROM architectures WHERE provider=? ORDER BY created_at DESC", (provider,)).fetchall()
    else:
        rows = db.execute("SELECT id,name,provider,created_at FROM architectures ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]

@router.get("/{arch_id}")
def get_arch(arch_id: str):
    db = get_db()
    row = db.execute("SELECT * FROM architectures WHERE id=?", (arch_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Arquitectura no encontrada")
    return dict(row)

@router.delete("/{arch_id}")
def delete_arch(arch_id: str):
    db = get_db()
    db.execute("DELETE FROM architectures WHERE id=?", (arch_id,))
    db.commit()
    return {"deleted": True}
```

- [ ] **Step 4: Include router in main.py**

```python
from routers import arch
app.include_router(arch.router)
```

- [ ] **Step 5: Run tests — PASS**

Run: `pytest tests/test_arch.py -v`
Expected: PASS 3/3

- [ ] **Step 6: Commit**

```bash
git add backend/routers/arch.py backend/db/schema.sql backend/main.py backend/tests/test_arch.py
git commit -m "feat: architecture save/load/delete endpoints"
```

---

### Task 4: Frontend — save/load + Arch gallery

**Files:**
- Modify: `frontend/src/api/client.ts` (add arch API calls)
- Create: `frontend/src/pages/ArchGallery.tsx`
- Modify: `frontend/src/pages/ArchMode.tsx` (toolbar: save button, diagram name input)
- Modify: `frontend/src/App.tsx` (add `/arch/gallery` route)

**Interfaces:**
- Consumes: `/arch` endpoints from Task 3
- Produces: `saveArchitecture(name, provider, nodes, edges)`, `listArchitectures(provider)`, `loadArchitecture(id)`; ArchMode toolbar with save; ArchGallery page

- [ ] **Step 1: Add API functions to client.ts**

```typescript
export async function saveArchitecture(name: string, provider: string, nodes: unknown[], edges: unknown[]) {
  const r = await fetch(`${base}/arch`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name, provider, nodes_json: JSON.stringify(nodes), edges_json: JSON.stringify(edges) })
  })
  return r.json()
}
export async function listArchitectures(provider?: string) {
  const qs = provider ? `?provider=${provider}` : ''
  return fetch(`${base}/arch${qs}`).then(r => r.json())
}
export async function loadArchitecture(id: string) {
  return fetch(`${base}/arch/${id}`).then(r => r.json())
}
export async function deleteArchitecture(id: string) {
  return fetch(`${base}/arch/${id}`, { method: 'DELETE' }).then(r => r.json())
}
```

- [ ] **Step 2: Add Save toolbar to ArchMode**

Add a top toolbar row below AppHeader: text input for diagram name + "Guardar" button. On click: call `saveArchitecture`, show brief success toast "Guardado ✓".

- [ ] **Step 3: Create ArchGallery.tsx**

List saved architectures for a provider. Each card shows name + date + "Abrir" / "Eliminar" buttons. "Abrir" navigates to `/arch?provider=X&id=Y` which loads nodes/edges into the canvas.

- [ ] **Step 4: Wire load-by-id in ArchMode**

In ArchMode, if `?id=` is present in search params, fetch the architecture on mount and populate `nodes`/`edges` state.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/pages/ArchGallery.tsx frontend/src/pages/ArchMode.tsx frontend/src/App.tsx
git commit -m "feat: save/load architecture diagrams; arch gallery page"
```
