export interface ClientOut {
  id: string
  name: string
  whatsapp_phone: string | null
  plan_status: string
}

export interface ClientUpdateIn {
  whatsapp_phone?: string | null
}
