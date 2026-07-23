import { Link } from 'react-router-dom'
import { Logo } from '../components/Logo'
import { WhatsAppMockup } from '../components/WhatsAppMockup'
import { FeatureCard } from '../components/FeatureCard'
import { ReportPreview } from '../components/ReportPreview'
import '../landing.css'

const FEATURES = [
  {
    icon: '💰',
    title: 'Faturamento e variação',
    description: 'Total do período e comparação com o período anterior, sem precisar montar filtro nenhum.',
  },
  {
    icon: '📊',
    title: 'Margem por produto',
    description: 'Lucro por produto e margem agregada do período, a partir do custo que você cadastra.',
  },
  {
    icon: '🎯',
    title: 'Ticket médio',
    description: 'Valor médio por pedido e sua variação, pra saber se você está vendendo mais caro ou mais barato.',
  },
  {
    icon: '📦',
    title: 'Unidades vendidas',
    description: 'Quantidade total vendida no período e sua variação, volume de verdade, não só o valor em reais.',
  },
  {
    icon: '📈',
    title: 'Ranking de produtos e categorias',
    description: 'Quais categorias e produtos subiram ou caíram, ordenados pelo que mais mudou.',
  },
  {
    icon: '🆕',
    title: 'Clientes novos vs. recorrentes',
    description: 'Quantos clientes são novos nesse período e quantos já compravam antes, com o faturamento de cada grupo.',
  },
  {
    icon: '⚠️',
    title: 'Alerta de margem negativa',
    description: 'Produto vendendo no prejuízo é avisado primeiro, antes que vire hábito.',
  },
  {
    icon: '👋',
    title: 'Clientes que sumiram',
    description: 'Quem parou de comprar comparado ao padrão histórico dele, não uma regra genérica de dias.',
  },
]

const PLATFORMS = ['Mercado Livre', 'Shopify', 'Nuvemshop']

const STEPS = [
  {
    title: 'Autorize o acesso à sua conta',
    description: 'Mercado Livre, Shopify ou Nuvemshop — nada de planilha, nada de upload manual. Só a conta oficial da sua loja.',
  },
  {
    title: 'A gente calcula em tempo real',
    description: 'Cada venda chega sozinha assim que acontece. O motor valida os dados, calcula as métricas e prioriza os 2-3 insights mais relevantes.',
  },
  {
    title: 'Você recebe no WhatsApp',
    description: 'Resumo automático direto na sua conversa, sem precisar abrir nada. Quer se aprofundar? O relatório completo fica sempre disponível no site.',
  },
]

export function Landing() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <Logo />
        <Link to="/login" className="nav-cta">
          Entrar
        </Link>
      </header>

      <div className="platform-strip">
        <span className="platform-strip-label">Conecta direto com:</span>
        {PLATFORMS.map((platform) => (
          <span className="platform-badge" key={platform}>
            {platform}
          </span>
        ))}
      </div>

      <section className="hero">
        <div className="hero-glow hero-glow-a" aria-hidden="true" />
        <div className="hero-glow hero-glow-b" aria-hidden="true" />
        <div className="hero-content">
          <span className="eyebrow">🔥 O diferencial: você não abre nada, a gente te chama</span>
          <h1>Seu faturamento te manda mensagem antes de você ir atrás dele</h1>
          <p className="hero-subhead">
            Enquanto ferramentas tradicionais te dão só um painel pra consultar, a Zapture manda o que importa direto
            no seu WhatsApp, sozinha, sem você precisar entrar em lugar nenhum. Conectando direto com a sua conta
            oficial (Mercado Livre, Shopify ou Nuvemshop), o dado chega em tempo real — nada de planilha
            desatualizada. E se quiser se aprofundar, o relatório completo também fica disponível pra consulta no
            site.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="btn-primary">
              Criar conta grátis
            </Link>
            <a href="#como-funciona" className="btn-ghost">
              Ver como funciona
            </a>
          </div>
        </div>
        <div className="hero-visual">
          <WhatsAppMockup />
        </div>
      </section>

      <section className="section" id="canais">
        <div className="channels-grid">
          <div className="channel-card channel-card-primary">
            <span className="channel-tag">O diferencial</span>
            <span className="channel-icon">📲</span>
            <h3>Resumo automático no WhatsApp</h3>
            <p>
              O coração da Zapture. Assim que há novidade no seu faturamento, o resumo chega sozinho na sua
              conversa, sem login, sem abrir aba, sem lembrar de consultar nada.
            </p>
          </div>
          <div className="channel-card">
            <span className="channel-tag">Também disponível</span>
            <span className="channel-icon">💻</span>
            <h3>Relatório completo no site</h3>
            <p>
              Quando quiser se aprofundar num número, o relatório dinâmico fica sempre disponível no site, com todos
              os detalhes por trás do resumo que você recebeu.
            </p>
          </div>
        </div>
      </section>

      <section className="section" id="relatorio">
        <h2 className="section-title">Um exemplo do relatório que você vai ter</h2>
        <p className="section-subtitle">O mesmo motor que gera o resumo do WhatsApp alimenta esse relatório, sempre calculado na hora.</p>
        <ReportPreview />
      </section>

      <section className="section" id="features">
        <h2 className="section-title">O que entra no seu resumo (e no relatório)</h2>
        <p className="section-subtitle">Tudo calculado na hora, direto dos dados da sua loja.</p>
        <div className="feature-grid">
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </section>

      <section className="section section-alt" id="como-funciona">
        <h2 className="section-title">Como funciona</h2>
        <div className="steps-grid">
          {STEPS.map((step, index) => (
            <div className="step-card" key={step.title}>
              <span className="step-number">{index + 1}</span>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2 className="section-title">Painel completo pra consultar não é a mesma coisa que resumo que chega sozinho</h2>
        <div className="comparison-grid">
          <div className="comparison-card">
            <h3>Ferramentas tradicionais</h3>
            <ul>
              <li>Painel passivo: você precisa entrar e procurar</li>
              <li>Preço não público ou "sob consulta"</li>
              <li>Foco em inteligência de mercado, não no seu dia a dia</li>
            </ul>
          </div>
          <div className="comparison-card comparison-card-highlight">
            <h3>Zapture</h3>
            <ul>
              <li>Entrega proativa: o resumo chega até você, no WhatsApp, sem precisar abrir nada</li>
              <li>Direto da API oficial da sua loja, em tempo real — sem planilha, sem upload</li>
              <li>Preço público e simples</li>
              <li>Quer se aprofundar? Relatório dinâmico completo também disponível no site</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="section" id="preco">
        <h2 className="section-title">Preço</h2>
        <div className="pricing-card">
          <p className="pricing-value">
            A partir de <strong>R$ 47/mês</strong>
          </p>
          <ul>
            <li>Conecte sua conta do Mercado Livre, Shopify ou Nuvemshop</li>
            <li>Dados em tempo real, direto da API oficial</li>
            <li>Resumo periódico automático via WhatsApp</li>
            <li>Relatório dinâmico sempre disponível</li>
          </ul>
          <Link to="/login" className="btn-primary">
            Criar conta grátis
          </Link>
        </div>
      </section>

      <section className="cta-band">
        <h2>Pronto pra parar de ir atrás do seu próprio faturamento?</h2>
        <Link to="/login" className="btn-inverted">
          Criar conta grátis
        </Link>
      </section>

      <footer className="landing-footer">
        <Logo size={20} />
        <span>
          © {new Date().getFullYear()} Zapture · <a href="mailto:contato@zapture.app">contato@zapture.app</a>
        </span>
      </footer>
    </div>
  )
}
