interface LastSyncedBadgeProps {
  lastSyncedAt: string | null
  lastSyncLabel: string | null
}

export function LastSyncedBadge({ lastSyncedAt, lastSyncLabel }: LastSyncedBadgeProps) {
  if (!lastSyncedAt) {
    return <span className="last-synced-badge">Nenhuma fonte de dados conectada ainda</span>
  }

  const formatted = new Date(lastSyncedAt).toLocaleString('pt-BR')
  return (
    <span className="last-synced-badge">
      dado de: {lastSyncLabel ?? 'fonte desconhecida'}, sincronizado em {formatted}
    </span>
  )
}
