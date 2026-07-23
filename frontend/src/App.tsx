import { Navigate, Route, Routes } from 'react-router-dom'
import { useSession } from './lib/useSession'
import { Landing } from './routes/Landing'
import { Login } from './routes/Login'
import { ConnectSource } from './routes/ConnectSource'
import { Report } from './routes/Report'
import './App.css'

function App() {
  const { session, loading } = useSession()

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

  return (
    <Routes>
      <Route path="/relatorio" element={<Report />} />
      <Route path="/conectar" element={<ConnectSource />} />
      <Route path="*" element={<Navigate to="/relatorio" replace />} />
    </Routes>
  )
}

export default App
