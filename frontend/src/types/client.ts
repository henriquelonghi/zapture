export interface ClientOut {
  id: string
  name: string
  whatsapp_phone: string | null
}

export interface ClientUpdateIn {
  whatsapp_phone?: string | null
}
