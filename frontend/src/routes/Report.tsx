import { useEffect, useState, type FormEvent } from 'react'
import { apiGet } from '../lib/apiClient'
import { InsightList } from '../components/InsightList'
import { LastSyncedBadge } from '../components/LastSyncedBadge'
import { MetricCard } from '../components/MetricCard'
import type { ReportOut } from '../types/report'

function formatCurrency(value: number): string {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10)
}

function defaultRange(days: number): { start: string; end: string } {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - (days - 1))
  return { start: toIsoDate(start), end: toIsoDate(end) }
}

function isoToBr(iso: string): string {
  const [y, m, d] = iso.split('-')
  return y && m && d ? `${d}/${m}/${y}` : ''
}

function brToIso(br: string): string | null {
  const match = br.match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
  if (!match) return null
  const [, d, m, y] = match
  const day = Number(d)
  const month = Number(m)
  if (month < 1 || month > 12 || day < 1 || day > 31) return null
  return `${y}-${m}-${d}`
}

function maskBrDate(raw: string): string {
  const digits = raw.replace(/\D/g, '').slice(0, 8)
  const parts = [digits.slice(0, 2), digits.slice(2, 4), digits.slice(4, 8)].filter(Boolean)
  return parts.join('/')
}

const PRESETS = [
  { label: '7 dias', days: 7 },
  { label: '30 dias', days: 30 },
  { label: '90 dias', days: 90 },
]

