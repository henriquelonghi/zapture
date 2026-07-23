interface MetricCardProps {
  label: string
  value: string
  variationPct: number | null
}

export function MetricCard({ label, value, variationPct }: MetricCardProps) {
  const hasVariation = variationPct !== null
  const isPositive = (variationPct ?? 0) >= 0

  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      {hasVariation && (
        <span className={`metric-variation ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '▲' : '▼'} {Math.abs(variationPct as number).toFixed(1)}%
        </span>
      )}
    </div>
  )
}
