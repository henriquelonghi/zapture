import type { InsightOut } from '../types/report'

export function InsightList({ insights }: { insights: InsightOut[] }) {
  if (insights.length === 0) {
    return <p className="empty-state">Nenhum insight relevante pro período ainda.</p>
  }

  return (
    <ul className="insight-list">
      {insights.map((insight) => (
        <li key={insight.key} className="insight-item">
          <strong>{insight.title}</strong>
          <p>{insight.description}</p>
        </li>
      ))}
    </ul>
  )
}
