type DecorProps = {
  className?: string
}

function BarsWidget({ className }: DecorProps) {
  return (
    <div className={`decor-card decor-bars ${className ?? ''}`}>
      <span className="decor-card-label">Faturamento</span>
      <div className="decor-bars-row">
        <span className="decor-bar" style={{ height: '38%' }} />
        <span className="decor-bar" style={{ height: '62%' }} />
        <span className="decor-bar" style={{ height: '48%' }} />
        <span className="decor-bar decor-bar-accent" style={{ height: '88%' }} />
      </div>
      <span className="decor-card-delta positive">+18%</span>
    </div>
  )
}

function SparklineWidget({ className }: DecorProps) {
  return (
    <div className={`decor-card decor-sparkline ${className ?? ''}`}>
      <span className="decor-card-label">Ticket médio</span>
      <svg viewBox="0 0 100 36" preserveAspectRatio="none" className="decor-sparkline-svg" aria-hidden="true">
        <defs>
          <linearGradient id="decor-spark-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="var(--zapture-blue)" stopOpacity="0.35" />
            <stop offset="1" stopColor="var(--zapture-blue)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d="M0,30 L15,24 L30,27 L45,16 L60,20 L75,8 L100,4 L100,36 L0,36 Z" fill="url(#decor-spark-fill)" />
        <polyline
          points="0,30 15,24 30,27 45,16 60,20 75,8 100,4"
          fill="none"
          stroke="var(--zapture-blue)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  )
}

function TableWidget({ className }: DecorProps) {
  const rows = [
    { name: 'Capa de celular', value: '+32%', trend: 'positive' },
    { name: 'Carregador portátil', value: '+9%', trend: 'positive' },
    { name: 'Fone XYZ', value: '-18%', trend: 'negative' },
  ]
  return (
    <div className={`decor-card decor-table ${className ?? ''}`}>
      <span className="decor-card-label">Ranking</span>
      {rows.map((row) => (
        <div className="decor-table-row" key={row.name}>
          <span>{row.name}</span>
          <span className={row.trend}>{row.value}</span>
        </div>
      ))}
    </div>
  )
}

function KpiChip({ text, className }: DecorProps & { text: string }) {
  return <span className={`decor-chip ${className ?? ''}`}>{text}</span>
}

export function HeroInsightsDecor() {
  return (
    <div className="decor-layer decor-layer-hero" aria-hidden="true">
      <BarsWidget className="decor-pos-bars decor-float-a" />
      <SparklineWidget className="decor-pos-spark decor-float-b" />
      <TableWidget className="decor-pos-table decor-float-a" />
      <KpiChip text="R$ 4.280" className="decor-pos-chip-1 decor-float-b" />
      <KpiChip text="+18%" className="decor-pos-chip-2 decor-float-a" />
    </div>
  )
}

export function BandInsightsDecor() {
  return (
    <div className="decor-layer decor-layer-band" aria-hidden="true">
      <SparklineWidget className="decor-pos-band-spark decor-float-a decor-on-dark" />
      <KpiChip text="+24%" className="decor-pos-band-chip decor-float-b decor-on-dark" />
    </div>
  )
}
