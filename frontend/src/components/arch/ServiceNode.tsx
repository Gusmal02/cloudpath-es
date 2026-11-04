import { useRef, useState } from 'react'
import { Handle, Position, useReactFlow } from '@xyflow/react'

interface ServiceNodeData {
  icon: string
  label: string
  category: string
}

export function ServiceNode({ id, data }: { id: string; data: ServiceNodeData }) {
  const { deleteElements, updateNodeData } = useReactFlow()
  const [editing, setEditing] = useState(false)
  const [editValue, setEditValue] = useState(data.label)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleDelete(e: React.MouseEvent) {
    e.stopPropagation()
    deleteElements({ nodes: [{ id }] })
  }

  function handleDoubleClick(e: React.MouseEvent) {
    e.stopPropagation()
    setEditValue(data.label)
    setEditing(true)
    setTimeout(() => inputRef.current?.select(), 0)
  }

  function commitEdit() {
    const trimmed = editValue.trim()
    if (trimmed) updateNodeData(id, { ...data, label: trimmed })
    setEditing(false)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter') commitEdit()
    if (e.key === 'Escape') setEditing(false)
  }

  return (
    <div className="service-node">
      <Handle type="target" position={Position.Top} id="top-target" />
      <Handle type="source" position={Position.Top} id="top-source" />
      <Handle type="target" position={Position.Bottom} id="bottom-target" />
      <Handle type="source" position={Position.Bottom} id="bottom-source" />
      <Handle type="target" position={Position.Left} id="left-target" />
      <Handle type="source" position={Position.Left} id="left-source" />
      <Handle type="target" position={Position.Right} id="right-target" />
      <Handle type="source" position={Position.Right} id="right-source" />
      <button className="service-node__delete" onClick={handleDelete} title="Eliminar nodo">×</button>
      <div className="service-node__icon">{data.icon}</div>
      {editing ? (
        <input
          ref={inputRef}
          className="service-node__label-input"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={commitEdit}
          onKeyDown={handleKeyDown}
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <div className="service-node__label" onDoubleClick={handleDoubleClick} title="Doble clic para renombrar">
          {data.label}
        </div>
      )}
      <div className="service-node__category">{data.category}</div>
    </div>
  )
}
