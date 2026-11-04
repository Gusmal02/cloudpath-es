import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { deleteArchitecture, listArchitectures } from '../api/client'
import { AppHeader } from '../components/AppHeader'
import type { Provider } from '../types/exam'

interface ArchSummary {
  id: string
  name: string
  provider: string
  created_at: string
}

export function ArchGallery() {
  const [params] = useSearchParams()
  const provider = (params.get('provider') ?? 'AWS') as Provider
  const navigate = useNavigate()
  const [archs, setArchs] = useState<ArchSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listArchitectures(provider)
      .then(setArchs)
      .catch(() => setArchs([]))
      .finally(() => setLoading(false))
  }, [provider])

  async function handleDelete(id: string) {
    await deleteArchitecture(id)
    setArchs((prev) => prev.filter((a) => a.id !== id))
  }

  return (
    <>
      <AppHeader title="Mis Arquitecturas" provider={provider} backTo="/" />
      <main className="arch-gallery">
        <div className="arch-gallery-header">
          <button
            className="btn btn--primary"
            onClick={() => navigate(`/arch?provider=${provider}`)}
          >
            + Nueva arquitectura
          </button>
        </div>
        {loading && <p className="loading">Cargando…</p>}
        {!loading && archs.length === 0 && (
          <p className="arch-gallery-empty">
            Aún no tienes arquitecturas guardadas. ¡Crea la primera!
          </p>
        )}
        <div className="arch-gallery-grid">
          {archs.map((arch) => (
            <div key={arch.id} className="arch-card">
              <div className="arch-card-body">
                <h3 className="arch-card-name">{arch.name}</h3>
                <p className="arch-card-date">
                  {new Date(arch.created_at).toLocaleDateString('es-MX', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </p>
              </div>
              <div className="arch-card-actions">
                <button
                  className="btn btn--primary btn--sm"
                  onClick={() => navigate(`/arch?provider=${provider}&id=${arch.id}`)}
                >
                  Abrir
                </button>
                <button
                  className="btn btn--ghost btn--sm"
                  onClick={() => handleDelete(arch.id)}
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </>
  )
}
