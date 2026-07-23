import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { isSupabaseConfigured, supabase } from '../lib/supabaseClient'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSignIn(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setInfo(null)
    setLoading(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setLoading(false)
    if (error) setError(error.message)
  }

  async function handleSignUp() {
    setError(null)
    setInfo(null)
    setLoading(true)
    const { error } = await supabase.auth.signUp({ email, password })
    setLoading(false)
    if (error) {
      setError(error.message)
      return
    }
    setInfo('Conta criada. Se a confirmação por e-mail estiver ativada no seu projeto Supabase, confirme antes de entrar.')
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSignIn}>
        <Link to="/" className="link-button" style={{ alignSelf: 'flex-start' }}>
          ← Voltar
        </Link>
        <h1>Entrar</h1>
        {!isSupabaseConfigured && (
          <p className="warning-list">
            Supabase ainda não configurado — copie <code>frontend/.env.example</code> para <code>.env</code>,
            preencha com as chaves do seu projeto e reinicie o servidor de dev.
          </p>
        )}
        <label>
          E-mail
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Senha
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </label>
        {error && <p className="error-text">{error}</p>}
        {info && <p className="info-text">{info}</p>}
        <div className="auth-actions">
          <button type="submit" disabled={loading}>
            Entrar
          </button>
          <button type="button" onClick={handleSignUp} disabled={loading}>
            Criar conta
          </button>
        </div>
      </form>
    </div>
  )
}
