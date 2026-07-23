type Metric = {
  label: string
  value: string
  variation?: string
  positive?: boolean
}

const METRICS: Metric[] = [
  { label: 'Faturamento', value: 'R$ 4.280', variation: '+12%', positive: true },
  { label: 'Ticket médio', value: 'R$ 101,90', variation: '+4%', positive: true },
  { label: 'Pedidos', value: '42', variation: '-3%', positive: false },
  { label: 'Unidades vendidas', value: '58', variation: '+7%', positive: true },
  { label: 'Margem agregada', value: '34,2%' },
  { label: 'Produto mais vendido', value: 'Capa de celular (14 un.)' },
  { label: 'Venda de maior preço', value: 'Fone XYZ — R$ 249,90' },
]

const RANKING = [
  { product: 'Capa de celular', variation: '+32%', positive: true },
  { product: 'Carregador portátil', variation: '+9%', positive: true },
  { product: 'Fone XYZ', variation: '-18%', positive: false },
]

export function ReportPreview() {
  return (
    <div className="report-preview">
      <div className="report-preview-bar">
        <span className="report-preview-dot" />
        <span className="report-preview-dot" />
        <span className="report-preview-dot" />
        <span className="report-preview-url">zapture.app/relatorio</span>
      </div>
      <div className="report-preview-body">
        <div className="report-preview-header">
          <h3>Relatório de faturamento</h3>
          <span className="report-preview-sync">Atualizado agora · Mercado Livre (tempo real)</span>
        </div>

        <div className="report-preview-metrics">
          {METRICS.map((metric) => (
            <div className="report-preview-metric" key={metric.label}>
              <span className="report-preview-label">{metric.label}</span>
              <span className="report-preview-value">{metric.value}</span>
              {metric.variation && (
                <span className={metric.positive ? 'positive' : 'negative'}>{metric.variation}</span>
              )}
            </div>
          ))}
        </div>

        <div className="report-preview-alerts">
          <span>⚠️ Fone XYZ está com margem negativa</span>
          <span>👋 3 clientes sumiram</span>
        </div>

        <table className="report-preview-table">
          <thead>
            <tr>
              <th>Produto</th>
              <th>Variação</th>
            </tr>
          </thead>
          <tbody>
            {RANKING.map((row) => (
              <tr key={row.product}>
                <td>{row.product}</td>
                <td className={row.positive ? 'positive' : 'negative'}>{row.variation}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="report-preview-footnote">
          <span>🆕 9 clientes novos</span>
          <span>🔁 14 recorrentes</span>
        </div>
      </div>
    </div>
  )
}
