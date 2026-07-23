import { Logo } from './Logo'

const MESSAGES = [
  { time: '08:03', text: 'Bom dia! Aqui está o resumo de ontem 👋' },
  {
    time: '08:03',
    text: '💰 Faturamento: R$ 4.280 (+12% vs. semana passada)\n🛒 42 pedidos\n🎯 Ticket médio: R$ 101,90',
  },
  {
    time: '08:03',
    text: "⚠️ Atenção: margem do produto \"Fone XYZ\" ficou negativa essa semana. Vale revisar o preço.",
  },
]

export function WhatsAppMockup() {
  return (
    <div className="wa-frame" role="img" aria-label="Simulação de conversa no WhatsApp recebendo o resumo automático">
      <div className="wa-screen">
        <div className="wa-header">
          <span className="wa-avatar">
            <Logo size={16} withWordmark={false} />
          </span>
          <span className="wa-header-text">
            <strong>Zapture</strong>
            <small>conta comercial</small>
          </span>
        </div>
        <div className="wa-messages">
          {MESSAGES.map((message, index) => (
            <div className="wa-bubble" key={index}>
              <p>{message.text}</p>
              <span className="wa-timestamp">{message.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
