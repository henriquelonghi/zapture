import { useEffect, useState, type FormEvent } from 'react'
import { apiGet, apiPatchJson, apiPutJson } from '../lib/apiClient'
import type { ClientOut } from '../types/client'
import type { ProductOut } from '../types/product'

export function Settings() {
  const [phone, setPhone] = useState('')
  const [phoneSaving, setPhoneSaving] = useState(false)
  const [phoneError, setPhoneError] = useState<string | null>(null)
  const [phoneSaved, setPhoneSaved] = useState(false)

  const [products, setProducts] = useState<ProductOut[]>([])
  const [productsLoading, setProductsLoading] = useState(true)
  const [costDrafts, setCostDrafts] = useState<Record<string, string>>({})
  const [savingProductId, setSavingProductId] = useState<string | null>(null)
  const [productError, setProductError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<ClientOut>('/me').then((data) => setPhone(data.whatsapp_phone ?? ''))
  }, [])

  useEffect(() => {
    apiGet<ProductOut[]>('/products')
      .then(setProducts)
      .finally(() => setProductsLoading(false))
  }, [])

  async function savePhone(event: FormEvent) {
    event.preventDefault()
    setPhoneError(null)
    setPhoneSaved(false)
    setPhoneSaving(true)
    try {
      const updated = await apiPatchJson<ClientOut>('/me', { whatsapp_phone: phone.trim() || null })
      setPhone(updated.whatsapp_phone ?? '')
      setPhoneSaved(true)
    } catch (err) {
      setPhoneError(err instanceof Error ? err.message : 'Erro ao salvar telefone.')
    } finally {
      setPhoneSaving(false)
    }
  }

  async function saveCost(product: ProductOut) {
    const draft = costDrafts[product.id]
    const value = Number(draft)
    if (!draft || Number.isNaN(value) || value < 0) {
      setProductError('Custo inválido.')
      return
    }
    setProductError(null)
    setSavingProductId(product.id)
    try {
      const updated = await apiPutJson<ProductOut>(`/products/${product.id}/cost`, { unit_cost: value })
      setProducts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)))
      setCostDrafts((prev) => ({ ...prev, [product.id]: '' }))
    } catch (err) {
      setProductError(err instanceof Error ? err.message : 'Erro ao salvar custo.')
    } finally {
      setSavingProductId(null)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>Configurações</h1>
      </div>

      <section>
        <h2>Número de WhatsApp</h2>
        <p>Pra onde o resumo periódico automático é enviado.</p>
        <form className="method-form" onSubmit={savePhone}>
          <label>
            Telefone (formato internacional, só dígitos)
            <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="5511999998888" />
          </label>
          <button type="submit" className="btn-accent" disabled={phoneSaving}>
            {phoneSaving ? 'Salvando...' : 'Salvar'}
          </button>
          {phoneSaved && <span className="positive">Salvo!</span>}
        </form>
        {phoneError && <p className="error-text">{phoneError}</p>}
      </section>

      <section>
        <h2>Custo dos produtos</h2>
        <p>
          Necessário pra calcular margem — sem custo cadastrado, a margem desse produto fica indisponível no
          relatório.
        </p>
        {productsLoading && <p className="empty-state">Carregando produtos...</p>}
        {!productsLoading && products.length === 0 && (
          <p className="empty-state">Nenhum produto ainda — conecte uma fonte de dados primeiro.</p>
        )}
        {products.length > 0 && (
          <table className="ranking-table">
            <thead>
              <tr>
                <th>Produto</th>
                <th>SKU</th>
                <th>Custo unitário</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td>{product.sku ?? '—'}</td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder={product.unit_cost !== null ? String(product.unit_cost) : 'sem custo'}
                      value={costDrafts[product.id] ?? ''}
                      onChange={(e) => setCostDrafts((prev) => ({ ...prev, [product.id]: e.target.value }))}
                    />
                  </td>
                  <td>
                    <button
                      className="btn-accent"
                      onClick={() => saveCost(product)}
                      disabled={savingProductId === product.id}
                    >
                      {savingProductId === product.id ? 'Salvando...' : 'Salvar'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {productError && <p className="error-text">{productError}</p>}
      </section>
    </div>
  )
}