export function Report() {
  const initialRange = defaultRange(30)
  const [startText, setStartText] = useState(isoToBr(initialRange.start))
  const [endText, setEndText] = useState(isoToBr(initialRange.end))
  const [appliedRange, setAppliedRange] = useState(initialRange)
  const [report, setReport] = useState<ReportOut | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dateError, setDateError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    const params = new URLSearchParams({
      period_start: appliedRange.start,
      period_end: appliedRange.end,
    })
    apiGet<ReportOut>(`/report?${params.toString()}`)
      .then((data) => {
        if (!cancelled) setReport(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Erro ao carregar relatório.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [appliedRange])

  function applyPreset(days: number) {
    const range = defaultRange(days)
    setStartText(isoToBr(range.start))
    setEndText(isoToBr(range.end))
    setDateError(null)
    setAppliedRange(range)
  }

  function handleStartTextChange(raw: string) {
    setStartText(maskBrDate(raw))
  }

  function handleEndTextChange(raw: string) {
    setEndText(maskBrDate(raw))
  }

  function applyCustomRange(event: FormEvent) {
    event.preventDefault()
    const startIso = brToIso(startText)
    const endIso = brToIso(endText)
    if (!startIso || !endIso) {
      setDateError('Data inválida — use o formato dd/mm/aaaa.')
      return
    }
    if (startIso > endIso) {
      setDateError('A data inicial não pode ser depois da data final.')
      return
    }
    setDateError(null)
    setAppliedRange({ start: startIso, end: endIso })
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Relatório</h1>
      </div>

      <form className="date-filter" onSubmit={applyCustomRange}>
        <div className="date-filter-presets">
          {PRESETS.map((preset) => (
            <button
              type="button"
              key={preset.days}
              className={appliedRange.start === defaultRange(preset.days).start ? 'preset-active' : ''}
              onClick={() => applyPreset(preset.days)}
            >
              {preset.label}
            </button>
          ))}
        </div>
        <label>
          De
          <input
            type="text"
            inputMode="numeric"
            placeholder="dd/mm/aaaa"
            maxLength={10}
            value={startText}
            onChange={(e) => handleStartTextChange(e.target.value)}
          />
        </label>
        <label>
          Até
          <input
            type="text"
            inputMode="numeric"
            placeholder="dd/mm/aaaa"
            maxLength={10}
            value={endText}
            onChange={(e) => handleEndTextChange(e.target.value)}
          />
        </label>
        <button type="submit" className="btn-accent">
          Aplicar
        </button>
      </form>
      {dateError && <p className="error-text">{dateError}</p>}

      {loading && (
        <div className="skeleton-grid" aria-label="Carregando relatório" role="status">
          {Array.from({ length: 9 }).map((_, i) => (
            <div className="skeleton-card" key={i} />
          ))}
        </div>
      )}
      {error && <p className="error-text">{error}</p>}

      {report && (
        <>
          <LastSyncedBadge lastSyncedAt={report.last_synced_at} lastSyncLabel={report.last_sync_label} />

          {report.validation_warnings.length > 0 && (
            <ul className="warning-list">
              {report.validation_warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          )}

          <section>
            <h2>Insights</h2>
            <InsightList insights={report.insights} />
          </section>

          <section className="metric-grid">
            <MetricCard
              label="Faturamento"
              value={formatCurrency(report.revenue.total_current)}
              variationPct={report.revenue.variation_pct}
            />
            <MetricCard
              label="Ticket médio"
              value={report.ticket.average_current !== null ? formatCurrency(report.ticket.average_current) : '—'}
              variationPct={report.ticket.variation_pct}
            />
            <MetricCard
              label="Pedidos"
              value={String(report.volume.orders_current)}
              variationPct={report.volume.variation_pct}
            />
            <MetricCard
              label="Unidades vendidas"
              value={String(report.units.units_current)}
              variationPct={report.units.variation_pct}
            />
            <MetricCard
              label="Margem agregada"
              value={
                report.aggregate_margin.margin_pct !== null
                  ? `${report.aggregate_margin.margin_pct.toFixed(1)}%`
                  : 'sem dado de custo'
              }
              variationPct={null}
            />
            <MetricCard
              label="Clientes novos"
              value={String(report.new_customers.new_customers_count)}
              variationPct={null}
            />
            <MetricCard
              label="Clientes recorrentes"
              value={String(report.new_customers.returning_customers_count)}
              variationPct={null}
            />
            <MetricCard
              label="Produto mais vendido"
              value={
                report.bestseller
                  ? `${report.bestseller.product_name} (${report.bestseller.units_sold} un.)`
                  : '—'
              }
              variationPct={null}
            />
            <MetricCard
              label="Venda de maior preço"
              value={
                report.highest_priced_sale
                  ? `${report.highest_priced_sale.product_name} — ${formatCurrency(report.highest_priced_sale.unit_price)}`
                  : '—'
              }
              variationPct={null}
            />
          </section>

          {report.negative_margin_products.length > 0 && (
            <section>
              <h2>Produtos com margem negativa</h2>
              <ul className="alert-list">
                {report.negative_margin_products.map((p) => (
                  <li key={p.product_key}>
                    {p.product_name}, margem de {formatCurrency(p.margin_value)} ({p.margin_pct?.toFixed(1)}%)
                  </li>
                ))}
              </ul>
            </section>
          )}

          {report.churned_customers.length > 0 && (
            <section>
              <h2>Clientes que sumiram</h2>
              <ul>
                {report.churned_customers.slice(0, 10).map((c) => (
                  <li key={c.customer_id}>
                    {c.customer_id}, {c.days_since_last_purchase} dias sem comprar (padrão dele: ~
                    {Math.round(c.avg_interval_days)} dias)
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section>
            <h2>Ranking de produtos</h2>
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>Faturamento</th>
                  <th>Variação</th>
                </tr>
              </thead>
              <tbody>
                {report.ranking_products.slice(0, 10).map((entry) => (
                  <tr key={entry.name}>
                    <td>{entry.name}</td>
                    <td>{formatCurrency(entry.revenue_current)}</td>
                    <td className={entry.variation_abs >= 0 ? 'positive' : 'negative'}>
                      {entry.variation_pct !== null ? `${entry.variation_pct.toFixed(1)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section>
            <h2>Ranking de categorias</h2>
            <table className="ranking-table">
              <thead>
                <tr>
                  <th>Categoria</th>
                  <th>Faturamento</th>
                  <th>Variação</th>
                </tr>
              </thead>
              <tbody>
                {report.ranking_categories.slice(0, 10).map((entry) => (
                  <tr key={entry.name}>
                    <td>{entry.name}</td>
                    <td>{formatCurrency(entry.revenue_current)}</td>
                    <td className={entry.variation_abs >= 0 ? 'positive' : 'negative'}>
                      {entry.variation_pct !== null ? `${entry.variation_pct.toFixed(1)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  )
}
