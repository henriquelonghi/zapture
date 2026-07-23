import { useState } from 'react'
import { apiGet } from '../lib/apiClient'
import type { AuthorizeUrlOut } from '../types/integrations'

type Platform = 'mercado_livre' | 'shopify' | 'nuvemshop'

const PLATFORMS: { id: Platform; name: string; description: string }[] = [
  { id: 'mercado_livre', name: 'Mercado Livre', description: 'Autorize o acesso oficial à sua conta de vendedor.' },
  { id: 'shopify', name: 'Shopify', description: 'Informe o domínio da sua loja e autorize o app.' },
  { id: 'nuvemshop', name: 'Nuvemshop', description: 'Autorize o acesso oficial à sua loja.' },
]

export function ConnectSource() {
  const [shopDomain, setShopDomain] = useState('')
  const [loadingPlatform, setLoadingPlatform] = useState<Platform | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function connect(platform: Platform) {
    setError(null)

    if (platform === 'shopify' && !shopDomain.trim()) {
      setError('Informe o domínio da sua loja Shopify (ex: sualoja.myshopify.com).')
      return
    }

    setLoadingPlatform(platform)
    try {
      const query = platform === 'shopify' ? `?shop=${encodeURIComponent(shopDomain.trim())}` : ''
      const result = await apiGet<AuthorizeUrlOut>(`/integrations/${platform}/authorize${query}`)
      window.location.href = result.authorize_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar a conexão.')
      setLoadingPlatform(null)
    }
  }

  return (
    <div className="page">
      <h1>Conecte a origem dos seus dados de venda</h1>
      <p>Cada plataforma exige autorização oficial via OAuth — a Zapture nunca pede sua senha.</p>

      <div className="method-grid">
        {PLATFORMS.map((platform) => (
          <div className="method-card" key={platform.id} style={{ cursor: 'default' }}>
            <strong>{platform.name}</strong>
            <p>{platform.description}</p>

            {platform.id === 'shopify' && (
              <input
                value={shopDomain}
                onChange={(e) => setShopDomain(e.target.value)}
                placeholder="sualoja.myshopify.com"
              />
            )}

            <button onClick={() => connect(platform.id)} disabled={loadingPlatform !== null}>
              {loadingPlatform === platform.id ? 'Redirecionando...' : `Conectar ${platform.name}`}
            </button>
          </div>
        ))}
      </div>

      {error && <p className="error-text">{error}</p>}
    </div>
  )
}
