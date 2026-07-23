import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey)

if (!isSupabaseConfigured) {
  console.warn(
    'VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY não configurados — copie frontend/.env.example para .env e preencha com os dados do seu projeto Supabase. Usando um projeto placeholder por enquanto (login não vai funcionar).',
  )
}

// createClient exige uma URL válida mesmo sem credenciais reais — sem isso o app
// inteiro quebra no carregamento em vez de mostrar a tela de login normalmente.
export const supabase = createClient(supabaseUrl || 'https://placeholder.supabase.co', supabaseAnonKey || 'placeholder')
