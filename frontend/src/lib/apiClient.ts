import { supabase } from './supabaseClient'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

async function authHeader(): Promise<HeadersInit> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (typeof data.detail === 'string') return data.detail
    if (data.detail?.errors) return data.detail.errors.join('; ')
    return JSON.stringify(data)
  } catch {
    return `Erro ${response.status}`
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: await authHeader() })
  if (!response.ok) throw new Error(await extractErrorMessage(response))
  return response.json() as Promise<T>
}

export async function apiPostJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { ...(await authHeader()), 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(await extractErrorMessage(response))
  return response.json() as Promise<T>
}

export async function apiPostFile<T>(path: string, file: File): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: await authHeader(),
    body: formData,
  })
  if (!response.ok) throw new Error(await extractErrorMessage(response))
  return response.json() as Promise<T>
}
