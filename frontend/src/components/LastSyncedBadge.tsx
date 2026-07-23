import { Link } from 'react-router-dom'

interface LastSyncedBadgeProps {
  lastSyncedAt: string | null
  lastSyncLabel: string | null
}

export function LastSyncedBadge({ lastSyncedAt, lastSyncLabel }: LastSyncedBadgeProps) {
  if (!lastSyncedAt) {
    return (
      <span className="last-synced-badge">
        <span className="last-synced-dot offline" />
        Nenhuma fonte de dados conectada ainda — <Link to="/conectar">conectar agora</Link>
      </span>
    )
  }

  const formatted = new Date(lastSyncedAt).toLocaleString('pt-BR')
  return (
    <span className="last-synced-badge">
      <span className="last-synced-dot" />
      dado de: {lastSyncLabel ?? 'fonte desconhecida'}, sincronizado em {formatted}
    </span>
  )
}
