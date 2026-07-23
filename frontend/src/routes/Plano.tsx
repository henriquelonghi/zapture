import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiGet, apiPostJson } from '../lib/apiClient'
import type { ClientOut } from '../types/client'
import type { CheckoutSessionOut, PlanOut } from '../types/billing'

function formatPrice(cents: number, currency: string): string {
  return (cents / 100).toLocaleString('pt-BR', { style: 'currency', currency })
}

function intervalLabel(interval: string): string {
  return interval === 'month' ? 'mês' : interval
}

type PlanoProps = {
  client: ClientOut | null
  onPlanUpdated: (client: ClientOut) => void
}

export function Plano({ client, onPlanUpdated }: PlanoProps) {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [plans, setPlans] = useState<PlanOut[]>([])
  const [checkoutLoading, setCheckoutLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [confirming, setConfirming] = useState(searchParams.get('checkout') === 'sucesso')

  const isActive = client?.plan_status === 'active'
  const checkoutCanceled = searchParams.get('checkout') === 'cancelado'

  useEffect(() => {
    apiGet<PlanOut[]>('/billing/plans').then(setPlans)
  }, [])

  useEffect(() => {
    if (!confirming) return

    let attempts = 0
    const interval = setInterval(async () => {
      attempts += 1
      try {
        const updated = await apiGet<ClientOut>('/me')
        onPlanUpdated(updated)
        if (updated.plan_status === 'active') {
          clearInterval(interval)
          setConfirming(false)
          navigate('/conectar')
        } else if (attempts >= 10) {
          clearInterval(interval)
          setConfirming(false)
        }
      } catch {
        clearInterval(interval)
        setConfirming(false)
      }
    }, 1500)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [confirming])

  async function handleSubscribe() {
    setError(null)
    setCheckoutLoading(true)
    try {
      const session = await apiPostJson<CheckoutSessionOut>('/billing/checkout', {})
      window.location.href = session.checkout_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar o pagamento.')
      setCheckoutLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Seu plano</h1>
      </div>

      {isActive && (
        <div className="method-form">
          <p>Plano ativo. Agora é só conectar sua loja.</p>
          <button className="btn-accent" onClick={() => navigate('/conectar')}>
            Conectar fonte de dados
          </button>
        </div>
      )}

      {!isActive && confirming && <p className="empty-state">Confirmando pagamento...</p>}

      {!isActive && !confirming && (
        <>
          {checkoutCanceled && <p className="warning-list">Pagamento cancelado — pode tentar de novo quando quiser.</p>}
          {plans.map((plan) => (
            <div className="pricing-card" key={plan.id}>
              <p className="pricing-value">
                <strong>{formatPrice(plan.price_cents, plan.currency)}</strong> / {intervalLabel(plan.interval)}
              </p>
              <ul>
                <li>Conecte sua conta do Mercado Livre, Shopify ou Nuvemshop</li>
                <li>Dados em tempo real, direto da API oficial</li>
                <li>Resumo periódico automático via WhatsApp</li>
                <li>Relatório dinâmico sempre disponível</li>
              </ul>
              <button className="btn-accent" onClick={handleSubscribe} disabled={checkoutLoading}>
                {checkoutLoading ? 'Redirecionando...' : 'Assinar'}
              </button>
            </div>
          ))}
          {error && <p className="error-text">{error}</p>}
        </>
      )}
    </div>
  )
}
