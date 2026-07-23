import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useSession } from './lib/useSession'
import { apiGet } from './lib/apiClient'
import { AppHeader } from './components/AppHeader'
import { Landing } from './routes/Landing'
import { Login } from './routes/Login'
import { ConnectSource } from './routes/ConnectSource'
import { Report } from './routes/Report'
import { Settings } from './routes/Settings'
import { Plano } from './routes/Plano'
import type { ClientOut } from './types/client'
import './App.css'

function App() {
  const location = useLocation()
  const { session, loading } = useSession()
  // client fica null enquanto carrega OU enquanto não há sessão — nenhum
  // booleano de loading separado, pra não abrir uma janela de estado
  // inconsistente (session verdadeiro + client ainda null é sempre "carregando").
  const [client, setClient] = useState<ClientOut | null>(null)

  useEffect(() => {
    setClient(null)
    if (!session) return
    apiGet<ClientOut>('/me').then(setClient)
  }, [session])

  if (loading) return <div className="page">Carregando...</div>

  if (!session) {
    return (
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    )
  }

  if (!client) return <div className="page">Carregando...</div>

  const planActive = client.plan_status === 'active'
  const isHome = location.pathname === '/'

  if (!planActive) {
    return (
      <>
        {!isHome && <AppHeader showNav={false} />}
        <Routes>
          <Route path="/" element={<Landing loggedIn appHref="/plano" />} />
          <Route path="/plano" element={<Plano client={client} onPlanUpdated={setClient} />} />
          <Route path="*" element={<Navigate to="/plano" replace />} />
        </Routes>
      </>
    )
  }

  return (
    <>
      {!isHome && <AppHeader />}
      <Routes>
        <Route path="/" element={<Landing loggedIn appHref="/relatorio" />} />
        <Route path="/relatorio" element={<Report />} />
        <Route path="/conectar" element={<ConnectSource />} />
        <Route path="/configuracoes" element={<Settings />} />
        <Route path="/plano" element={<Plano client={client} onPlanUpdated={setClient} />} />
        <Route path="*" element={<Navigate to="/relatorio" replace />} />
      </Routes>
    </>
  )
}

export default App
