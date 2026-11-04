import { cloudServices, type CloudService } from '../../data/cloudServices'

interface Props {
  provider: string
  onAdd: (svc: CloudService) => void
}

export function ServicePalette({ provider, onAdd }: Props) {
  const services = cloudServices[provider] ?? []
  const grouped = services.reduce<Record<string, CloudService[]>>((acc, svc) => {
    if (!acc[svc.category]) acc[svc.category] = []
    acc[svc.category].push(svc)
    return acc
  }, {})

  return (
    <aside className="arch-palette">
      {Object.entries(grouped).map(([category, svcs]) => (
        <div key={category} className="arch-palette-group">
          <div className="arch-palette-category">{category}</div>
          {svcs.map((svc) => (
            <button
              key={svc.id}
              className="arch-palette-item"
              onClick={() => onAdd(svc)}
            >
              <span className="arch-palette-item-icon">{svc.icon}</span>
              <span className="arch-palette-item-text">
                <span className="arch-palette-item-label">{svc.label}</span>
                <span className="arch-palette-item-desc">{svc.description}</span>
              </span>
            </button>
          ))}
        </div>
      ))}
    </aside>
  )
}
