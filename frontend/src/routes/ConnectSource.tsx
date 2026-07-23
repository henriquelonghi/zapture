import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiPostFile, apiPostJson } from '../lib/apiClient'
import type { IngestionResultOut } from '../types/report'

type Method = 'upload' | 'sheets'

export function ConnectSource() {
  const navigate = useNavigate()
  const [method, setMethod] = useState<Method | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [spreadsheetId, setSpreadsheetId] = useState('')
  const [rangeName, setRangeName] = useState('A1:Z10000')
  const [error, setError] = useState<string | null>(null)
  const [warnings, setWarnings] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  async function handleUpload() {
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const result = await apiPostFile<IngestionResultOut>('/data-sources/upload', file)
      setWarnings(result.warnings)
      navigate('/relatorio')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar arquivo.')
    } finally {
      setLoading(false)
    }
  }

  async function handleConnectSheets() {
    setError(null)
    setLoading(true)
    try {
      const result = await apiPostJson<IngestionResultOut>('/data-sources/sheets/connect', {
        spreadsheet_id: spreadsheetId,
        range_name: rangeName,
      })
      setWarnings(result.warnings)
      navigate('/relatorio')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao conectar planilha.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Conecte a origem dos seus dados de venda</h1>

      {!method && (
        <div className="method-grid">
          <button className="method-card" onClick={() => setMethod('sheets')}>
            <span className="method-icon">📊</span>
            <strong>Google Sheets</strong>
            <p>Fica sincronizado sozinho toda vez que você abre o relatório.</p>
          </button>
          <button className="method-card" onClick={() => setMethod('upload')}>
            <span className="method-icon">📁</span>
            <strong>Upload de CSV/XLSX</strong>
            <p>Mais rápido pra começar, mas você precisa reenviar o arquivo pra atualizar.</p>
          </button>
        </div>
      )}

      {method === 'upload' && (
        <div className="method-form">
          <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          <button onClick={handleUpload} disabled={!file || loading}>
            {loading ? 'Enviando...' : 'Enviar arquivo'}
          </button>
          <button className="link-button" onClick={() => setMethod(null)}>
            Voltar
          </button>
        </div>
      )}

      {method === 'sheets' && (
        <div className="method-form">
          <label>
            ID da planilha
            <input
              value={spreadsheetId}
              onChange={(e) => setSpreadsheetId(e.target.value)}
              placeholder="encontrado na URL da planilha"
            />
          </label>
          <label>
            Intervalo
            <input value={rangeName} onChange={(e) => setRangeName(e.target.value)} />
          </label>
          <button onClick={handleConnectSheets} disabled={!spreadsheetId || loading}>
            {loading ? 'Conectando...' : 'Conectar planilha'}
          </button>
          <button className="link-button" onClick={() => setMethod(null)}>
            Voltar
          </button>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
      {warnings.length > 0 && (
        <ul className="warning-list">
          {warnings.map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
