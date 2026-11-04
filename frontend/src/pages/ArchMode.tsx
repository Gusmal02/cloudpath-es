import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { analyzeArchitecture, loadArchitecture, saveArchitecture } from '../api/client'
import type { WhatIfResult } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import { ServiceNode } from '../components/arch/ServiceNode'
import { ServicePalette } from '../components/arch/ServicePalette'
import { WhatIfPanel } from '../components/arch/WhatIfPanel'
import type { CloudService } from '../data/cloudServices'
import type { Provider } from '../types/exam'
import './ArchMode.css'

const nodeTypes = { service: ServiceNode }

function ArchModeInner() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const archId = params.get('id')
  const navigate = useNavigate()

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const { screenToFlowPosition } = useReactFlow()

  const [whatIfOpen, setWhatIfOpen] = useState(false)
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null)
  const [whatIfLoading, setWhatIfLoading] = useState(false)
  const [whatIfError, setWhatIfError] = useState<string | null>(null)

  useEffect(() => {
    if (!archId) return
    loadArchitecture(archId).then((arch) => {
      if (arch.detail) return
      setNodes(JSON.parse(arch.nodes_json))
      setEdges(JSON.parse(arch.edges_json))
    })
  }, [archId, setNodes, setEdges])

  const onConnect = useCallback(
    (params: Parameters<typeof addEdge>[0]) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  function handleAddService(svc: CloudService) {
    const position = screenToFlowPosition({ x: window.innerWidth / 2, y: window.innerHeight / 2 })
    setNodes((nds) => [
      ...nds,
      {
        id: `${svc.id}-${Date.now()}`,
        type: 'service',
        position,
        data: { icon: svc.icon, label: svc.label, category: svc.category },
      },
    ])
  }

  async function handleAnalyze() {
    setWhatIfOpen(true)
    setWhatIfLoading(true)
    setWhatIfError(null)
    setWhatIfResult(null)
    try {
      const result = await analyzeArchitecture(nodes, edges, provider)
      setWhatIfResult(result)
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Error al analizar la arquitectura'
      setWhatIfError(msg)
    } finally {
      setWhatIfLoading(false)
    }
  }

  async function handleSave() {
    const name = (document.getElementById('arch-name') as HTMLInputElement)?.value?.trim()
    if (!name) { alert('Escribe un nombre para el diagrama'); return }
    if (nodes.length === 0) { alert('Agrega al menos un servicio al diagrama'); return }
    await saveArchitecture(name, provider, nodes, edges)
    const btn = document.getElementById('arch-save-btn') as HTMLButtonElement
    if (btn) { btn.textContent = 'Guardado ✓'; setTimeout(() => { btn.textContent = 'Guardar' }, 2000) }
  }

  return (
    <>
      <AppHeader title="Simulador de Arquitecturas" provider={provider} />
      <div className="arch-toolbar">
        <input id="arch-name" className="arch-name-input" placeholder="Nombre del diagrama…" defaultValue="" />
        <button id="arch-save-btn" className="btn btn--primary btn--sm" onClick={handleSave}>Guardar</button>
        <button className="btn btn--ghost btn--sm" onClick={() => navigate(`/arch/gallery?provider=${provider}`)}>
          Mis arquitecturas
        </button>
        <button
          className="btn btn--ghost btn--sm arch-analyze-btn"
          onClick={handleAnalyze}
          disabled={whatIfLoading || nodes.length === 0}
          title={nodes.length === 0 ? 'Agrega servicios al diagrama primero' : 'Analizar arquitectura con IA'}
        >
          {whatIfLoading ? 'Analizando…' : 'Analizar con IA ✦'}
        </button>
      </div>
      <div className={`arch-layout${whatIfOpen ? ' arch-layout--with-panel' : ''}`}>
        <ServicePalette provider={provider} onAdd={handleAddService} />
        <div className="arch-canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
        {whatIfOpen && (
          <WhatIfPanel
            result={whatIfResult}
            loading={whatIfLoading}
            error={whatIfError}
            diagramName={(document.getElementById('arch-name') as HTMLInputElement)?.value ?? ''}
            provider={provider}
            onClose={() => setWhatIfOpen(false)}
          />
        )}
      </div>
    </>
  )
}

export function ArchMode() {
  return (
    <ReactFlowProvider>
      <ArchModeInner />
    </ReactFlowProvider>
  )
}
